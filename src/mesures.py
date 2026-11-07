import heapq
import time

from src.historique import bf_naif, bf_indexe


def chrono(fn, *args, repetitions=1):
    t0 = time.perf_counter()
    for _ in range(repetitions):
        res = fn(*args)
    return res, (time.perf_counter() - t0) / repetitions


def mesures(lignes, par_cle):
    paires = sorted(par_cle)
    r_naif, t_naif = chrono(bf_naif, lignes, paires)
    r_idx, t_idx = chrono(bf_indexe, lignes, repetitions=20)
    identiques = all(abs(r_naif[k] - r_idx[k]) < 1e-9 for k in r_idx)

    liste = [f"{s}|{pid}|{d}" for d, s, pid, _ in lignes]
    ensemble = set(liste)
    cible = liste[-1]
    _, t_liste = chrono(lambda: cible in liste, repetitions=200)
    _, t_set = chrono(lambda: cible in ensemble, repetitions=200000)

    prix = [p for *_, p in lignes]
    _, t_sorted = chrono(lambda: sorted(prix, reverse=True)[:3], repetitions=50)
    _, t_heap = chrono(lambda: heapq.nlargest(3, prix), repetitions=50)
    return {"paires": len(paires), "n": len(lignes), "naif": t_naif, "index": t_idx,
            "identiques": identiques, "liste": t_liste, "set": t_set,
            "sorted": t_sorted, "heap": t_heap}
