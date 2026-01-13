# Séance bilan : préparation et trame de compte-rendu

## Avant la séance (30 min)

1. Télécharger les livrables et **exécuter le notebook** dans l'environnement fourni (critère C de la grille).
2. Remplir la [grille d'évaluation](04_grille_evaluation.md) : 🟢 / 🟠 / 🔴.
3. Comparer 3 ou 4 chiffres clés avec le [corrigé](README.md#chiffres-de-référence-corrigé) : nombre de faux pays,
   nombre d'indicateurs restants, années retenues.
4. Choisir **2 axes de progrès maximum** : au-delà, rien n'est retenu.
5. Préparer 2 ou 3 questions d'oral dans [02_questions_oral.md](02_questions_oral.md), de préférence sur un point 🟠.

## Pendant la séance (45-60 min)

| Minutes | Contenu |
|---|---|
| 0-10 | L'apprenant présente sa fiche d'autoévaluation et ses notes |
| 10-25 | Présentation « comme devant Mark » (10 min max), puis questions |
| 25-40 | Questions d'oral ciblées sur les points 🟠 |
| 40-50 | Difficultés rencontrées et points forts, selon l'apprenant |
| 50-60 | Actions pour la suite : ressources, points de vigilance pour le projet suivant |

**Validation** : on valide s'il n'y a aucun 🔴. Les 🟠 deviennent des objectifs pour le projet suivant.

## Trame de compte-rendu (à copier sur la plateforme)

```markdown
**Bilan du projet** (sur la base de l'autoévaluation)
- Exploration et nettoyage : …
- Réduction du périmètre et choix des indicateurs : …
- Analyse statistique (corrélations, distributions) : …
- Présentation et storytelling : …
- Environnement reproductible (uv) : …

**Points d'amélioration et recommandations**
1. … (constat précis → action concrète)
2. …

**Ressources suggérées**
- … (fiche du dossier pedagogie/, chapitre de cours, documentation)

**Encouragements**
- … (une qualité précise et observée, par exemple : « ta règle de détection des faux pays a été vérifiée sur ses
  exceptions, c'est exactement le bon réflexe »)
```

## Exemples de formulations

| Situation | Formulation |
|---|---|
| Hardcoding | « Ton code supprime les faux pays par position (lignes 5, 57…). Si les données sont triées, il supprime les mauvais pays. Pour le prochain projet : toujours filtrer par valeur (`isin`). » |
| Seuils non justifiés | « Ton seuil de 50 % est raisonnable, mais il n'est pas argumenté. Montre le graphique du remplissage et explique ce que tu perds en dessous. » |
| Présentation trop technique | « Mark ne connaît pas `pivot_table`. Remplace la capture de code par une phrase : "une ligne par pays, une colonne par indicateur". » |
| Très bon travail | « Le test de sensibilité aux poids va au-delà des attentes : c'est ce qui rend ta recommandation crédible. » |
