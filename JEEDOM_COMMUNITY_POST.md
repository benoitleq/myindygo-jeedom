# Post à publier sur community.jeedom.com

**Catégorie recommandée :** Présentation Plugin  
**Tags suggérés :** piscine, indygo, pool-command, python, streamlit  
**Titre du post :**

> [Outil gratuit] MyIndygo — Pilotez votre piscine Indygo Pool Command depuis un navigateur

---

## Texte du post (copiez tout ci-dessous)

---

Bonjour à tous,

Je partage un petit outil open-source que j'ai développé pour piloter ma piscine connectée **Indygo Pool Command** depuis un navigateur, en attendant un vrai plugin Jeedom.

---

### 🏊 MyIndygo — Interface web locale pour Indygo Pool Command

**GitHub :** https://github.com/benoitleq/myindygo-jeedom

---

#### Ce que ça fait

- 🌡️ **Température de l'eau** affichée en temps réel
- 💧 **Filtration** : Off / On / Auto avec retour visuel de l'état courant
- 💡 **Équipements auxiliaires** détectés automatiquement (éclairage, PAC, robot…)
- 🔄 Auto-rafraîchissement configurable (30 s à 5 min)
- 📡 Utilise l'**API officielle OAuth2** de myindygo.com (pas de scraping, robuste)
- 🔒 Vos identifiants restent **en local** — aucun tiers impliqué

---

#### Installation en 4 commandes

```bash
git clone https://github.com/benoitleq/myindygo-jeedom.git
cd myindygo
pip install -r requirements.txt
cp config.example.py config.py   # puis éditez config.py avec vos identifiants
streamlit run streamlit_app.py
```

L'interface s'ouvre sur http://localhost:8501.

---

#### Configuration minimale (`config.py`)

```python
EMAIL    = "votre.email@exemple.com"
PASSWORD = "votre_mot_de_passe"
POOL_ID  = "..."   # visible dans l'URL après login sur myindygo.com
```

---

#### Compatibilité

Testé avec un **Pool Command** (module LoRaWAN V2). Devrait fonctionner avec tout équipement géré par myindygo.com. Retour de 10–30 s normal (latence LoRa).

---

#### Pourquoi pas un vrai plugin Jeedom ?

C'est l'étape suivante si la communauté est intéressée ! En attendant, cet outil tourne en parallèle de Jeedom sur n'importe quelle machine (Raspberry Pi, NAS, PC).

---

#### Crédits

- API reverse-engineerée par [FunFR](https://github.com/FunFR) via [ha-indygo-pool](https://github.com/FunFR/ha-indygo-pool) (Apache 2.0)
- Inspiré du travail de B_Leq sur le forum HACF

---

N'hésitez pas à ouvrir une issue sur GitHub ou à répondre ici si vous avez un Pool Command et que vous voulez tester. Vos retours m'aideront à améliorer le projet et éventuellement en faire un plugin Jeedom complet.

Bonne baignade ! 🌊

---

## Checklist avant de poster

- [ ] Remplacer `benoitleq` par votre vrai pseudo GitHub dans les deux URLs
- [ ] Avoir créé le dépôt GitHub public (voir instructions dans le README)
- [ ] Être connecté sur community.jeedom.com
- [ ] Aller dans : **Présentation Plugin** > bouton **+ Nouveau sujet**
- [ ] Coller le texte ci-dessus (sans la partie "Texte du post")
- [ ] Ajouter les tags : `piscine`, `indygo`, `pool-command`, `python`
