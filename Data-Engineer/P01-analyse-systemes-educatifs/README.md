# P01 — Analysez les données de systèmes éducatifs

**Parcours Data Engineer · OpenClassrooms · premier projet technique**

academy, start-up EdTech (cours en ligne du lycée à l'université), veut s'étendre à l'international. Mark, le
manager, demande si les données éducatives de la Banque mondiale (EdStats) peuvent éclairer la décision, et quels
pays présentent le plus fort potentiel.

## Par où commencer ?

| Vous êtes… | Ouvrez |
|---|---|
| **Mentor**, avant une séance | [kit-mentor/](kit-mentor/) : déroulé, questions d'oral, erreurs fréquentes, grille, trame de bilan |
| **Apprenant**, en début de projet | la page interactive [site/index.html](site/index.html) (étapes, labos, quiz, check-list) |
| **Apprenant**, bloqué sur une notion | [pedagogie/](pedagogie/) : une notion par notebook, sur les vraies données |
| Curieux des pratiques actuelles | [ALLER_PLUS_LOIN.md](ALLER_PLUS_LOIN.md) |
| À la recherche de la référence | [notebooks/projet_edstats_corrige.ipynb](notebooks/projet_edstats_corrige.ipynb) et [presentation/](presentation/) |

> Le corrigé sert au mentor à **comparer** ; on ne le transmet pas à l'apprenant avant son bilan.

## Résultats du corrigé

| Étape | Résultat |
|---|---|
| Exploration | 5 fichiers, 0 doublon ; Data = un (pays, indicateur), avec les années en colonnes ; 86 % de cellules vides |
| Faux pays | 25 agrégats retirés ; Gibraltar et Nauru gardés (sans région, mais vrais territoires) ; 1 pays d'écart entre liste noire et jointure (VGB) |
| Périmètre | 3 665 indicateurs → 751 (métier) → 314 (≥ 60 % renseignés sur 2010-2014) → 15 → **5 non redondants** |
| Agrégation | médiane 2010-2014, avec au moins 3 années renseignées → 216 pays × 15 indicateurs |
| Score | 3 critères en rangs : marché connecté 50 %, maturité numérique 30 %, dynamique 2015-2030 20 % ; 161 pays notés |
| Robustesse | autour des poids métier : 8 pays dans le top 10 au moins 89 % du temps ; en tirage uniforme des poids : seuls **Royaume-Uni** (74 %) et **France** (59 %) au-delà de 50 % |
| Recommandation | **Royaume-Uni et France** d'abord ; ensuite deux stratégies : marchés matures (États-Unis, Russie, Allemagne, Japon) ou connectés en croissance (Maroc, Arabie saoudite, Mexique…) |

Constat principal : maturité numérique et croissance de la cible sont **anti-corrélées** (ρ = −0,66). Le choix des
pays au-delà des deux premiers est donc une décision stratégique, pas statistique.

## Lancer le projet

```bash
uv sync --frozen                     # environnement exact (Python 3.12, versions de uv.lock)
uv run pytest                        # 25 tests du package edstats
uv run jupyter lab                   # le premier chargement télécharge et vérifie les données (~39 Mo)
```

Réexécuter tous les notebooks :

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb pedagogie/*.ipynb
```

Régénérer la présentation : voir [presentation/README.md](presentation/README.md).

## Organisation

```text
├── PLAN.md                 protocole figé avant les résultats
├── src/edstats/            io (téléchargement + SHA-256), quality, cleaning, analysis, viz
├── tests/                  tests sur petits jeux construits à la main
├── notebooks/              corrigé (livrable 1)
├── pedagogie/              01 maille et qualité · 02 filtrer et agréger · 03 corrélations · 04 distributions · 05 score pays
├── kit-mentor/             séances, questions, erreurs, grille, bilan
├── presentation/           livrable 2 (.pptx + script de génération + figures)
├── site/                   page interactive pour les apprenants
├── data/processed/         sorties du corrigé (pays × indicateurs, classement, journal de nettoyage)
└── data/raw/               données brutes (non versionnées, téléchargées automatiquement)
```

## Ce qui a changé par rapport au plan

| Plan | Réalité | Pourquoi |
|---|---|---|
| Années 2010-2015 | **2010-2014** | 2015 n'est renseignée qu'à 33 % (contre 43 à 55 % pour les autres années) |
| Familles listées dans le plan | + « Health: Population: Structure / Dynamics » | la structure par âge et la croissance démographique y sont classées |
| Score à 4 critères (+ pouvoir d'achat, + scolarisation supérieure) | **3 critères** | PIB/hab et scolarisation supérieure sont redondants avec le taux d'internet (ρ = 0,91 et 0,79) : les garder aurait compté trois fois le niveau de développement |
| Poids 40 / 30 / 20 / 10 | **50 / 30 / 20** | conséquence du point précédent |
| Robustesse testée par un tirage de poids | **Deux lois de tirage** | relecture du statisticien : la fréquence dépend de la loi. Autour des poids métier, 8 pays sont stables ; en tirage uniforme, 2 seulement. C'est le choix de stratégie qui est fragile, pas les poids |
| — | Internet compté dans 2 critères sur 3 | choix assumé (pas de client en ligne sans internet) ; variante « taille sans internet » montrée : 8 pays sur 10 communs |
| Comparaison moyenne / médiane prévue | Non faite dans le notebook | la médiane est justifiée par l'exemple de la fiche 2 (une année aberrante) |
| `make notebooks` | `nbconvert` | pas de Makefile : la commande est donnée ci-dessus |
| — | Bug corrigé dans `redundant_pairs` | plantait sur une matrice issue d'un `pivot_table` (index et colonnes portant le même nom) ; reproduit par un test avant correction |

## Limites connues

- Données arrêtées en 2014 (export OpenClassrooms de 2018) : les ordres de grandeur d'internet ont changé depuis.
- Les fichiers du corrigé ne suivent pas le nommage `Nom_Prenom_n°_livrable_mmaaaa` demandé aux apprenants : c'est
  un corrigé de référence, pas un dépôt.
- Contrôle visuel du `.pptx` non fait avec LibreOffice (absent de la machine de production) : fichier validé par
  schéma, contenu relu, figures vérifiées individuellement. La version web du deck a été contrôlée.
