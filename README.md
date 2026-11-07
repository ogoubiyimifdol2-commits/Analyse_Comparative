# Analyse comparative de marché

Programme Python qui compare les prix de trois boutiques en ligne ivoiriennes (Marché Lagune, Baobab Shop, Comptoir Ivoire) pour dire, produit par produit, où acheter et quels écarts de prix existent.

Cours : Algorithmique et Python, séance 3, Institut Ivoirien de Technologie.
Auteur : (votre nom et votre classe)

## Démarche

Le programme suit les cinq étapes du cours :

1. **Collecter** : lecture de trois sources de formats différents (CSV, JSON, Excel), d'un catalogue de référence et d'un historique de prix.
2. **Normaliser** : nettoyage des noms (casse, accents, espaces, abréviations, anglais) et rapprochement de chaque article avec un produit du catalogue.
3. **Indexer** : dictionnaire produit -> enseigne -> prix payé par le client.
4. **Comparer** : prix minimum, écart en FCFA et en %, enseigne la moins chère.
5. **Décider** : synthèse, panier de rentrée, analyse du Black Friday, exports.

## Prix retenu pour chaque enseigne

| Enseigne | Prix payé par le client |
|---|---|
| Marché Lagune | Prix affiché (livraison incluse) |
| Baobab Shop | amount + delivery_fee |
| Comptoir Ivoire | Prix catalogue x (1 - remise / 100) |

Les articles en rupture, sans prix ou à stock 0 sont exclus du « moins cher ». Un produit présent dans une seule enseigne n'est pas comparé.

## Installation

Prérequis : Python 3.10 ou plus récent.

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Sous Mac, Linux ou Git Bash, l'activation est `source .venv/bin/activate` (ou `source .venv/Scripts/activate` sous Git Bash).

## Utilisation

Les cinq fichiers de données doivent se trouver dans le dossier `donnees/`. Puis :

```
python main.py
```

Le rapport s'affiche dans le terminal et trois fichiers sont écrits dans `resultats/` :

- `comparatif.csv` : tableau comparatif, trié par écart décroissant ;
- `journal_nettoyage.csv` : tous les problèmes repérés dans les données et leur traitement ;
- `rapport.txt` : rapport complet (comparatif, synthèse, panier, Black Friday, mesures de temps).

## Structure du projet

```
comparaison/
├── main.py                 point d'entrée
├── config.py               chemins, enseignes, panier, dates du Black Friday
├── requirements.txt
├── donnees/                fichiers sources
├── resultats/              fichiers produits par le programme
└── src/
    ├── journal.py          journal des problèmes de données
    ├── normalisation.py    nettoyage des noms et rapprochement
    ├── chargement.py       lecture CSV, JSON, Excel, historique
    ├── nettoyage.py        prix aberrants et index final
    ├── comparaison.py      comparatif, synthèse, panier
    ├── historique.py       Black Friday, versions naïve et indexée
    ├── mesures.py          chronométrage des structures de données
    └── export.py           écriture des CSV et du rapport
```

## Problèmes de données rencontrés

- Doublons exacts dans le CSV de Marché Lagune.
- Espaces et casse parasites dans les noms.
- Prix absents (« Prix sur demande », valeur vide, null) : article écarté.
- Prix aberrant : le Tecno Spark 20 est à 779 000 FCFA chez Marché Lagune alors que l'historique donne 77 900 ; le prix est corrigé (facteur 10 confirmé par l'historique) et la correction est journalisée.
- Prix stocké en texte avec espace insécable dans l'Excel.
- Remises à appliquer chez Comptoir Ivoire, livraison à ajouter chez Baobab Shop.
- Articles en rupture ou à stock 0.

## Résultats principaux

- 23 produits sur 30 sont comparables (au moins deux enseignes avec un prix valide et du stock).
- Enseigne la moins chère : Baobab Shop 9 fois, Comptoir Ivoire 8 fois, Marché Lagune 6 fois.
- Panier de rentrée : Comptoir Ivoire 484 075 FCFA, Baobab Shop 491 500 FCFA, Marché Lagune 504 300 FCFA. En achetant chaque article au meilleur prix : 477 575 FCFA.
- Black Friday 2025 : Marché Lagune −11,3 % et Baobab Shop −11,7 % par rapport à leur moyenne annuelle ; Comptoir Ivoire ne fait pas de promotion.

## Complexité

Le calcul de la moyenne du Black Friday est mesuré en deux versions sur 20 876 lignes :

- boucles imbriquées, O(paires x n) : environ 38 ms ;
- dictionnaire en une seule passe, O(n) : environ 1 ms.

Le programme vérifie que les deux versions donnent le même résultat. Il compare aussi `x in list` et `x in set`, ainsi que `sorted()[:3]` et `heapq.nlargest(3)`. Les temps exacts dépendent de la machine.

## Limites

- Les prix de Comptoir Ivoire datent de plusieurs jours d'octobre 2026 et ses remises sont supposées valables pour tout client.
- L'historique contient des prix affichés ; la livraison de Baobab Shop n'y est pas forcément incluse.
- Le Black Friday de 2025 est un repère pour le prochain, pas un prix disponible aujourd'hui.