# Erreurs fréquentes : diagnostic et remédiation

Beaucoup d'erreurs de ce projet **naissent dans le tableur** avant même que la base existe. Demander à voir le CSV
ouvert dans un éditeur de texte révèle la plupart d'entre elles.

| # | Erreur | Comment la repérer | Pourquoi c'est un problème | Remédiation |
|---|---|---|---|---|
| 1 | Corse perdue (2A, 2B) | 33 918 ventes au lieu de 34 169 ; aucune commune « 2A… » | code lu comme un nombre (tableur ou colonne `INTEGER`) : « 01 » devient 1, la clé reconstruite ne correspond plus et la jointure perd les lignes | fiche 3 §1 ; codes en texte |
| 2 | Zéros initiaux perdus | codes postaux à 4 chiffres, département « 1 » | le tableur a converti en nombre | importer les colonnes en texte ; `TEXTE(A2;"00000")` |
| 3 | Code postal pris comme clé de la commune | doublons de clé ou communes fusionnées | un code postal couvre plusieurs communes | fiche 3 §3 ; clé département + commune |
| 4 | Nom de l'acquéreur conservé | colonne présente dans le dictionnaire ou la base | donnée personnelle inutile (RGPD) | fiche 4 §3 |
| 5 | Région répétée dans `commune` ou `bien` | `nom_region` hors de la table `region` | viole la 3NF ; risque de contradiction | fiche 2 §3 |
| 6 | Clés étrangères non vérifiées | un bien rattaché à une commune inexistante est accepté | SQLite ignore les FK par défaut | `PRAGMA foreign_keys = ON;` (fiche 3 §2) |
| 7 | Colonnes inversées à l'import | des prix dans la colonne date | l'import associe par position | afficher 5 lignes après chaque import (fiche 5 §3) |
| 8 | Vide importé comme `''` | `AVG` plus bas que prévu ; `COUNT(col)` = `COUNT(*)` | `''` est lu comme 0 | `UPDATE … SET col = NULL WHERE col = ''` (fiche 5 §1) |
| 9 | CSV non UTF-8 | accents remplacés par des symboles | export tableur en Windows-1252 | « Enregistrer sous » CSV UTF-8 |
| 10 | Dates au format jj/mm/aaaa | `BETWEEN '2020-01-01' AND '2020-03-31'` ne renvoie rien ou des résultats faux | le texte se compare caractère par caractère | stocker en AAAA-MM-JJ |
| 11 | WHERE sur un agrégat | erreur « misuse of aggregate » | le COUNT n'existe pas encore au WHERE | HAVING (fiche 6 §3) |
| 12 | Division entière | proportions à 0 | entier / entier = entier | `100.0 *` avant la division (fiche 8 §1) |
| 13 | Jointure qui perd des lignes | somme des groupes < total attendu | INNER JOIN sans correspondance, sans erreur | prédire puis compter ; LEFT JOIN pour trouver les orphelins (fiche 7) |
| 14 | Filtre sur le nom « Île-de-France » qui ne renvoie rien | 0 ligne au besoin 5 | la source écrit « Ile-de-France » sans accent | filtrer sur le code région ('11') |
| 15 | Département « 6 » au lieu de « 06 » | besoin 11 vide pour les Alpes-Maritimes | code en texte sur 2 caractères | `IN ('06', '13', …)` |
| 16 | Groupement par nom de commune | homonymes fusionnés | 15 noms partagés par plusieurs communes | grouper par la clé, afficher le nom |
| 17 | Moyenne présentée sans effectif | « La Réunion 2ᵉ région la plus chère » | moyenne sur 2 ventes | afficher `COUNT(*)` à côté de chaque moyenne |
| 18 | Résultats commentés en SQL | « j'ai fait un GROUP BY » | l'interlocuteur n'est pas technicien | une phrase métier par résultat ([fiche transverse](../../transverse/presenter_un_resultat.md)) |

## Profils

- **Découvre l'informatique** : rassurer, avancer par petites victoires (créer une table, insérer une ligne, la
  relire). Les fiches 1 et 5 en séance.
- **À l'aise en tableur, pas en SQL** : très bon sur la préparation, perdu sur les jointures ; insister sur la
  fiche 7 et la prédiction du nombre de lignes.
- **Déjà développeur** : risque de bâcler le dictionnaire et la normalisation ; insister sur la justification des
  types et des clés, et proposer PostgreSQL.
