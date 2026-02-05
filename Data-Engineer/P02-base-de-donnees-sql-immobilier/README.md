# P02 — Entraînez-vous avec SQL et créez votre BDD

**Parcours Data Engineer · OpenClassrooms · première base de données relationnelle**

Laplace Immo, réseau national d'agences immobilières, lance un POC : la base **DATAImmo**, qui rassemble les ventes
de logements du 1er semestre 2020 (fichier DVF), les communes et les régions. La base doit être propre, conforme au
RGPD et répondre en SQL aux 12 besoins d'analyse exprimés en réunion.

## Par où commencer ?

| Vous êtes… | Ouvrez |
|---|---|
| **Mentor**, avant une séance | [kit-mentor/](kit-mentor/) : déroulé, questions d'oral, erreurs fréquentes, grille, trame de bilan avec démonstration en direct |
| **Apprenant**, en début de projet | la page interactive [site/index.html](site/index.html) (étapes, labos, quiz, check-list) |
| **Apprenant**, bloqué sur une notion | [pedagogie/](pedagogie/) : une notion par notebook, avec du SQL copiable dans SQLite Studio |
| **Apprenant**, avant de présenter | la fiche transverse [présenter un résultat](../transverse/presenter_un_resultat.md) |
| Curieux des pratiques actuelles | [ALLER_PLUS_LOIN.md](ALLER_PLUS_LOIN.md) |
| À la recherche de la référence | [notebooks/dataimmo_corrige.ipynb](notebooks/dataimmo_corrige.ipynb), [livrables/](livrables/), [sql/](sql/), [schéma relationnel](presentation/figures/schema_relationnel.png) et [presentation/](presentation/) |

> Le corrigé sert au mentor à **comparer** ; on ne le transmet pas à l'apprenant avant son bilan.

## Résultats du corrigé

| Étape | Résultat |
|---|---|
| Données | 3 fichiers : DVF (34 169 ventes × 46 colonnes, dont 17 vides), population INSEE, référentiel géographique |
| Pièges | codes en texte (`2A`, `2B`, zéros initiaux) ; le code postal décrit l'adresse, pas la commune (Nice en a 4) ; 24 noms de communes à réencoder ; nom de l'acquéreur à supprimer (RGPD) |
| Modèle | 4 tables en 3NF : `region` ← `commune` ← `bien` ← `vente` ; clé commune = code département + code commune |
| Chargement | vente 34 169 · bien 34 169 · commune 3 125 · région 19 : aucune ligne perdue, Corse comprise ; 18 valeurs foncières absentes gardées en `NULL` |
| Volumes | 31 378 appartements vendus ; Île-de-France 45 % des ventes d'appartements ; 2 et 3 pièces 60 % |
| Prix au m² | Paris 12 053 €/m² en moyenne ; maison en Île-de-France 3 745 € ; 3 pièces 12,4 % moins cher au m² qu'un 2 pièces, ≈ 5 % à géographie égale |
| Anomalies signalées | appartement à 9 M€ pour 9,10 m² ; rangs régionaux sur 1 ou 2 ventes ; 5 communes sur 15 du top 3 avec une seule vente |

Constat principal : la base répond aux 12 besoins, mais un prix moyen au m² se lit toujours avec **l'effectif, la
médiane et la géographie** : quelques erreurs de saisie ou une répartition différente des biens suffisent à
déplacer un classement. Le 1er semestre 2020 (premier confinement) est atypique : pas de tendance sans 2019.
Tous les chiffres, avec leurs variantes acceptables, sont dans le [kit mentor](kit-mentor/README.md#chiffres-de-référence-corrigé).

## Lancer le projet

```bash
uv sync --frozen                     # environnement exact (Python 3.12, versions de uv.lock)
uv run pytest                        # 83 tests du package dataimmo
uv run python -m dataimmo.build      # télécharge et vérifie les données (~15 Mo), crée les CSV et la base
uv run jupyter lab
```

Réexécuter tous les notebooks :

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb pedagogie/*.ipynb
```

La base `data/processed/dataimmo.sqlite` s'ouvre aussi dans SQLite Studio ; les 12 requêtes sont dans
[sql/requetes/](sql/requetes/). Régénérer la présentation : voir [presentation/README.md](presentation/README.md).

## Organisation

```text
├── PLAN.md                 protocole figé avant les résultats
├── src/dataimmo/           io (téléchargement + SHA-256), prepare, build, db, dictionnaire, schema_figure
├── tests/                  tests sur petits jeux construits à la main, et des 12 requêtes contre pandas
├── sql/                    schema.sql (DDL contraint) et requetes/ (une requête par besoin)
├── livrables/              dictionnaire des données (livrable 1)
├── notebooks/              corrigé
├── pedagogie/              01 du tableur à la table · 02 normaliser · 03 clés, types, intégrité · 04 dictionnaire et RGPD
│                           05 créer, charger, vérifier · 06 interroger · 07 joindre · 08 plusieurs étapes · 09 conditions et classements
├── kit-mentor/             séances, questions, erreurs, grille, bilan
├── presentation/           livrable 2 (.pptx généré depuis la base)
├── site/                   page interactive pour les apprenants
├── data/processed/         4 CSV de chargement et la base SQLite
└── data/raw/               données brutes (non versionnées, téléchargées automatiquement)
```

## Ce qui a changé par rapport au plan

| Plan | Réalité | Pourquoi |
|---|---|---|
| Contraintes : clés, `NOT NULL`, types | + `CHECK` sur les dates (refuse `2020-13-45`), sur la valeur foncière (refuse `''`), `UNIQUE` sur `vente.id_bien` | un import au tableur produit exactement ces erreurs ; la base les refuse au lieu de les fausser en silence |
| Besoin 7 : (T2 − T1) / T1 | + ventes par mois | le chiffre global (+3,68 %) masque la chute de mi-mars à avril et le rebond de mai-juin |
| Besoin 10 : écart 2 / 3 pièces, médiane, autre sens | + écart à géographie égale (≈ −5 %) et à Paris seul | relecture du statisticien : les 2 pièces sont plus souvent à Paris, l'écart brut mêle taille et localisation |
| Présentation `.pptx` + version web | **`.pptx` seul** | décision du mentor : le `.pptx` suffit |
| Énoncé : capture d'écran de la base | aperçu des tables exporté de la base | même information, régénérée avec la base au lieu d'une image qui vieillit |

## Limites connues

- Extrait préparé par OpenClassrooms : 92 % d'appartements et des surfaces Carrez pour toutes les maisons ; les
  ratios ne décrivent que l'extrait, pas le marché français.
- Surface Carrez du 1er lot seulement, valeur foncière de toute la vente : le m² est surestimé pour les ventes à
  plusieurs lots (34 % des ventes, médiane +4 %).
- Les fichiers du corrigé ne suivent pas le nommage imposé aux apprenants : c'est un corrigé de référence, pas un
  dépôt.
- Contrôle visuel du `.pptx` non fait avec LibreOffice (absent de la machine de production) : contenu relu par le
  pédagogue, positions vérifiées par le calcul, chiffres contrôlés contre la base au moment de la génération.
