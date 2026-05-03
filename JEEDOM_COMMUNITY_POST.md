# Post à publier sur community.jeedom.com

**Catégorie :** Présentation Plugin  
**Tags :** piscine, indygo, pool-command, lora, plugin-gratuit  
**Titre du post :**

> [Plugin gratuit] MyIndygo — Pilotez votre piscine Indygo Pool Command dans Jeedom

---

## Texte du post (copiez tout ci-dessous)

---

Bonjour à tous,

Je partage un plugin Jeedom open-source gratuit pour piloter votre piscine connectée **Indygo Pool Command** directement depuis Jeedom.

---

### 🏊 Plugin MyIndygo pour Jeedom

**GitHub :** https://github.com/benoitleq/myindygojeedom  
**Licence :** MIT — gratuit, pour toujours

---

### Ce que ça fait

- 🌡️ **Température de l'eau** — commande info numérique, historisée
- 💧 **Filtration active** — commande info binaire, historisée
- 🎛️ **Mode courant** de chaque programme (Filtration, Éclairage, PAC…) — Off / On / Auto
- ▶️ **Commandes action** Off / On / Auto pour chaque programme détecté
- 🔍 **Auto-détection** des équipements au premier lancement
- 🔄 **Rafraîchissement automatique** toutes les 5 min (cron Jeedom natif)
- 📡 API **OAuth2 officielle** myindygo.com — pas de scraping, robuste aux mises à jour
- 🔒 Identifiants stockés **localement** dans Jeedom — aucun tiers impliqué

---

### Installation

**Plugins > Gestion des plugins > + > GitHub**

| Champ | Valeur |
|---|---|
| Utilisateur | `benoitleq` |
| Dépôt | `myindygojeedom` |
| Branche | `main` |

Puis :

1. Installer et activer le plugin
2. **Plugins > Confort > MyIndygo** → **Ajouter une piscine**
3. Saisir l'**email**, le **mot de passe** et le **Pool ID**
4. Sauvegarder → les commandes sont créées automatiquement

> 💡 **Trouver le Pool ID** : connectez-vous sur [myindygo.com](https://myindygo.com), l'URL contient `pools/<POOL_ID>`.

---

### Commandes créées automatiquement

| Commande | Type | Détail |
|---|---|---|
| Température eau | info numérique | °C, historisée |
| Filtration active | info binaire | 1/0, historisée |
| `<Programme>` — mode | info texte | Off / On / Auto |
| `<Programme>` → Off | action | Forcer l'arrêt |
| `<Programme>` → On | action | Forcer la marche |
| `<Programme>` → Auto | action | Repasser en programmation |

Les programmes (filtration + auxiliaires) sont détectés automatiquement.

---

### Compatibilité

Testé avec **Pool Command** (module LoRaWAN V2, type `lr-pc`).  
Compatible aussi avec les modules **IPX**.  
La latence de **10 à 30 secondes** entre la commande et le retour visuel est normale (propagation LoRa).

---

### En bonus : interface web standalone

Si vous souhaitez piloter votre piscine sans Jeedom (Raspberry Pi, NAS…), une interface **Python/Streamlit** est aussi disponible :

**https://github.com/benoitleq/myindygo-jeedom**

---

### Crédits

- API reverse-engineerée par [FunFR](https://github.com/FunFR) via [ha-indygo-pool](https://github.com/FunFR/ha-indygo-pool) (Apache 2.0)
- Inspiré du travail de B_Leq sur le forum HACF

---

Vos retours sont les bienvenus ici ou en ouvrant une issue sur GitHub.  
Si vous avez un Pool Command et que vous testez, dites-moi comment ça se passe !

Bonne baignade ! 🌊

---

## Checklist avant de poster

- [x] Dépôt GitHub public créé : https://github.com/benoitleq/myindygojeedom
- [ ] Ajouter l'icône `myindygojeedom_icon.png` (128×128 px) dans `desktop/img/` et pousser sur GitHub
- [ ] Tester l'installation sur votre Jeedom (logs : Analyse > Logs > myindygojeedom)
- [ ] Être connecté sur community.jeedom.com
- [ ] Aller dans : **Présentation Plugin** > **+ Nouveau sujet**
- [ ] Coller le texte ci-dessus (à partir de "Bonjour à tous")
- [ ] Ajouter les tags : `piscine`, `indygo`, `pool-command`, `lora`, `plugin-gratuit`
