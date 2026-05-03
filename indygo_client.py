"""
indygo_client.py — Client Python pour l'API MyIndygo
======================================================

Client réutilisable pour interagir avec l'API REST OAuth2 d'Indygo / Pool Command.
Utilisable depuis un script CLI ou une application Streamlit.

Inspiré de https://github.com/FunFR/ha-indygo-pool (Apache 2.0).
Réécrit en synchrone (requests) pour faciliter l'intégration Streamlit.

Fonctionnalités :
    * Authentification OAuth2 (token réutilisé pendant 1 h)
    * Récupération des données de la piscine (température, pH, sel)
    * Lecture des programmes (filtration + auxiliaires comme l'éclairage)
    * Pilotage des programmes (mode Off / On / Auto)

⚠️ Avertissement : ce code modifie la configuration de votre Pool Command.
   Le mécanisme respecte le protocole reverse-engineered par FunFR
   (envoi de tous les programmes ensemble pour ne pas corrompre la config),
   mais utilisez-le à vos risques et périls.
"""

from __future__ import annotations

import base64
import copy
import logging
import time
from typing import Any, Optional

import requests

# ─────────────────────────────────────────────────────────────────────
# Constantes API (extraites de l'APK Android par FunFR)
# ─────────────────────────────────────────────────────────────────────
BASE_URL = "https://myindygo.com"

_OAUTH2_CLIENT_ID = "5d1c5bb0b4acd1c748988085"
_OAUTH2_CLIENT_SECRET = "LUowRAajRhZb6NZYqVCFkaLC"
_OAUTH2_BASIC = base64.b64encode(
    f"{_OAUTH2_CLIENT_ID}:{_OAUTH2_CLIENT_SECRET}".encode()
).decode()

_TOKEN_EXPIRY_MARGIN = 300  # secondes
_API_ACCEPT_HEADER = "version=2.7"

# Types de programmes
PROGRAM_TYPE_FILTRATION = 4
PROGRAM_TYPE_NAMES = {
    1: "Auxiliaire 1",
    2: "Auxiliaire 2",
    3: "Auxiliaire 3",
    4: "Filtration",
    5: "Auxiliaire 5",
    6: "Auxiliaire 6",
}

# Modes
MODE_OFF = 0
MODE_ON = 1
MODE_AUTO = 2
MODE_NAMES = {MODE_OFF: "Off", MODE_ON: "On", MODE_AUTO: "Auto"}
MODE_TO_INT = {v: k for k, v in MODE_NAMES.items()}


log = logging.getLogger("indygo")


# ─────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────
class IndygoError(Exception):
    """Erreur générique de l'API Indygo."""


class IndygoAuthError(IndygoError):
    """Erreur d'authentification."""


class IndygoCommunicationError(IndygoError):
    """Erreur réseau ou réponse HTTP inattendue."""


