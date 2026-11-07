import re
import unicodedata

SYNONYMES = {
    "frigo": "refrigerateur", "fridge": "refrigerateur",
    "clim": "climatiseur", "conditioner": "climatiseur",
    "ventilo": "ventilateur", "dd": "disque dur",
    "mouse": "souris", "wireless": "sans fil",
    "printer": "imprimante", "monitor": "ecran",
    "blender": "mixeur", "kettle": "bouilloire",
    "iron": "fer repasser", "repasser": "repasser",
    "microwave": "microondes",
    "air": "", "laptop": "", "electric": "", "electrique": "", "steam": "",
    "ultra": "", "expansion": "", "portable": "", "pc": "", "ssd": "",
    "core": "", "externe": "", "sur": "", "pied": "", "crystal": "",
    "uhd": "", "4k": "", "ac1200": "", "a": "", "de": "", "la": "", "le": "",
    "du": "", "des": "", "et": "", "en": "", "pouces": "",
}


def normaliser(texte):
    t = unicodedata.normalize("NFKD", str(texte))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = t.replace("\u202f", " ").replace("\xa0", " ").replace("micro-ondes", "microondes")
    t = t.replace('"', " pouces ").replace(",", ".")
    t = re.sub(r"[()/\-]", " ", t)
    t = re.sub(r"(\d)\s*(go|gb|to|tb|l|cv|hp|pouces)\b", r"\1\2", t)
    return re.sub(r"\s+", " ", t).strip()


def jetons(texte):
    sortie = set()
    for mot in normaliser(texte).split():
        mot = re.sub(r"(\d)gb$", r"\1go", mot)
        mot = re.sub(r"(\d)tb$", r"\1to", mot)
        mot = re.sub(r"(\d)hp$", r"\1cv", mot)
        sortie.update(m for m in SYNONYMES.get(mot, mot).split() if m)
    return sortie


def construire_index_catalogue(catalogue):
    return {pid: jetons(c["nom"]) for pid, c in catalogue.items()}


def rapprocher(nom, index_cat):
    jt = jetons(nom)
    scores = []
    for pid, jc in index_cat.items():
        communs = jt & jc
        if not communs:
            continue
        precision = len(communs) / len(jt)
        rappel = len(communs) / len(jc)
        scores.append((precision * 0.5 + rappel * 0.5, pid))
    scores.sort(reverse=True)
    if not scores or scores[0][0] < 0.5:
        return None
    if len(scores) > 1 and scores[0][0] - scores[1][0] < 0.08:
        return None
    return scores[0][1]
