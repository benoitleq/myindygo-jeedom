"""
Configuration MyIndygo — dupliquer ce fichier en `config.py` puis compléter.

    cp config.example.py config.py

⚠️  Ne JAMAIS committer `config.py` (il est dans .gitignore).
"""

# ─── Identifiants myindygo.com ────────────────────────────────────────
EMAIL = "votre.email@exemple.com"
PASSWORD = "votre_mot_de_passe"

# ID de la piscine, visible dans l'URL après connexion :
#   https://myindygo.com/pools/<POOL_ID>#dashboard
POOL_ID = "votre_pool_id"


# ─── Personnalisation des noms de programmes (optionnel) ─────────────
# Permet de renommer les équipements pour qu'ils s'affichent avec un nom
# parlant dans l'interface. Trois formats de clé sont acceptés (du plus
# spécifique au plus général) :
#
#   1. "module_id:program_id" → cible un programme précis
#   2. "type:N" (ex: "type:2") → renomme tous les programmes de programType=N
#   3. N (entier, ex: 2)       → équivalent à "type:N"
#
# Le programType correspond à la nature de l'équipement piloté :
#   * 4 = Filtration (toujours présent sur Pool Command)
#   * 1 = Auxiliaire 1 (souvent éclairage AUX1)
#   * 2 = Auxiliaire 2 (souvent éclairage AUX2 ou PAC)
#   * 3, 5, 6 = autres auxiliaires
#
# Astuce : si vous ne savez pas quel programType correspond à quoi,
# lancez l'app une fois et regardez la section debug en bas, ou cherchez
# "program_type" dans le JSON brut.
PROGRAM_NAMES = {
    # Exemple : Auxiliaire 2 = éclairage chez vous
    2: "Lumières",
    # 1: "Pompe à chaleur",
    # 3: "Robot",
}
