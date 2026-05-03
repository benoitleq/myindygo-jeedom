# MyIndygo Jeedom — Interface Streamlit

Application web locale pour piloter votre piscine connectée Indygo (Pool Command).
Affichage en temps réel de la température et contrôle de la filtration et des
équipements auxiliaires (éclairage, etc.).

![architecture](https://img.shields.io/badge/Python-3.10+-blue.svg)
![streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![licence](https://img.shields.io/badge/Licence-MIT-green.svg)

> Discussion & support : [Communauté Jeedom](https://community.jeedom.com) — rubrique *Présentation Plugin*

## ✨ Fonctionnalités

- 🌡️ **Température de l'eau** affichée en grand, avec dernière mesure
- 💧 **Filtration** : Off / On / Auto avec retour visuel de l'état courant
- 💡 **Équipements auxiliaires** détectés automatiquement (éclairage, PAC…)
- 🔄 **Rafraîchissement** manuel ou automatique (configurable)
- 📡 **API officielle OAuth2** (pas de scraping HTML, robuste aux changements UI)
- 🔍 **Mode debug** intégré (JSON brut visible en bas de page)

## 📦 Installation

### 1. Cloner / extraire les fichiers

Vous devez avoir au minimum ces fichiers dans le même dossier :
```
indygo_v4/
├── streamlit_app.py        ← l'application
├── indygo_client.py        ← le client API (réutilisable)
├── config.example.py       ← template de configuration
└── requirements.txt        ← dépendances Python
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

(ou plus moderne avec [uv](https://docs.astral.sh/uv/) : `uv pip install -r requirements.txt`)

### 3. Configurer vos identifiants

```bash
cp config.example.py config.py
```

Puis éditez `config.py` :
```python
EMAIL = "votre.email@example.com"
PASSWORD = "votre_mot_de_passe"
POOL_ID = "votre_pool_id"  # cf. URL après login

# Optionnel : renommer les équipements
PROGRAM_NAMES = {
    2: "Lumières",         # Auxiliaire 2 = éclairage chez vous
    # 1: "Pompe à chaleur",
    # 3: "Robot",
}
```

> 💡 **Trouver le bon programType** : lancez l'app une fois, dépliez la
> section « 🔍 Données brutes » en bas de page, et regardez les valeurs de
> `program_type` pour chaque équipement. Vous saurez ainsi quel auxiliaire
> correspond à quel numéro chez vous.

### 4. Lancer

```bash
streamlit run streamlit_app.py
```

L'application s'ouvre automatiquement dans votre navigateur sur
[http://localhost:8501](http://localhost:8501).

## 🎯 Utilisation

### Connexion automatique
Au premier lancement, l'app se connecte automatiquement avec les identifiants
de `config.py` et récupère l'état de votre piscine. Le token OAuth2 est valide
1 heure et renouvelé automatiquement.

### Pilotage des équipements
Pour chaque programme détecté (filtration, éclairage…), trois modes sont
disponibles :

| Mode | Effet |
|---|---|
| **Off** | Équipement forcé à l'arrêt |
| **On** | Équipement forcé en marche |
| **Auto** | Suit la programmation (horaires + thermo-régulation) |

> ⚠️ **Latence LoRa** : la commande passe par le cloud → la passerelle LRMB →
> l'antenne LoRa → votre Pool Command. Le retour visuel peut prendre **10 à 30
> secondes**. Patientez avant de cliquer plusieurs fois.

### Rafraîchissement automatique
Activez l'auto-refresh dans la barre latérale (intervalle 30–300 s) pour
suivre l'évolution en temps réel.

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│  streamlit_app.py                                │
│  └─ UI Streamlit (cache via st.session_state)    │
│        │                                         │
│        ▼                                         │
│  indygo_client.py                                │
│  └─ IndygoClient (synchrone, OAuth2, requests)   │
│        │                                         │
│        ▼                                         │
│  https://myindygo.com                            │
│  ├─ POST /oauth2/token                           │
│  ├─ POST /api/getUserWithHisModules              │
│  ├─ POST /api/getModuleWithHisPrograms           │
│  ├─ GET  /v1/module/{addr}/status/{dev}          │
│  ├─ PUT  /api/updatePrograms     ← écrit         │
│  ├─ POST /api/module/{addr}/programs/{dev}       │
│  └─ POST /modules/sendDataViaLoRaWAN             │
└──────────────────────────────────────────────────┘
```

## ⚙️ Détails techniques importants

### Lecture de la température
Le parser teste deux sources, dans cet ordre :
1. `sensorState[index=0].value / 100` (mesure live, **prioritaire**)
2. `temperature` à la racine (fallback, peut être obsolète)

### Modification d'un programme
Pour ne **pas** corrompre la configuration du Pool Command, le client envoie
toujours **tous** les programmes du module ensemble (logique copiée de FunFR) :
- Le programme cible reçoit le nouveau mode
- Les autres programmes (de type différent) ont leur `mode` mis à `null` pour
  signaler qu'on ne veut pas les modifier
- Pour les modules LoRaWAN V2, une synchro radio est déclenchée en bonus

### Sécurité
- Vos identifiants restent **en local** dans `config.py`
- Aucun envoi vers d'autres serveurs que `myindygo.com`
- Le token OAuth2 est gardé en mémoire uniquement pendant la session

## 🐛 Dépannage

### « Identifiants refusés (HTTP 401) »
Vérifiez `EMAIL` et `PASSWORD` dans `config.py`. Si vous venez de changer le
mot de passe, redémarrez Streamlit.

### « Impossible de déterminer les IDs hardware »
Votre installation n'a ni Pool Command (`lr-pc`) ni IPX dans la liste des
modules. L'app supporte ces deux configurations. Pour d'autres setups,
ouvrez une issue.

### Le mode change dans l'UI mais pas sur le device
- C'est normal pendant 10–30 s (latence LoRa)
- Si après 1 min rien ne bouge : vérifiez que la passerelle LRMB est en ligne
  (LED verte) et que le Pool Command communique bien avec
- Tentez un cycle alimentation (off / on) du Pool Command en dernier recours

### Le bouton « Appliquer » ne fait rien
Il est désactivé quand le mode sélectionné est déjà le mode courant. C'est
normal pour éviter les commandes inutiles.

## 📚 Crédits

- **API officielle reverse-engineerée** par [FunFR](https://github.com/FunFR)
  via le projet [ha-indygo-pool](https://github.com/FunFR/ha-indygo-pool)
  (Apache 2.0, intégration Home Assistant)
- **Premier proof-of-concept** scraping par
  [B_Leq](https://forum.hacf.fr/u/B_Leq) sur le forum HACF

## ⚠️ Disclaimer

Ce projet n'est pas affilié à Indygo / Solem. Utilisez-le à vos propres
risques. Ne pas utiliser sur des installations professionnelles ou critiques.
