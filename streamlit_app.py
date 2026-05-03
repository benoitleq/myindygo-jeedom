"""
streamlit_app.py — Interface MyIndygo
=======================================

Application Streamlit pour piloter votre piscine connectée Indygo :
    * Affichage en temps réel de la température de l'eau
    * Pilotage de la filtration (Off / On / Auto)
    * Pilotage des équipements auxiliaires (éclairage, etc.)

Lancement :
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import time
from datetime import datetime

import streamlit as st

from config import EMAIL, PASSWORD, POOL_ID

# PROGRAM_NAMES est optionnel dans config.py
try:
    from config import PROGRAM_NAMES
except ImportError:
    PROGRAM_NAMES = {}

from indygo_client import (
    IndygoAuthError,
    IndygoClient,
    IndygoCommunicationError,
    IndygoError,
    MODE_AUTO,
    MODE_NAMES,
    MODE_OFF,
    MODE_ON,
)


# ─────────────────────────────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ma piscine — Indygo",
    page_icon="🏊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# CSS custom — palette aquatique sobre
st.markdown(
    """
    <style>
    /* Reset bordures par défaut */
    .block-container { padding-top: 2rem; max-width: 720px; }

    /* Titre principal */
    h1 { font-weight: 700; letter-spacing: -0.02em; color: #0F172A; }

    /* Cartes "metric" custom */
    .metric-card {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 16px;
        border: 1px solid #BFDBFE;
    }
    .metric-card .metric-label {
        font-size: 0.85rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .metric-card .metric-value {
        font-size: 3rem;
        font-weight: 700;
        color: #0C4A6E;
        line-height: 1;
    }
    .metric-card .metric-unit {
        font-size: 1.5rem;
        color: #0EA5E9;
        margin-left: 4px;
    }
    .metric-card .metric-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 8px;
    }

    /* Section programmes */
    .program-row {
        background: #F8FAFC;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #E2E8F0;
    }

    /* Pastilles de mode */
    .mode-badge {
        display: inline-block;
        padding: 2px 12px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .mode-on   { background: #DCFCE7; color: #166534; }
    .mode-off  { background: #FEE2E2; color: #991B1B; }
    .mode-auto { background: #DBEAFE; color: #1E40AF; }
    .mode-unknown { background: #F1F5F9; color: #64748B; }

    /* Boutons Streamlit */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────
# Initialisation de la session (client + cache)
# ─────────────────────────────────────────────────────────────────────
def get_client() -> IndygoClient | None:
    """Récupère ou crée le client Indygo dans st.session_state."""
    if "client" not in st.session_state:
        try:
            client = IndygoClient(
                EMAIL, PASSWORD, POOL_ID,
                program_name_overrides=PROGRAM_NAMES,
            )
            client.login()
            st.session_state.client = client
            st.session_state.connected = True
            st.session_state.last_error = None
        except IndygoAuthError as e:
            st.session_state.connected = False
            st.session_state.last_error = f"Authentification refusée : {e}"
            return None
        except IndygoCommunicationError as e:
            st.session_state.connected = False
            st.session_state.last_error = f"Erreur réseau : {e}"
            return None
    return st.session_state.client


def refresh_data() -> dict | None:
    """Rafraîchit toutes les données et les met en cache dans session_state."""
    client = get_client()
    if not client:
        return None
    try:
        data = client.refresh()
        st.session_state.data = data
        st.session_state.last_refresh = datetime.now()
        st.session_state.last_error = None
        return data
    except IndygoError as e:
        st.session_state.last_error = f"Erreur API : {e}"
        return st.session_state.get("data")  # on garde l'ancien cache


def mode_badge_html(mode: int | None) -> str:
    """Renvoie une pastille HTML colorée pour un mode."""
    if mode == MODE_ON:
        return '<span class="mode-badge mode-on">● On</span>'
    if mode == MODE_OFF:
        return '<span class="mode-badge mode-off">○ Off</span>'
    if mode == MODE_AUTO:
        return '<span class="mode-badge mode-auto">⟲ Auto</span>'
    return '<span class="mode-badge mode-unknown">⋯ Indéterminé</span>'


# ─────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────
st.title("🏊 Ma piscine")

# ─── Sidebar : connexion + actions globales ──────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Connexion")
    client = get_client()
    if client and st.session_state.get("connected"):
        st.success("✅ Connecté à myindygo.com")
        st.caption(f"Email : `{EMAIL}`")
        st.caption(f"Pool ID : `{POOL_ID[:8]}…`")
    else:
        st.error("❌ Non connecté")
        st.caption(st.session_state.get("last_error", ""))
        if st.button("🔄 Réessayer la connexion"):
            st.session_state.pop("client", None)
            st.rerun()

    st.markdown("---")
    st.markdown("### 🔁 Auto-refresh")
    auto_refresh = st.checkbox("Activer", value=False)
    refresh_interval = st.slider("Intervalle (sec)", 30, 300, 60, step=30,
                                  disabled=not auto_refresh)

    st.markdown("---")
    st.caption("Inspiré de [FunFR/ha-indygo-pool](https://github.com/FunFR/ha-indygo-pool)")


# ─── Si non connecté, on s'arrête là ─────────────────────────────────
if not client or not st.session_state.get("connected"):
    st.warning("Impossible de se connecter à l'API. Vérifiez `config.py` et la connexion réseau.")
    st.stop()

# ─── Premier chargement ──────────────────────────────────────────────
if "data" not in st.session_state:
    with st.spinner("Récupération des données…"):
        refresh_data()

data = st.session_state.get("data")

# Bouton refresh + horodatage
col_a, col_b = st.columns([3, 1])
with col_a:
    last_refresh = st.session_state.get("last_refresh")
    if last_refresh:
        st.caption(f"📡 Dernière mise à jour : {last_refresh.strftime('%H:%M:%S')}")
with col_b:
    if st.button("🔄 Rafraîchir", use_container_width=True):
        with st.spinner("Mise à jour…"):
            refresh_data()
        st.rerun()

if not data:
    st.error("Aucune donnée disponible.")
    st.stop()

# Garde-fou supplémentaire (au cas où st.stop ne stoppe pas en mode bare)
if data is None:
    st.stop()
    raise SystemExit  # noqa: F821 (pour aider les linters)

# ─── Affichage principal : température ───────────────────────────────
temp = data.get("water_temperature_c")
last_meas = data.get("last_measurement_time", "")
temp_str = f"{temp:.1f}" if temp is not None else "—"

st.markdown(
    f"""
    <div class="metric-card">
        <div class="metric-label">🌡️ Température de l'eau</div>
        <div class="metric-value">{temp_str}<span class="metric-unit">°C</span></div>
        <div class="metric-sub">Dernier relevé : {last_meas or 'inconnu'}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Filtration en cours ?
filt_running = data.get("is_filtration_running")
if filt_running is not None:
    icon = "🟢" if filt_running else "⚪"
    state = "**en marche**" if filt_running else "**arrêtée**"
    st.markdown(f"{icon} Filtration actuellement {state}")

st.markdown("---")

# ─── Section : Programmes (filtration + auxiliaires) ─────────────────
st.markdown("### 🎛️ Pilotage")

programs = data.get("programs", [])
if not programs:
    st.info("Aucun programme détecté sur ce module.")
else:
    # On trie pour afficher la filtration en premier
    programs_sorted = sorted(programs, key=lambda p: (not p["is_filtration"], p["program_name"]))

    for prog in programs_sorted:
        prog_id = prog["program_id"]
        widget_key = f"prog_{prog['module_id']}_{prog_id}"

        # En-tête du programme
        icon = "💧" if prog["is_filtration"] else "💡"
        with st.container():
            st.markdown(
                f"""
                <div class="program-row">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:1.05rem; font-weight:600;">{icon} {prog['program_name']}</span>
                        <span>État actuel : {mode_badge_html(prog['current_mode'])}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Sélecteur de mode (radio horizontal)
            mode_options = ["Off", "On", "Auto"]
            current_mode_name = prog["current_mode_name"]
            try:
                default_idx = mode_options.index(current_mode_name)
            except ValueError:
                default_idx = 2  # Auto par défaut si mode inconnu/indéterminé

            cols = st.columns([3, 1])
            with cols[0]:
                selected = st.radio(
                    f"Mode pour {prog['program_name']}",
                    mode_options,
                    index=default_idx,
                    horizontal=True,
                    key=widget_key,
                    label_visibility="collapsed",
                )
            with cols[1]:
                # Bouton désactivé seulement si mode connu ET identique
                mode_known = current_mode_name in mode_options
                same_as_current = mode_known and (selected == current_mode_name)
                btn_label = "✓ Appliqué" if same_as_current else "Appliquer"
                if st.button(btn_label, key=f"btn_{widget_key}",
                             disabled=same_as_current,
                             use_container_width=True):
                    new_mode_int = {"Off": MODE_OFF, "On": MODE_ON, "Auto": MODE_AUTO}[selected]
                    try:
                        with st.spinner(f"Envoi de la commande « {selected} »…"):
                            client.set_program_mode(
                                module_id=prog["module_id"],
                                program_id=prog_id,
                                mode=new_mode_int,
                            )
                            # Le device prend ~10 s pour répondre via LoRa
                            time.sleep(2)
                            refresh_data()
                        st.success(
                            f"✅ Commande envoyée : {prog['program_name']} → {selected}. "
                            f"Le changement peut prendre jusqu'à 10–30 s pour se propager via LoRa."
                        )
                        time.sleep(1.5)
                        st.rerun()
                    except IndygoError as e:
                        st.error(f"❌ Échec : {e}")

# ─── Section debug ───────────────────────────────────────────────────
st.markdown("---")
with st.expander("🔍 Données brutes (debug)"):
    st.json({
        "water_temperature_c": data.get("water_temperature_c"),
        "is_filtration_running": data.get("is_filtration_running"),
        "last_measurement_time": data.get("last_measurement_time"),
        "programs_count": len(programs),
        "programs": [
            {k: v for k, v in p.items() if k != "raw"} for p in programs
        ],
    })

    st.markdown("**Statut JSON brut (top-level)**")
    raw = data.get("status_raw", {})
    st.json({k: (f"<{type(v).__name__}, len={len(v)}>" if isinstance(v, (list, dict))
                  else v) for k, v in raw.items()})

# ─── Auto-refresh ────────────────────────────────────────────────────
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
