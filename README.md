# Mentoring OpenClassrooms

Supports de mentorat pour les parcours OpenClassrooms que j'accompagne : pour chaque projet, un **corrigé de
référence** réalisé de bout en bout, des **notebooks pédagogiques** (une notion par notebook, sur les vraies
données), un **kit mentor** pour mener les séances, une **page interactive** à partager avec les apprenants et
une section **« aller plus loin »** sur les pratiques actuelles du métier.

## Parcours

| Parcours | Projets traités |
|---|---|
| [Data Engineer](Data-Engineer/) | [P01 — Analysez les données de systèmes éducatifs](Data-Engineer/P01-analyse-systemes-educatifs/) |
| Data Scientist — Machine Learning | à venir |
| AI Engineer | à venir |
| Architecte Logiciel | à venir |
| Expert DevOps | à venir |

## Organisation d'un projet

```text
Pxx-nom-du-projet/
├── README.md            ← point d'entrée : résultats, comment lancer, plan vs réalité
├── PLAN.md              ← protocole figé avant de voir les résultats
├── pyproject.toml       ← dépendances (uv) ; uv.lock fige les versions
├── src/<package>/       ← code réutilisable et testé
├── tests/
├── notebooks/           ← corrigé (livrable étudiant)
├── pedagogie/           ← une notion = un notebook, à dérouler en séance
├── kit-mentor/          ← déroulé des séances, questions d'oral, grille, erreurs fréquentes
├── presentation/        ← support de soutenance (.pptx) + figures
├── site/                ← page interactive pour les apprenants
└── ALLER_PLUS_LOIN.md   ← pratiques actuelles du marché sur les notions du projet
```

## Méthode

Ces supports sont produits avec Claude Code selon la méthode décrite dans
[Claude Code pour la data science](https://gwils28.github.io/posts/claude-code-data-science/) : plan écrit avant le
code, tests, données brutes vérifiées par empreinte, notebooks exécutés et versionnés, et relecture humaine de
chaque commit.

Les énoncés et guides mentor d'OpenClassrooms ne sont **pas** publiés ici : le kit mentor les reformule.
