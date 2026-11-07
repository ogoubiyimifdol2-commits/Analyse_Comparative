from collections import defaultdict

from src.journal import log
from src.normalisation import rapprocher


def rapprocher_articles(articles, index_cat):
    deja = defaultdict(list)
    for a in articles:
        a["pid"] = rapprocher(a["nom"], index_cat)
        if a["pid"] is None:
            log(a["enseigne"], a["ref"], f"aucun produit du catalogue ne correspond à {a['nom']!r}",
                "article ignoré")
        else:
            deja[(a["enseigne"], a["pid"])].append(a["ref"])
    for (e, pid), refs in deja.items():
        if len(refs) > 1:
            log(e, ", ".join(refs), f"plusieurs articles rapprochés du même produit {pid}",
                "à vérifier à la main")


def verifier_prix_avec_historique(articles, hist_dernier):
    for a in articles:
        if a["prix"] is None or a["pid"] is None:
            continue
        ref_hist = hist_dernier.get((a["enseigne"], a["pid"]))
        if not ref_hist:
            continue
        rapport = a["prix"] / ref_hist
        if rapport > 3 or rapport < 1 / 3:
            candidat = a["prix"] / 10 if rapport > 3 else a["prix"] * 10
            if abs(candidat / ref_hist - 1) < 0.10:
                log(a["enseigne"], a["ref"],
                    f"prix aberrant : {a['prix']} FCFA alors que l'historique donne ~{ref_hist} FCFA (facteur 10)",
                    f"corrigé en {int(candidat)} FCFA (faute de frappe probable, confirmée par l'historique)")
                a["prix"] = int(candidat)
            else:
                log(a["enseigne"], a["ref"],
                    f"prix aberrant : {a['prix']} FCFA vs ~{ref_hist} FCFA en historique",
                    "écarté du comparatif")
                a["prix"] = None


def construire_index(articles):
    index = defaultdict(dict)
    for a in articles:
        if a["pid"] and a["prix"] is not None and a["en_stock"]:
            index[a["pid"]][a["enseigne"]] = a["prix"]
    return index
