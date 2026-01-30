# Grille d'évaluation commentée

Grille de travail du mentor, reformulée et regroupée par compétence. Cocher à la lecture des livrables.

Légende : 🟢 acquis · 🟠 à consolider (on en parle au bilan, non bloquant) · 🔴 bloquant (à corriger avant validation)

## A. Structurer les données (dictionnaire et schéma)

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | 3NF | Aucune information répétée : le nom de la région n'est que dans `region` | notebook §1.4, fiche 2 |
| ☐ | Atomicité | Adresse découpée (numéro, indice, type de voie, voie, code postal) | dictionnaire, table `bien` |
| ☐ | Données nécessaires | Toutes les variables utiles aux 12 besoins, et seulement elles | dictionnaire |
| ☐ | Clés | Une clé primaire par table, unique ; clés étrangères qui suivent le schéma ; choix justifié à l'oral | `sql/schema.sql` |
| ☐ | Dictionnaire complet | Prix, date, surface, adresse, code département, code commune, ville, nombre de pièces, code région, région, commune (clé), type de local, population | `livrables/dictionnaire_donnees.xlsx` |
| ☐ | 7 colonnes | Code, signification, type, longueur, nature, règle de gestion, règle de calcul ; les données calculées ou concaténées ont leur règle de calcul | idem |
| ☐ | RGPD | Aucune trace du nom de l'acquéreur | idem |

**Code postal** : 🟢 dans `commune` ou dans `bien` si l'apprenant sait répondre « Nice a 4 codes postaux… » ;
🟠 dans `commune` sans avoir vu le problème ; 🔴 utilisé comme clé de la commune.

## B. Créer la base

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Tables = schéma | Mêmes tables, mêmes colonnes, mêmes clés que le schéma présenté | `sql/schema.sql` |
| ☐ | Contraintes | PK, FK, NOT NULL au minimum ; FK activées | idem |
| ☐ | Types | Cohérents avec le dictionnaire ; codes en texte (sinon Corse et zéros perdus) | idem |
| ☐ | RGPD | Pas de colonne nominative en base | — |
| ☐ | Volumes | 34 169 ventes, 34 169 biens, au moins 3 125 communes, au moins 19 régions (capture ou requête) ; tout écart expliqué | notebook §2 |
| ☐ | Bonnes colonnes | Quelques lignes affichées : une date est une date, un prix est un prix | — |

## C. Interroger

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Exhaustivité | Une requête et un résultat pour chacun des 12 besoins | `sql/requetes/` |
| ☐ | Justesse | Résultats proches du corrigé, ou écart expliqué par un choix assumé (voir les variantes du [README](README.md#chiffres-de-référence-corrigé)) | notebook §3 |
| ☐ | Lisibilité | Alias explicites ; mots-clés en majuscules ; indentation | `sql/requetes/` |
| ☐ | Vocabulaire SQL | SELECT, WHERE, JOIN, GROUP BY, ORDER BY présents | idem |
| ☐ | Étapes | Au moins une sous-requête, une CTE ou une table temporaire | besoins 3, 7, 10, 11 |
| ☐ | Démonstration | Les requêtes tournent en direct au bilan | [05_trame_bilan.md](05_trame_bilan.md) |

## D. Présenter

| ✓ | Critère | Ce qu'on vérifie |
|---|---|---|
| ☐ | Contenu | Contexte, préparation des données, extrait du dictionnaire, schéma, capture de la base, requêtes et résultats |
| ☐ | Preuve | Une diapositive montre les `COUNT(*)` du chargement |
| ☐ | Lecture métier | Chaque résultat finit par une phrase compréhensible par le directeur ; les anomalies sont signalées |
