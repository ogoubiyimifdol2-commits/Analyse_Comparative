import heapq

from config import ENSEIGNES, PANIER


def analyser(index, catalogue):
    rapport = []
    for pid, prix in index.items():
        if len(prix) < 2:
            continue
        meilleure = min(prix, key=prix.get)
        bas, haut = min(prix.values()), max(prix.values())
        rapport.append({
            "produit_id": pid, "produit": catalogue[pid]["nom"],
            "categorie": catalogue[pid]["categorie"],
            **{e: prix.get(e) for e in ENSEIGNES},
            "meilleure": meilleure, "prix_min": bas,
            "ecart_fcfa": haut - bas, "ecart_pct": round((haut - bas) / bas * 100, 1),
        })
    return sorted(rapport, key=lambda r: r["ecart_pct"], reverse=True)


def synthese(rapport):
    victoires = {e: 0 for e in ENSEIGNES}
    ecarts = {e: [] for e in ENSEIGNES}
    for r in rapport:
        victoires[r["meilleure"]] += 1
        for e in ENSEIGNES:
            if r[e] is not None:
                ecarts[e].append((r[e] - r["prix_min"]) / r["prix_min"] * 100)
    moyennes = {e: (sum(v) / len(v) if v else None) for e, v in ecarts.items()}
    top3_pct = heapq.nlargest(3, rapport, key=lambda r: r["ecart_pct"])
    top3_fcfa = heapq.nlargest(3, rapport, key=lambda r: r["ecart_fcfa"])
    return victoires, moyennes, top3_pct, top3_fcfa


def panier(index):
    totaux = {}
    for e in ENSEIGNES:
        total, manquants = 0, []
        for pid, q in PANIER.items():
            if e in index.get(pid, {}):
                total += q * index[pid][e]
            else:
                manquants.append(pid)
        totaux[e] = (total, manquants)
    optimal, detail = 0, {}
    for pid, q in PANIER.items():
        e = min(index[pid], key=index[pid].get)
        detail[pid] = (e, index[pid][e], q)
        optimal += q * index[pid][e]
    return totaux, optimal, detail
