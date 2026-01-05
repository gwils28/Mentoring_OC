# PLAN — P01 « Analysez les données de systèmes éducatifs »

Plan figé **avant** de produire les résultats (méthode : explorer → planifier → coder → vérifier → committer).
Les écarts constatés pendant la réalisation sont consignés dans le README, section « Ce qui a changé par rapport au plan ».

## Question métier

academy (EdTech, lycée + université, 100 % en ligne) veut s'étendre à l'international.
1. Les données EdStats de la Banque mondiale permettent-elles d'éclairer cette décision ?
2. Si oui : quels pays présentent le plus fort potentiel de clients, et comment ce potentiel évolue-t-il ?

## Protocole d'analyse (fixé avant de voir les résultats)

| Décision | Choix | Justification |
|---|---|---|
| Faux pays | `Region` vide **et** code alpha-2 d'agrégat (chiffre, ou X*/Z*, EU, OE) | Un simple « Region vide » supprimerait Gibraltar et Nauru, qui sont de vrais territoires |
| Familles d'indicateurs (`Topic`) | Population, Secondaire, Tertiaire, Communications (internet), Économie (PIB, RNB, PPA), Chômage, Dépenses d'éducation, Attainment (projections) | Les 4 familles du besoin : démographie, éducation, internet, économie |
| Années observées | 2010-2015 | 2016 et 2017 sont presque vides ; avant 2010, les données sont moins actuelles |
| Projections | Traitées à part (2015 → 2030, Wittgenstein) | Ne jamais moyenner des observations avec des projections |
| Seuil de complétude | Indicateur conservé si ≥ 60 % des couples (pays, année) sont renseignés sur 2010-2015 | Compromis entre richesse et nombre d'indicateurs |
| Agrégation des années | Médiane 2010-2015, et au moins 3 années renseignées | Robuste aux valeurs extrêmes ; jamais de « moyenne » sur 1 ou 2 points |
| Redondance | \|ρ de Spearman\| ≥ 0,7 → garder le plus pertinent pour le métier | Seuil accepté par la grille ; Spearman car les distributions sont asymétriques |
| Score pays | Moyenne pondérée de rangs percentiles : jeunes connectés 40 %, pouvoir d'achat 30 %, scolarisation dans le supérieur 20 %, croissance projetée des 15-24 ans 10 % | Les rangs neutralisent les échelles et les valeurs extrêmes |
| Robustesse | 1 000 tirages de poids aléatoires (Dirichlet) ; fréquence d'apparition dans le top 10 | Une recommandation qui dépend des poids n'est pas une recommandation |

## Livrables et emplacement

| Livrable | Chemin | Preuve que c'est fini |
|---|---|---|
| Corrigé — notebook (livrable 1) | `notebooks/projet_edstats_corrige.ipynb` | Exécuté de bout en bout par `make notebooks`, sans erreur |
| Corrigé — présentation (livrable 2) | `presentation/` (.pptx + version web) | Rendu vérifié visuellement |
| Corrigé — environnement (livrable 3) | `pyproject.toml` + `uv.lock` | `uv sync --frozen` puis exécution OK |
| Code réutilisable | `src/edstats/` + `tests/` | `uv run pytest` vert |
| Notebooks pédagogiques | `pedagogie/` (une notion par notebook) | Exécutés, sorties versionnées |
| Kit mentor | `kit-mentor/` | Relu avec la grille d'évaluation |
| Page interactive | `site/index.html` → artifact | Vérifiée dans Chrome (clair et sombre, largeur mobile) |
| Aller plus loin | `ALLER_PLUS_LOIN.md` | — |

## Vérifications

- **Code** : tests unitaires sur de petits jeux de données construits à la main (détection des agrégats, taux de remplissage, score).
- **Données** : SHA-256 du zip brut vérifié au chargement ; contrôles de clé unique (pays, indicateur) ; journal du nombre de lignes avant et après chaque filtre.
- **Validité** : sensibilité aux poids, comparaison moyenne et médiane, nombre de pays restants à chaque étape.

## Hors périmètre

Pas de modélisation prédictive ; aucune affirmation causale (« l'internet *cause* l'inscription ») ; aucune donnée externe à EdStats dans le corrigé (des pistes figurent dans « aller plus loin »).
