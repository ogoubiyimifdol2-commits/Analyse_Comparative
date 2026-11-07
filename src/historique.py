from collections import defaultdict
from datetime import date, timedelta

from config import ENSEIGNES, BF_DEBUT, BF_FIN


def historique_index(lignes):
    par_cle = defaultdict(list)
    for d, s, pid, p in lignes:
        par_cle[(s, pid)].append((d, p))
    return par_cle


def black_friday(par_cle):
    ratios = {e: [] for e in ENSEIGNES}
    for (s, pid), serie in par_cle.items():
        bf = [p for d, p in serie if BF_DEBUT <= d <= BF_FIN]
        if not bf:
            continue
        annuel = sum(p for _, p in serie) / len(serie)
        ratios[s].append(sum(bf) / len(bf) / annuel - 1)
    return {e: (sum(v) / len(v) * 100, len(v)) for e, v in ratios.items()}


def promo_black_friday(par_cle):
    debut, fin = date.fromisoformat(BF_DEBUT), date.fromisoformat(BF_FIN)
    voisines = [((debut - timedelta(days=28)).isoformat(), (debut - timedelta(days=1)).isoformat()),
                ((fin + timedelta(days=1)).isoformat(), (fin + timedelta(days=28)).isoformat())]
    res = {e: {"voisinage": [], "meilleure": []} for e in ENSEIGNES}
    semaine_min = {e: defaultdict(int) for e in ENSEIGNES}
    for (s, pid), serie in par_cle.items():
        bf = [p for d, p in serie if BF_DEBUT <= d <= BF_FIN]
        autour = [p for d, p in serie if any(lo <= d <= hi for lo, hi in voisines)]
        if not bf or not autour:
            continue
        moy_bf = sum(bf) / len(bf)
        res[s]["voisinage"].append(moy_bf / (sum(autour) / len(autour)) - 1)
        par_sem = defaultdict(list)
        for d, p in serie:
            iso = date.fromisoformat(d).isocalendar()
            par_sem[(iso[0], iso[1])].append(p)
        sem, vals = min(par_sem.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
        semaine_min[s][sem] += 1
        res[s]["meilleure"].append(moy_bf / (sum(vals) / len(vals)) - 1)
    sortie = {}
    for e in ENSEIGNES:
        sortie[e] = {k: sum(v) / len(v) * 100 for k, v in res[e].items()}
        sortie[e]["semaine_frequente"] = max(semaine_min[e].items(), key=lambda kv: kv[1])[0]
    return sortie


def bf_naif(lignes, paires):
    out = {}
    for s, pid in paires:
        vals = [p for d, s2, p2, p in lignes if s2 == s and p2 == pid and BF_DEBUT <= d <= BF_FIN]
        out[(s, pid)] = sum(vals) / len(vals) if vals else None
    return out


def bf_indexe(lignes):
    somme, nb = defaultdict(int), defaultdict(int)
    for d, s, pid, p in lignes:
        if BF_DEBUT <= d <= BF_FIN:
            somme[(s, pid)] += p
            nb[(s, pid)] += 1
    return {k: somme[k] / nb[k] for k in somme}
