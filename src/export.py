import csv
from datetime import date

from config import ENSEIGNES, BF_DEBUT, BF_FIN


def fmt(n):
    return f"{int(round(n)):,}".replace(",", " ")


def exporter_csv(rapport, chemin):
    champs = ["produit_id", "produit", "categorie"] + ENSEIGNES + ["meilleure", "prix_min", "ecart_fcfa", "ecart_pct"]
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=champs, delimiter=";")
        w.writeheader()
        for r in rapport:
            w.writerow({c: ("" if r[c] is None else r[c]) for c in champs})


def exporter_journal(journal, chemin):
    with open(chemin, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["source", "reference", "probleme", "traitement"])
        w.writerows(journal)


def construire_rapport(c):
    L = []
    L.append("=" * 72)
    L.append("ANALYSE COMPARATIVE - Marché Lagune / Baobab Shop / Comptoir Ivoire")
    L.append(f"Programme exécuté le {date.today():%d/%m/%Y}. Prix en FCFA, prix réellement payé par le client.")
    L.append("=" * 72)
    L.append("\nArticles rapprochés du catalogue : " + ", ".join(f"{e} {c['couverture'][e]}" for e in ENSEIGNES))
    L.append(f"Entrées du journal de nettoyage : {c['nb_journal']} (voir journal_nettoyage.csv)")
    L.append(f"Produits comparables (>= 2 enseignes, en stock, avec prix) : {len(c['rapport'])} sur {c['nb_catalogue']}")

    L.append("\n--- 4. COMPARATIF (trié par écart décroissant) ---")
    L.append(f"{'Produit':42}{'Moins chère':>16}{'Prix min':>10}{'Écart':>10}{'%':>7}")
    for r in c["rapport"]:
        L.append(f"{r['produit'][:41]:42}{r['meilleure']:>16}{fmt(r['prix_min']):>10}"
                 f"{fmt(r['ecart_fcfa']):>10}{r['ecart_pct']:>6.1f}%")

    L.append("\n--- 5. SYNTHÈSE ---")
    L.append("Nombre de fois la moins chère :")
    for e in ENSEIGNES:
        L.append(f"  {e:16} {c['victoires'][e]:3d}  sur {len(c['rapport'])}")
    L.append("Écart moyen par rapport au prix le plus bas (sur les produits qu'elle vend) :")
    for e in ENSEIGNES:
        L.append(f"  {e:16} {c['moyennes'][e]:5.1f} %")
    L.append("Les 3 produits où il y a le plus à gagner à comparer :")
    L.append("  en % :    " + " ; ".join(f"{r['produit']} ({r['ecart_pct']} %)" for r in c["top_pct"]))
    L.append("  en FCFA : " + " ; ".join(f"{r['produit']} ({fmt(r['ecart_fcfa'])})" for r in c["top_fcfa"]))

    L.append("\n--- 6. PANIER DE RENTRÉE ---")
    for e in ENSEIGNES:
        total, manq = c["totaux"][e]
        L.append(f"  {e:16} {fmt(total):>10} FCFA"
                 + (f"   (INCOMPLET : {', '.join(manq)} indisponible)" if manq else ""))
    L.append(f"  Chaque article au meilleur prix : {fmt(c['optimal'])} FCFA")
    for pid, (e, p, q) in c["detail"].items():
        L.append(f"    {q} x {c['catalogue'][pid]['nom']:40} {e:16} {fmt(p)}")
    complets = {e: t for e, (t, mq) in c["totaux"].items() if not mq}
    if complets:
        meilleure = min(complets, key=complets.get)
        L.append(f"  Meilleure enseigne unique : {meilleure} ({fmt(complets[meilleure])}) ; "
                 f"gain en répartissant les achats : {fmt(complets[meilleure] - c['optimal'])} FCFA")

    L.append(f"\n--- 7. HISTORIQUE : semaine du Black Friday ({BF_DEBUT} au {BF_FIN}) vs moyenne de l'année ---")
    for e in ENSEIGNES:
        v, n = c["bf"][e]
        L.append(f"  {e:16} {v:+6.1f} %  (moyenne sur {n} produits)")
    L.append("Effet de la promo (BF vs 4 semaines avant/après) et semaine la moins chère de l'année :")
    for e in ENSEIGNES:
        pr = c["promo"][e]
        an, sem = pr["semaine_frequente"]
        L.append(f"  {e:16} BF vs voisinage {pr['voisinage']:+6.1f} %   "
                 f"BF vs semaine la moins chère {pr['meilleure']:+6.1f} %   (semaine la plus fréquente : S{sem:02d}/{an})")

    m = c["mesures"]
    L.append("\n--- 8. COMPLEXITÉ (mesures réelles) ---")
    L.append(f"Historique : {fmt(m['n'])} lignes, {m['paires']} couples (enseigne, produit)")
    L.append(f"  Moyenne Black Friday, boucles imbriquées : {m['naif']*1000:8.1f} ms   O(paires x n)")
    L.append(f"  Même calcul avec un dict (une passe)      : {m['index']*1000:8.2f} ms   O(n)")
    L.append(f"  Résultats identiques : {m['identiques']}   -> accélération x{m['naif']/m['index']:.0f}")
    L.append(f"  'x in list' : {m['liste']*1e6:8.1f} µs     'x in set' : {m['set']*1e6:8.3f} µs")
    L.append(f"  Top 3 avec sorted()[:3] : {m['sorted']*1000:6.2f} ms     heapq.nlargest(3) : {m['heap']*1000:6.2f} ms")
    L.append(f"Temps total d'exécution du programme : {c['temps_total']:.2f} s")
    return "\n".join(L)
