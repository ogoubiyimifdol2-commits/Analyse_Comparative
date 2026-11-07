import csv
import json
import re

import openpyxl

from config import ML, BB, CI
from src.journal import log


def parse_prix_texte(valeur):
    if valeur is None:
        return None
    if isinstance(valeur, (int, float)):
        return int(valeur)
    chiffres = re.sub(r"[^\d]", "", str(valeur))
    return int(chiffres) if chiffres else None


def charger_catalogue(dossier):
    with open(dossier / "catalogue_reference.csv", encoding="utf-8-sig", newline="") as f:
        return {r["produit_id"]: r for r in csv.DictReader(f)}


def charger_marche_lagune(dossier):
    articles, vus = [], set()
    with open(dossier / "marche_lagune.csv", encoding="utf-8-sig", newline="") as f:
        for n, r in enumerate(csv.DictReader(f, delimiter=";"), start=2):
            ref = r["reference"].strip()
            if ref in vus:
                log(ML, f"{ref} (ligne {n})", "doublon exact d'une ligne déjà lue", "ligne ignorée")
                continue
            vus.add(ref)
            nom_brut = r["designation"]
            if nom_brut != nom_brut.strip():
                log(ML, ref, "espaces parasites dans la désignation", "nom normalisé")
            prix = parse_prix_texte(r["prix"])
            if prix is None:
                log(ML, ref, f"prix inexploitable ({r['prix'] or 'vide'!r}) ; "
                             f"l'ancien prix n'est pas un prix de vente",
                    "article sans prix : écarté du comparatif")
            dispo = r["disponibilite"].strip()
            articles.append({
                "enseigne": ML, "ref": ref, "nom": " ".join(nom_brut.split()),
                "prix": prix,
                "ancien_prix": parse_prix_texte(r["ancien_prix"]),
                "en_stock": dispo != "Rupture",
                "note": float(r["note_clients"].replace(",", ".")) if r["note_clients"] else None,
            })
            if dispo == "Rupture":
                log(ML, ref, "en rupture de stock", "écarté du « moins cher » (conservé dans les données)")
    return articles


def charger_baobab(dossier):
    with open(dossier / "baobab_shop.json", encoding="utf-8") as f:
        data = json.load(f)
    articles = []
    for it in data["items"]:
        ref = it["sku"]
        p = it["pricing"]
        if p.get("currency") != "XOF":
            log(BB, ref, f"devise {p.get('currency')}", "écarté")
            continue
        amount = p.get("amount")
        if amount is None:
            log(BB, f"{ref} ({it['title']})", "prix (amount) = null", "article sans prix : écarté du comparatif")
        prix = None if amount is None else amount + (p.get("delivery_fee") or 0)
        if it.get("seller") != "Baobab Shop":
            log(BB, ref, f"vendu par un partenaire ({it['seller']})",
                "conservé, prix retenu tel quel (information seulement)")
        if it["stock"] == 0:
            log(BB, ref, "stock = 0", "écarté du « moins cher » (conservé dans les données)")
        articles.append({
            "enseigne": BB, "ref": ref, "nom": it["title"], "prix": prix,
            "ancien_prix": None, "en_stock": it["stock"] > 0,
            "note": it["rating"]["average"] if it.get("rating") else None,
        })
    return articles


def charger_comptoir(dossier):
    wb = openpyxl.load_workbook(dossier / "comptoir_ivoire.xlsx", data_only=True)
    ws = wb.active
    articles = []
    for ligne in ws.iter_rows(min_row=4, values_only=True):
        code, article, rayon, prix_cat, remise, qte, maj = ligne[:7]
        if not code:
            continue
        brut = prix_cat
        prix_cat = parse_prix_texte(prix_cat)
        if isinstance(brut, str):
            log(CI, code, f"prix stocké comme texte ({brut!r}, espace insécable)", "converti en entier")
        remise = remise or 0
        prix = None if prix_cat is None else round(prix_cat * (1 - remise / 100))
        if remise:
            log(CI, code, f"remise de {remise} % sur le prix catalogue", f"prix payé = {prix} FCFA")
        if not qte:
            log(CI, code, "quantité en rayon = 0", "écarté du « moins cher » (conservé dans les données)")
        articles.append({
            "enseigne": CI, "ref": code, "nom": article, "prix": prix,
            "ancien_prix": prix_cat, "en_stock": bool(qte), "note": None,
        })
    return articles


def charger_historique(dossier):
    with open(dossier / "historique_prix.csv", encoding="utf-8", newline="") as f:
        return [(r["date"], r["source"], r["produit_id"], int(r["prix_fcfa"])) for r in csv.DictReader(f)]
