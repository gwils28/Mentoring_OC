# Séance bilan : démonstration en direct et compte-rendu

## Avant la séance (30 min)

1. Ouvrir la base de l'apprenant dans SQLite Studio (ou lui demander de partager son écran avec la sienne).
2. Remplir la [grille](04_grille_evaluation.md) à partir des livrables.
3. Comparer 4 chiffres avec les [chiffres de référence](README.md#chiffres-de-référence-corrigé) : volumes chargés,
   besoins 1, 5 et 9.
4. Choisir 3 requêtes pour la démonstration (voir ci-dessous) et **une modification** à demander en direct.

## Scénario de démonstration en direct (15-20 min)

L'objectif est de vérifier que l'apprenant **comprend** ses requêtes, pas qu'il les a écrites.

| Étape | Ce qu'on demande | Ce qu'on observe |
|---|---|---|
| 1 | « Montre-moi que ta base contient tout » : les 4 `COUNT(*)` | il sait les retrouver et les comparer aux CSV |
| 2 | Exécuter le **besoin 2** (jointures sur 4 tables) et expliquer le chemin vente → région | il lit sa requête clause par clause |
| 3 | Exécuter le **besoin 9** et dire pourquoi c'est HAVING et pas WHERE | WHERE / HAVING compris |
| 4 | Exécuter le **besoin 10 ou 11** (CTE ou sous-requête) | il sait isoler une étape et l'exécuter seule |
| 5 | **Modification en direct** : « refais le besoin 9 pour le 2ᵉ trimestre », ou « le besoin 11 pour les départements 34 et 44 », ou « le besoin 5 pour les appartements » | il modifie le bon endroit sans tout réécrire |
| 6 | « Ton appartement le plus cher : qu'en dis-tu ? » | il repère l'anomalie |

Une requête qui ne tourne pas en direct n'est pas bloquante si l'apprenant sait diagnostiquer pourquoi.

## Pendant la séance (45-60 min)

| Minutes | Contenu |
|---|---|
| 0-10 | Fiche d'autoévaluation de l'apprenant |
| 10-30 | Démonstration en direct (ci-dessus) |
| 30-40 | Questions ciblées sur les points 🟠 ([02_questions_oral.md](02_questions_oral.md)) |
| 40-50 | Difficultés et points forts, selon l'apprenant |
| 50-60 | Actions pour la suite |

**Validation** : aucun 🔴. Les 🟠 deviennent des objectifs pour le projet suivant.

## Trame de compte-rendu

```markdown
**Bilan du projet** (sur la base de l'autoévaluation)
- Modélisation (dictionnaire, schéma, 3NF, clés) : …
- Création et chargement (types, contraintes, volumes vérifiés) : …
- Requêtes (12 besoins, lisibilité, démonstration en direct) : …
- Présentation et lecture métier : …

**Points d'amélioration et recommandations**
1. … (constat précis → action concrète)
2. …

**Ressources suggérées**
- … (fiche du dossier pedagogie/, chapitre de cours, documentation SQLite)

**Encouragements**
- … (une qualité précise et observée)
```

## Exemples de formulations

| Situation | Formulation |
|---|---|
| Corse perdue | « Ta base contient 33 918 ventes au lieu de 34 169 : les 251 ventes de Corse ont disparu parce que le département est un nombre. Pour le prochain projet : tout code est du texte. » |
| Moyenne sans effectif | « Tu classes La Réunion 2ᵉ région la plus chère : c'est une moyenne sur 2 ventes. Affiche toujours le nombre de lignes à côté d'une moyenne. » |
| Commentaire technique | « Ta diapositive dit "GROUP BY région". Le directeur veut lire : "l'Île-de-France fait 45 % des ventes d'appartements". » |
| Très bon travail | « Tu as repéré que l'appartement à 9 M€ pour 9 m² est une anomalie au lieu de le présenter comme un résultat : c'est exactement le réflexe d'un analyste. » |
