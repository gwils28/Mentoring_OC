# Erreurs fréquentes : diagnostic et remédiation

| # | Erreur | Comment la repérer | Pourquoi c'est un problème | Remédiation |
|---|---|---|---|---|
| 1 | Supprimer des lignes par position (`iloc`, `drop([5, 57])`) | numéros en dur dans le code | le résultat change dès qu'on trie ou filtre | [fiche 1 §5](../pedagogie/01_maille_et_qualite.ipynb) : filtrer par valeur |
| 2 | Faux pays non retirés | « World » ou « High income » en tête d'un classement | les agrégats écrasent les comparaisons | [fiche 1 §4](../pedagogie/01_maille_et_qualite.ipynb) |
| 3 | Règle des faux pays non vérifiée | 27 pays supprimés au lieu de 25 | Gibraltar et Nauru perdus | lire toutes les lignes supprimées ; tester la règle sur ses exceptions |
| 4 | `dropna()` global | DataFrame vide ou minuscule | aucune ligne n'est complète sur 1970-2100 | mesurer les vides **par colonne** puis choisir |
| 5 | Projections mélangées aux observations | moyenne calculée sur 1970-2100 | moyenne de données réelles et de prévisions | séparer les colonnes ≥ 2020 ([corrigé §2.2](../notebooks/projet_edstats_corrige.ipynb)) |
| 6 | Filtres non chiffrés | aucun `len()` ni `shape` avant / après | impossible de défendre la démarche en présentation | journal des filtres (`FilterLog`) ou un `print` avant / après |
| 7 | `df_1`, `df_2`, … `df_14` | noms sans signification | l'apprenant ne relit plus son propre code | nommer par le contenu : `proportion_indicateurs_par_annee` |
| 8 | Copier-coller du même bloc pour chaque indicateur | blocs quasi identiques | une correction à faire N fois | fonction + boucle `for` ([fiche 4 §4](../pedagogie/04_distributions.ipynb)) |
| 9 | Moyenne sur 1 ou 2 années | pivot sans contrôle du nombre d'années | valeur isolée présentée comme une tendance | `where(nb_annees >= 3)` ([fiche 2 §5](../pedagogie/02_filtrer_agreger.ipynb)) |
| 10 | `describe()` sur tout `Data` interprété comme s'il avait du sens | « la moyenne des indicateurs est de 10¹⁰ » | unités hétérogènes (%, habitants, $) | `describe()` indicateur par indicateur |
| 11 | Pearson seul sur des données asymétriques | corrélations dominées par la Chine et l'Inde | coefficient tiré par 2 pays | Spearman ou échelle log ([fiche 3](../pedagogie/03_correlations.ipynb)) |
| 12 | Garder des indicateurs redondants dans le score | PIB/hab **et** internet **et** scolarisation | le développement compté 3 fois | une variable par bloc ([fiche 5 §4](../pedagogie/05_scorer_des_pays.ipynb)) |
| 13 | Additionner des critères d'unités différentes | score = population + % internet | la population décide de tout | normaliser (rangs) avant de pondérer |
| 14 | Supprimer les valeurs extrêmes « parce qu'elles dépassent » | outliers retirés sans justification | on supprime l'Inde, la Chine… ou une réalité (27 % de chômage) | ne supprimer que l'**impossible** |
| 15 | Conclusions causales | « internet fait augmenter la scolarisation » | corrélation ≠ causalité | reformuler en association |
| 16 | Graphiques sans titre ni axes, ou avec des couleurs inutiles | histogramme multicolore, axes « x », « y » | illisible pour Mark | titre qui dit le message, axes avec unités, une seule couleur si elle ne code rien |
| 17 | Présentation « scolaire » | une slide par cellule du notebook | Mark ne retient rien | storytelling : problème, données, démarche, réponse, limites |
| 18 | Environnement non reproductible | pas de `pyproject.toml`, ou dépendances absentes | « chez moi ça marche » | `uv init`, `uv add`, `uv sync` ([ALLER_PLUS_LOIN §1](../ALLER_PLUS_LOIN.md)) |

## Profils et points de vigilance

- **N'a jamais codé** : risque de se perdre dans les généralités Python. Le recentrer sur pandas et proposer des
  petites victoires rapides (charger, `shape`, `head`).
- **Développeur en reconversion** : code propre mais analyse superficielle (« j'ai filtré à 50 % » sans
  justification). Le pousser sur le *pourquoi* statistique et métier.
- **Profil statistique** : bonne analyse, mais notebook de 200 cellules répétitives. Le pousser sur les fonctions,
  le nommage et un module `.py`.
