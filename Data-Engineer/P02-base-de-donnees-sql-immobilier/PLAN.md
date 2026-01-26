# PLAN — P02 « Entraînez-vous avec SQL et créez votre BDD »

Plan figé avant de produire les réponses SQL. Les écarts constatés ensuite sont consignés dans le README.

## Question métier

Laplace Immo (réseau national d'agences) lance un POC, la base **DATAImmo**, sur les transactions immobilières du
**1er semestre 2020** (fichier DVF). Objectif : une base relationnelle propre et conforme au RGPD, capable de
répondre aux **12 besoins** du compte-rendu de réunion (volumes de ventes, prix au m², classements régionaux et
communaux).

## Ce que disent les données (exploration du 2026-01-26)

| Fichier | Lignes | Constat |
|---|---|---|
| `Valeurs-foncières.xlsx` (DVF) | 34 169 × 46 | 1 ligne = 1 vente d'1 bien ; 17 colonnes entièrement vides ; 2 types de biens ; 6 mois de janv. à juin 2020 ; **nom de l'acquéreur** présent (RGPD) |
| `donnees_communes.xlsx` (INSEE) | 34 991 × 9 | population par commune (municipale `PMUN`, totale `PTOT`) |
| `fr-esr-referentiel-geographique.xlsx` | 38 916 × 37 | commune → département → région (19 régions), 3 variantes redondantes du nom |

Pièges identifiés :
- **Codes** : départements `2A`/`2B` et DOM sur 3 chiffres ⇒ texte ; codes postaux sans zéro initial (`1170`) ⇒
  à recomposer sur 5 caractères.
- **Clé commune** = code département + code commune (3 chiffres) : 3 125 communes dans DVF, 100 % retrouvées dans les
  deux autres fichiers. Le code postal ne convient pas : 05100 = Briançon, Montgenèvre, Névache.
- **Le code postal n'est pas un attribut de la commune** : 57 communes en ont plusieurs (Nice : 4). Il va dans `bien`
  (adresse), contrairement à l'ébauche de schéma fournie.
- **Encodage** : des noms abîmés (« SchÅ“lcher ») à réparer (texte UTF-8 relu en Windows-1252).
- **Prix au m²** : `Valeur fonciere` porte sur toute la vente, `Surface Carrez du 1er lot` sur le 1er lot seulement.
  Les ventes multi-lots (34 %) ne biaisent que peu (médiane +4 % : le 2ᵉ lot est souvent une cave ou un parking).
  Les valeurs extrêmes viennent des **petites surfaces et des erreurs de saisie** : max 989 011 €/m² (9 M€ pour
  9,10 m², 1 seul lot) ; surfaces Carrez de 4 936 m² pour 52 m² bâtis ; 497 ventes avec un ratio Carrez/bâti hors
  de [0,5 ; 2]. 18 valeurs foncières manquantes ; 100 surfaces Carrez < 9 m². Toutes les maisons ont une surface
  Carrez, bien que la loi Carrez ne s'applique pas aux maisons individuelles (jeu préparé par OC).
- **Noms** : le référentiel écrit « Ile-de-France » sans accent ; 15 noms de communes DVF sont des homonymes
  (plusieurs clés) ; 17 des 19 régions ont des ventes.

## Protocole (décisions)

| Décision | Choix | Justification |
|---|---|---|
| Moteur | **SQLite** (fichier unique, pas de serveur) ; DDL compatible PostgreSQL autant que possible | recommandé par le CR et l'énoncé ; PostgreSQL en « aller plus loin » |
| Schéma | 4 tables : `region` ← `commune` ← `bien` ← `vente` | 3NF, aligné sur le schéma attendu, avec un écart justifié (code postal) |
| `region` | PK `id_region` = code région INSEE ; `nom_region`, `nom_regroupement` | 19 lignes depuis le référentiel |
| `commune` | PK `id_codedep_codecommune` (texte, 5-6 car.) ; FK `id_region` ; `code_departement` (texte) ; `code_commune` (texte 3) ; `nom_commune` ; `population` | 3 125 lignes (communes présentes dans DVF), comme le POC l'exige |
| Population | `PMUN` (population municipale) ; variante `PTOT` au besoin 12 | population de référence de l'INSEE ; `PTOT` = `PMUN` + personnes comptées à part (étudiants, etc.), qui seraient doublement comptées en sommant plusieurs communes. Impact mesuré : même top 20 |
| `bien` | PK `id_bien` (auto) ; FK commune ; adresse atomique (n°, BTQ, type de voie, voie, **code postal**) ; type de local ; pièces ; surface Carrez ; surface réelle bâtie | 1 bien par vente dans ce fichier |
| `vente` | PK `id_vente` (auto) ; FK `id_bien` ; `date_vente` (ISO `AAAA-MM-JJ`) ; `valeur_fonciere` (**NULL** si absente, 18 lignes) ; `nombre_lots` | 34 169 lignes : on ne supprime pas les 18 ventes sans valeur (contrôle de la grille) ; un vide importé en `''` serait lu comme 0 par `AVG` |
| RGPD | **suppression** de `Nom de l'acquereur` (anonymisation) | aucune requête n'en a besoin ; la pseudonymisation serait superflue |
| Préparation | Python (pandas) dans le corrigé ; pas de guide tableur pas à pas (décision du mentor) : les pièges du tableur (zéros, 2A/2B, dates, encodage, RECHERCHEV) sont couverts par le kit mentor et les fiches | le guide ne pouvait pas être testé |
| Prix au m² | `valeur_fonciere / surface_carrez`, ventes avec valeur renseignée | définition attendue par le corrigé type |
| Agrégation du prix au m² (besoins 4, 5, 8, 10) | **toujours** : réponse principale = moyenne des prix au m² `AVG(valeur / surface)` ; variante = **médiane** (sans filtre) ; `COUNT(*)` affiché ; groupes avec n < 30 signalés | décidé avant les résultats (pas de variante « au cas par cas ») ; la médiane neutralise les erreurs de saisie sans filtre arbitraire |
| Médiane | calculée en pandas dans le notebook ; version SQL (fonction de fenêtre) en « aller plus loin » | SQLite n'a pas de `MEDIAN` |
| Trimestres | T1 = janvier-mars, T2 = avril-juin 2020 | |
| Groupement des communes | toujours par `id_codedep_codecommune` (et le nom pour l'affichage) | 15 homonymes dans DVF |
| Filtre Île-de-France | `id_region = '11'` | le nom est écrit sans accent dans le référentiel |

### Interprétation de chaque besoin (figée avant les résultats)

| Besoin | Réponse principale | Variante affichée |
|---|---|---|
| 1. Appartements vendus au S1 | `COUNT(*)` des ventes d'appartements (valeur manquante comprise) | — |
| 2. Ventes d'appartements par région | `COUNT(*)` par région, tri décroissant ; les 2 régions sans vente sont mentionnées | — |
| 3. Proportion par nombre de pièces | dénominateur = **ventes d'appartements** ; modalité 0 pièce gardée et signalée | — |
| 4. Top 10 départements au m² | moyenne des prix au m², tous biens | médiane, n |
| 5. Prix moyen du m² d'une maison en IDF | moyenne des prix au m² des maisons, `id_region = '11'` | médiane, n |
| 6. Top 10 appartements les plus chers | tri par valeur foncière, avec région et surface Carrez | — |
| 7. Évolution T1 → T2 | toutes ventes ; (T2 − T1) / T1 | appartements seuls |
| 8. Régions, appartements de plus de 4 pièces | strictement > 4, moyenne des prix au m², n affiché | ≥ 4 ; médiane |
| 9. Communes avec au moins 50 ventes au T1 | ≥ 50, toutes ventes, par clé commune | — |
| 10. Écart 2 pièces / 3 pièces | (prix m² 3 p − prix m² 2 p) / prix m² 2 p, appartements | autre sens du calcul ; médiane |
| 11. Top 3 des communes de 5 départements | rang par moyenne de valeur foncière dans chaque département (06, 13, 33, 59, 69), n affiché | communes avec n ≥ 5 |
| 12. Transactions pour 1 000 habitants | communes de **plus de** 10 000 habitants (`PMUN > 10000`), toutes ventes | `PTOT` |

## Livrables et emplacement

| Livrable | Chemin | Preuve que c'est fini |
|---|---|---|
| Dictionnaire des données (livrable 1) | `livrables/dictionnaire_donnees.xlsx` | toutes les variables essentielles de la grille, 7 colonnes remplies |
| Schéma relationnel | `sql/schema.sql` + figure | la base se crée sans erreur, contraintes actives (`PRAGMA foreign_keys`) |
| CSV de chargement + base | `data/processed/*.csv`, `data/processed/dataimmo.sqlite` | lignes CSV = lignes en base (34 169 / 34 169 / 3 125 / 19), vérifié par test |
| Requêtes (12 besoins) | `sql/requetes/01…12.sql` + notebook corrigé | chaque requête testée, résultats affichés et commentés |
| Présentation (livrable 2) | `presentation/` (.pptx + version web) | rubriques attendues, dont **sauvegarde et RGPD** et **preuve du chargement** (requêtes COUNT) ; une diapositive par besoin avec requête, résultat et phrase métier |
| Scénario de démonstration en direct | `kit-mentor/05_trame_bilan.md` | 3 requêtes à exécuter + 1 paramètre à modifier en direct |
| Package + tests | `src/dataimmo/`, `tests/` | `uv run pytest` vert |
| Fiches, kit mentor, page interactive, aller plus loin | `pedagogie/`, `kit-mentor/`, `site/`, `ALLER_PLUS_LOIN.md` | relus par les agents |

## Vérifications

- **Code** : tests des fonctions de préparation (clés, codes postaux, encodage) sur de petits cas construits à la main.
- **Données** : SHA-256 du zip ; unicité des clés ; aucune FK orpheline ; décompte des lignes à chaque étape.
- **Validité** : chaque réponse SQL recoupée par un calcul pandas indépendant ; pour les prix au m², moyenne et
  médiane côte à côte, avec n.

## Hors périmètre

Années antérieures à 2020 (prévues après le POC) ; géolocalisation ; modèle complet DVF (tous les lots, toutes les
dispositions) ; aucune conclusion causale sur les prix.
