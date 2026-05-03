# Post à publier sur community.jeedom.com

**Catégorie :** Présentation Plugin  
**Titre du post :** MyIndygo (myindygojeedom)

**Tags à cocher :**
- `cron` ← le plugin utilise le moteur cron de Jeedom
- `gratuit`
- `beta`

---

## Texte du post (copiez tout ci-dessous)

---

Bonjour,

Je vous présente mon premier plugin Jeedom pour piloter les piscines connectées **Indygo Pool Command**.

---

**Nom et id**
MyIndygo — `myindygojeedom`

---

**Ce que fait le plugin**
Permet de contrôler une piscine connectée Indygo Pool Command depuis Jeedom via l'API officielle MyIndygo (OAuth2) :
- Lecture de la température de l'eau
- État de la filtration (active / inactive)
- Mode courant de chaque programme (Filtration, Éclairage, Pompe à chaleur…)
- Commandes action Off / On / Auto pour chaque équipement détecté automatiquement

---

**Langages utilisés**
PHP uniquement (plugin Jeedom standard, pas de démon externe).

---

**Démon / Dépendances / Crons**
- Démon : ❌ non
- Dépendances : ❌ aucune (PHP + cURL natifs)
- Cron : ✅ oui — `cron5` pour le rafraîchissement automatique toutes les 5 minutes

---

**Panel dédié**
❌ non

---

**Payant / Gratuit**
✅ Gratuit — licence MIT

---

**Lien GitHub**
https://github.com/benoitleq/myindygojeedom

---

Ouvert à toute remarque sur la conception, notamment si d'autres possesseurs de Pool Command veulent tester.

Merci !

---

## Checklist avant de poster

- [x] Dépôt GitHub public : https://github.com/benoitleq/myindygojeedom
- [x] Icône 128×128 px présente dans `desktop/img/`
- [x] README complet
- [ ] Tester l'installation sur votre Jeedom (Plugins > + > GitHub > benoitleq/myindygojeedom)
- [ ] Être connecté sur community.jeedom.com
- [ ] Aller dans **Présentation Plugin** > **+ Nouveau sujet**
- [ ] Titre : `MyIndygo (myindygojeedom)`
- [ ] Coller le texte ci-dessus (à partir de "Bonjour")
- [ ] Ajouter les tags : `cron`, `gratuit`, `beta`
