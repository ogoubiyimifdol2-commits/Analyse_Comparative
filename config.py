from pathlib import Path

RACINE = Path(__file__).parent
DOSSIER_DONNEES = RACINE / "donnees"
DOSSIER_SORTIE = RACINE / "resultats"

ML, BB, CI = "Marché Lagune", "Baobab Shop", "Comptoir Ivoire"
ENSEIGNES = [ML, BB, CI]

PANIER = {"P04": 1, "P12": 1, "P14": 2, "P15": 1, "P28": 1}

BF_DEBUT, BF_FIN = "2025-11-24", "2025-11-30"
