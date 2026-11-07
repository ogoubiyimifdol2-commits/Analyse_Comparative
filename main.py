import time

from config import DOSSIER_DONNEES, DOSSIER_SORTIE, ENSEIGNES
from src.chargement import (charger_catalogue, charger_marche_lagune, charger_baobab,
                            charger_comptoir, charger_historique)
from src.comparaison import analyser, synthese, panier
from src.export import exporter_csv, exporter_journal, construire_rapport
from src.historique import historique_index, black_friday, promo_black_friday
from src.journal import journal
from src.mesures import mesures
from src.nettoyage import rapprocher_articles, verifier_prix_avec_historique, construire_index
from src.normalisation import construire_index_catalogue


def main():
    t_debut = time.perf_counter()
    DOSSIER_SORTIE.mkdir(exist_ok=True)

    catalogue = charger_catalogue(DOSSIER_DONNEES)
    articles = (charger_marche_lagune(DOSSIER_DONNEES) + charger_baobab(DOSSIER_DONNEES)
                + charger_comptoir(DOSSIER_DONNEES))
    lignes = charger_historique(DOSSIER_DONNEES)

    rapprocher_articles(articles, construire_index_catalogue(catalogue))

    par_cle = historique_index(lignes)
    hist_dernier = {k: serie[-1][1] for k, serie in par_cle.items()}
    verifier_prix_avec_historique(articles, hist_dernier)
    index = construire_index(articles)

    rapport = analyser(index, catalogue)
    victoires, moyennes, top_pct, top_fcfa = synthese(rapport)
    totaux, optimal, detail = panier(index)

    bf = black_friday(par_cle)
    promo = promo_black_friday(par_cle)
    mes = mesures(lignes, par_cle)

    exporter_csv(rapport, DOSSIER_SORTIE / "comparatif.csv")
    exporter_journal(journal, DOSSIER_SORTIE / "journal_nettoyage.csv")
    texte = construire_rapport({
        "rapport": rapport, "catalogue": catalogue, "nb_catalogue": len(catalogue),
        "nb_journal": len(journal),
        "couverture": {e: sum(1 for a in articles if a["enseigne"] == e and a["pid"]) for e in ENSEIGNES},
        "victoires": victoires, "moyennes": moyennes, "top_pct": top_pct, "top_fcfa": top_fcfa,
        "totaux": totaux, "optimal": optimal, "detail": detail,
        "bf": bf, "promo": promo, "mesures": mes,
        "temps_total": time.perf_counter() - t_debut,
    })
    (DOSSIER_SORTIE / "rapport.txt").write_text(texte, encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main()
