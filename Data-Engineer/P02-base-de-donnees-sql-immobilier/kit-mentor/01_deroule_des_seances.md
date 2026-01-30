# Déroulé des séances

Principe : l'apprenant partage son écran et **montre** (son tableur, son schéma, SQLite Studio) ; le mentor
questionne. On ne corrige jamais une requête à sa place : on lui fait décomposer la question à voix haute.

## Parcours temps plein : 1 séance + bilan

### Séance 1 (fin de la modélisation, avant le chargement)

| Minutes | Contenu | Support |
|---|---|---|
| 0-5 | Météo : avancement, temps passé, blocages | — |
| 5-15 | « Une ligne du fichier DVF, c'est quoi ? » ; les 3 fichiers et leur rôle | [questions §1](02_questions_oral.md#1-comprendre-les-données) |
| 15-35 | Le dictionnaire : pourquoi garder ou supprimer chaque variable ; types des codes | [questions §2](02_questions_oral.md#2-modéliser) |
| 35-50 | Le schéma : clés primaires et étrangères, 3NF, code postal | fiches 2 et 3 |
| 50-60 | Préparer le chargement : ordre des colonnes, clés uniques, contrôle des lignes | fiche 5 |

### Bilan : voir [05_trame_bilan.md](05_trame_bilan.md)

## Parcours alternance : 3 séances + bilan

| Séance | Moment | Objectif | Focus |
|---|---|---|---|
| 1 | début | comprendre et modéliser | les 3 fichiers ; dictionnaire ; RGPD ; types des codes (2A, zéros) ; fiches 1 à 4 |
| 2 | après la création de la base | charger et prouver | CSV propres (clés uniques, ordre des colonnes, UTF-8) ; `COUNT(*)` des deux côtés ; `PRAGMA foreign_keys` ; fiche 5 |
| 3 | requêtes en cours | interroger | faire décomposer 2 ou 3 besoins à voix haute ; WHERE / HAVING ; jointures ; CTE ; fiches 6 à 9 |
| Bilan | après dépôt | valider | démonstration en direct, [05_trame_bilan.md](05_trame_bilan.md) |

## Bonnes pratiques de séance

- **Décortiquer avant d'écrire** : l'erreur la plus fréquente est d'aller trop vite sur la question. Faire dire
  à l'apprenant, avant tout code : *quoi* compter ou moyenner, *sur quelles lignes* (filtres), *par quoi*
  (regroupement), *dans quel ordre*.
- **Prédire avant d'exécuter** : « combien de lignes attends-tu ? ». Une jointure qui perd des lignes ne produit
  aucune erreur ; seule la prédiction la révèle.
- **Le tableur est le lieu des erreurs** : zéros perdus, 2A transformé, dates en jj/mm/aaaa, CSV non UTF-8.
  Demander à voir le fichier CSV ouvert dans un éditeur de texte, pas seulement dans le tableur.
- **Commenter en analyste** : chaque résultat doit finir par une phrase métier (« ce que je dirais au directeur »),
  pas par une description du code. Fiche transverse : [présenter un résultat](../../transverse/presenter_un_resultat.md).
- **Apprenants à l'aise** : PostgreSQL (Docker) au lieu de SQLite, modèle DVF complet (tous les lots), fonctions
  de fenêtre, médiane en SQL ([ALLER_PLUS_LOIN.md](../ALLER_PLUS_LOIN.md)).