# ─────────────────────────────────────────────────────────────────────
# Client API
# ─────────────────────────────────────────────────────────────────────
class IndygoClient:
    """Client OAuth2 synchrone pour l'API MyIndygo."""

    TIMEOUT = 15

    def __init__(self, email: str, password: str, pool_id: str,
                 program_name_overrides: Optional[dict] = None) -> None:
        self._email = email
        self._password = password
        self._pool_id = pool_id
        self._program_name_overrides = program_name_overrides or {}

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": "indygo-python/1.0"})

        # OAuth2 state
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0

        # Hardware IDs (résolus à la première récupération)
        self._pool_address: Optional[str] = None
        self._device_short_id: Optional[str] = None
        self._relay_id: Optional[str] = None

        # Cache modules + programmes
        self._modules: list[dict] = []
        self._modules_with_programs: dict[str, dict] = {}  # module_id -> module enrichi

    # ────────────────────────────────────────────────────────────────
    # Authentification
    # ────────────────────────────────────────────────────────────────
    def login(self) -> None:
        """OAuth2 Resource Owner Password Credentials grant."""
        url = f"{BASE_URL}/oauth2/token"
        try:
            r = self._session.post(
                url,
                headers={"Authorization": f"Basic {_OAUTH2_BASIC}"},
                json={
                    "grant_type": "password",
                    "username": self._email,
                    "password": self._password,
                    "scope": "*",
                },
                timeout=self.TIMEOUT,
            )
        except requests.RequestException as exc:
            raise IndygoCommunicationError(f"Erreur réseau au login : {exc}") from exc

        if r.status_code in (401, 403):
            raise IndygoAuthError(
                f"Identifiants refusés (HTTP {r.status_code}) — vérifiez email/mot de passe."
            )
        if r.status_code != 200:
            raise IndygoCommunicationError(
                f"OAuth2 → HTTP {r.status_code} : {r.text[:200]}"
            )

        data = r.json()
        if "access_token" not in data:
            raise IndygoAuthError(f"Pas d'access_token dans la réponse : {data}")

        self._token = f"{data.get('token_type', 'Bearer')} {data['access_token']}"
        self._token_expiry = time.monotonic() + data.get("expires_in", 3600)
        log.info("Auth OAuth2 OK (token valide %ss)", data.get("expires_in"))

    @property
    def is_authenticated(self) -> bool:
        return (
            self._token is not None
            and time.monotonic() < self._token_expiry - _TOKEN_EXPIRY_MARGIN
        )

    def _ensure_token(self) -> None:
        if not self.is_authenticated:
            self.login()

    # ────────────────────────────────────────────────────────────────
    # HTTP générique
    # ────────────────────────────────────────────────────────────────
    def _request(
        self,
        method: str,
        path_or_url: str,
        json_body: Optional[dict] = None,
        extra_headers: Optional[dict] = None,
    ) -> Any:
        self._ensure_token()
        url = path_or_url if path_or_url.startswith("http") else f"{BASE_URL}{path_or_url}"

        headers = {"Authorization": self._token, "Accept": _API_ACCEPT_HEADER}
        if extra_headers:
            headers.update(extra_headers)

        try:
            r = self._session.request(
                method, url, headers=headers, json=json_body, timeout=self.TIMEOUT
            )
        except requests.RequestException as exc:
            raise IndygoCommunicationError(f"Erreur réseau ({method} {url}) : {exc}") from exc

        # Re-login auto sur 401/403
        if r.status_code in (401, 403):
            log.debug("Token expiré, re-auth…")
            self.login()
            headers["Authorization"] = self._token
            r = self._session.request(
                method, url, headers=headers, json=json_body, timeout=self.TIMEOUT
            )

        if r.status_code != 200:
            raise IndygoCommunicationError(
                f"{method} {url} → HTTP {r.status_code} : {r.text[:200]}"
            )

        try:
            return r.json()
        except ValueError:
            return r.text

    # ────────────────────────────────────────────────────────────────
    # Récupération des modules + programmes
    # ────────────────────────────────────────────────────────────────
    def _fetch_modules(self) -> list[dict]:
        """POST /api/getUserWithHisModules."""
        data = self._request("POST", "/api/getUserWithHisModules", json_body={})
        modules = data.get("modules", []) if isinstance(data, dict) else []
        self._modules = modules
        return modules

    def _fetch_module_programs(self, module_id: str) -> list[dict]:
        """POST /api/getModuleWithHisPrograms."""
        data = self._request(
            "POST", "/api/getModuleWithHisPrograms",
            json_body={"module": module_id},
        )
        return data.get("programs", []) if isinstance(data, dict) else []

    def _resolve_hardware_ids(self, modules: list[dict]) -> None:
        """Détermine pool_address et device_short_id (cf. parser FunFR)."""
        if self._pool_address and self._device_short_id:
            return

        gateway = next((m for m in modules if m.get("type") == "lr-mb-10"), None)
        lr_pc = next((m for m in modules if m.get("type") == "lr-pc"), None)

        if lr_pc:
            gateway = gateway or lr_pc
            self._pool_address = gateway.get("serialNumber")
            name_parts = lr_pc.get("name", "").split("-")
            if len(name_parts) > 1:
                self._device_short_id = name_parts[-1]
            else:
                self._device_short_id = (lr_pc.get("serialNumber") or "")[-6:]
            self._relay_id = lr_pc.get("relay") or self._device_short_id
        else:
            ipx = next((m for m in modules if m.get("type") == "ipx"), None)
            if ipx:
                self._pool_address = ipx.get("serialNumber")
                self._device_short_id = ipx.get("ipxRelay")
                self._relay_id = self._device_short_id

        if not (self._pool_address and self._device_short_id):
            raise IndygoError(
                f"Impossible de déterminer les IDs hardware "
                f"(modules trouvés : {[m.get('type') for m in modules]})"
            )

    def _fetch_status(self) -> dict:
        """GET /v1/module/{pool_address}/status/{device_short_id}."""
        url = f"/v1/module/{self._pool_address}/status/{self._device_short_id}"
        return self._request(
            "GET", url, extra_headers={"x-requested-with": "XMLHttpRequest"}
        )

    # ────────────────────────────────────────────────────────────────
    # API publique haut niveau
    # ────────────────────────────────────────────────────────────────
    def refresh(self) -> dict:
        """
        Rafraîchit l'état complet de la piscine.

        Returns:
            dict avec les clés :
                - water_temperature_c : float | None
                - last_measurement_time : str | None
                - is_filtration_running : bool | None
                - programs : list[dict] (cf. format ci-dessous)
                - status_raw : dict (JSON brut pour debug)

        Format d'un programme :
            {
                "module_id": "...",
                "module_name": "...",
                "module_type": "lr-pc" | ...,
                "program_id": "...",
                "program_name": "Filtration" | "Éclairage" | ...,
                "program_type": int,
                "is_filtration": bool,
                "current_mode": int,            # 0=Off, 1=On, 2=Auto
                "current_mode_name": "Off"|"On"|"Auto",
                "raw": dict (programme complet pour replay)
            }
        """
        # 1. Modules + hardware IDs
        modules = self._fetch_modules()
        if not modules:
            raise IndygoError("Aucun module retourné par l'API.")
        self._resolve_hardware_ids(modules)

        # 2. Programmes pour chaque module
        for mod in modules:
            mod_id = mod.get("id")
            if mod_id:
                programs = self._fetch_module_programs(str(mod_id))
                if programs:
                    mod["programs"] = programs
            self._modules_with_programs[str(mod_id)] = mod

        # 3. Statut live
        status = self._fetch_status()

        # 4. Synthèse
        return {
            "water_temperature_c": self._extract_temperature(status),
            "last_measurement_time": status.get("temperatureTime"),
            "is_filtration_running": self._extract_filtration_state(status),
            "programs": self._extract_programs(modules, self._program_name_overrides),
            "status_raw": status,
            "modules_raw": modules,
        }

    @staticmethod
    def _extract_temperature(status: dict) -> Optional[float]:
        """sensorState[0]/100 prioritaire, fallback temperature racine."""
        for s in status.get("sensorState", []) or []:
            if s.get("index") == 0 and s.get("value") is not None:
                return float(s["value"]) / 100.0
        temp = status.get("temperature")
        return float(temp) if temp is not None else None

    @staticmethod
    def _extract_filtration_state(status: dict) -> Optional[bool]:
        """État live de la filtration depuis status['pool'][index=0]."""
        for item in status.get("pool", []) or []:
            if item.get("index") == 0:
                val = item.get("value")
                if val is not None:
                    try:
                        return float(val) == 1.0
                    except (TypeError, ValueError):
                        pass
        return None

    @staticmethod
    def _extract_programs(modules: list[dict],
                          name_overrides: Optional[dict] = None) -> list[dict]:
        """
        Aplatie tous les programmes de tous les modules.

        Args:
            modules: liste des modules avec leurs programmes
            name_overrides: dict optionnel pour renommer des programmes.
                Clés acceptées :
                  * int (programType) — renomme TOUS les programmes de ce type
                  * str au format "module_id:program_id" — renomme un programme précis
                  * str au format "type:N" — équivaut à int (alias texte)
                Exemple : {2: "Lumières", "type:1": "Pompe à chaleur"}
        """
        name_overrides = name_overrides or {}
        out: list[dict] = []
        for mod in modules:
            mod_id = str(mod.get("id"))
            mod_name = mod.get("name", f"Module {mod_id}")
            mod_type = mod.get("type", "unknown")
            for prog in mod.get("programs", []) or []:
                pc = prog.get("programCharacteristics")

                # Filtrage : on ignore les programmes sans programCharacteristics
                # ou avec un programType invalide (fantômes / templates non
                # configurés sur le device)
                if not isinstance(pc, dict):
                    continue
                ptype = pc.get("programType")
                if ptype is None or not isinstance(ptype, int):
                    continue

                mode = pc.get("mode")
                prog_id = prog.get("id")

                # Résolution du nom (priorité à l'override le plus spécifique)
                key_specific = f"{mod_id}:{prog_id}"
                key_type_str = f"type:{ptype}"
                resolved_name = (
                    name_overrides.get(key_specific)
                    or name_overrides.get(ptype)
                    or name_overrides.get(key_type_str)
                    or prog.get("name")
                    or PROGRAM_TYPE_NAMES.get(ptype, f"Programme {ptype}")
                )

                out.append({
                    "module_id": mod_id,
                    "module_name": mod_name,
                    "module_type": mod_type,
                    "program_id": prog_id,
                    "program_name": resolved_name,
                    "program_type": ptype,
                    "is_filtration": ptype == PROGRAM_TYPE_FILTRATION,
                    "current_mode": mode,
                    "current_mode_name": MODE_NAMES.get(mode, "Indéterminé"),
                    "raw": prog,
                })
        return out

    # ────────────────────────────────────────────────────────────────
    # Pilotage : changer le mode d'un programme
    # ────────────────────────────────────────────────────────────────
    def set_program_mode(self, module_id: str, program_id: Any, mode: int) -> None:
        """
        Change le mode (Off/On/Auto) d'un programme (filtration ou auxiliaire).

        Reproduit fidèlement la logique de FunFR :
            1. Récupère TOUS les programmes du module (cache si dispo).
            2. Met à jour le programme cible (mode = X, dataChanged = True).
            3. Met les autres programmes en mode=None pour préserver leur état
               (sauf si c'est aussi un programme du même type que le cible).
            4. PUT /api/updatePrograms
            5. POST /api/module/<addr>/programs/<dev>
            6. POST /api/reportModuleDatasSent
            7. POST /api/reportProgramsDatasSent
            8. Si LoRaWAN V2 : POST /modules/sendDataViaLoRaWAN

        Args:
            module_id: ID du module hébergeant le programme.
            program_id: ID du programme à modifier.
            mode: 0=Off, 1=On, 2=Auto.
        """
        if mode not in (MODE_OFF, MODE_ON, MODE_AUTO):
            raise ValueError(f"Mode invalide : {mode} (attendu 0, 1 ou 2)")

        # 1. Récupère les programmes (cache si possible, sinon on rappelle l'API)
        module = self._modules_with_programs.get(str(module_id))
        if not module or "programs" not in module:
            programs = self._fetch_module_programs(str(module_id))
        else:
            programs = module["programs"]

        if not programs:
            raise IndygoError(f"Aucun programme trouvé pour le module {module_id}")

        # 2. Trouver le programme cible
        target = next((p for p in programs if p.get("id") == program_id), None)
        if not target:
            raise IndygoError(
                f"Programme {program_id} introuvable dans le module {module_id}"
            )

        target_type = target.get("programCharacteristics", {}).get("programType")

        # 3. Construire la liste mise à jour
        updated_programs: list[dict] = []
        for prog in programs:
            prog_copy = copy.deepcopy(prog)
            prog_copy["dataChanged"] = True
            prog_type = prog_copy.get("programCharacteristics", {}).get("programType")

            if prog.get("id") == program_id:
                # Programme cible : on applique le nouveau mode
                if "programCharacteristics" not in prog_copy:
                    prog_copy["programCharacteristics"] = {}
                prog_copy["programCharacteristics"]["mode"] = mode
            elif prog_type != target_type:
                # Autres types : on préserve en mettant mode=None
                if (
                    "programCharacteristics" in prog_copy
                    and "mode" in prog_copy["programCharacteristics"]
                ):
                    prog_copy["programCharacteristics"]["mode"] = None
            # Programmes du même type que la cible : on garde leur mode tel quel
            updated_programs.append(prog_copy)

        log.info(
            "Envoi mode=%s pour programme %s du module %s (%d programmes au total)",
            MODE_NAMES.get(mode), program_id, module_id, len(updated_programs),
        )

        # 4. Update cloud DB
        self._request(
            "PUT", "/api/updatePrograms",
            json_body={"module": module_id, "programs": updated_programs},
        )

        # 5. Push vers le device via cloud → gateway → LoRa
        if self._pool_address and self._device_short_id:
            push_url = f"/api/module/{self._pool_address}/programs/{self._device_short_id}"
            self._request(
                "POST", push_url,
                json_body={"programs": updated_programs},
            )

        # 6. Reports (signalent au cloud que la commande a été émise)
        try:
            self._request(
                "POST", "/api/reportModuleDatasSent",
                json_body={"module": module_id},
            )
            self._request(
                "POST", "/api/reportProgramsDatasSent",
                json_body={"module": module_id, "programs": updated_programs},
            )
        except IndygoCommunicationError as e:
            log.warning("Report failed (non bloquant) : %s", e)

        # 7. Sync LoRaWAN si module V2
        if module and module.get("typeIsLoraWanV2"):
            try:
                self._request(
                    "POST", "/modules/sendDataViaLoRaWAN",
                    json_body={
                        "moduleId": module_id,
                        "sendProgram": True,
                        "sendCommand": True,
                    },
                )
            except IndygoCommunicationError as e:
                log.warning("LoRaWAN sync échouée : %s", e)

        # Met à jour notre cache local
        if module:
            module["programs"] = updated_programs
