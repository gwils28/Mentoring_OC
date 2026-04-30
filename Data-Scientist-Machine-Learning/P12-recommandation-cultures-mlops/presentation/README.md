# Présentation — support de soutenance du corrigé

| Fichier | Rôle |
|---|---|
| `recommandation_cultures_agritech.pptx` | support de soutenance (14 slides, notes orateur sur chaque slide) |
| `build_deck.js` | génère le `.pptx` : thème, layouts, sections et contenu ; lit `../data/processed/resultats.json` |
| `theme_colors.js` | injecte la palette dans le thème PowerPoint |
| `figures/` | figures des notebooks, captures MLflow et de l'interface |

```bash
cd presentation && npm ci && npm run build      # après `uv run agrireco all` et les captures
```

Aucun chiffre n'est saisi à la main : ceux des slides sont lus dans `resultats.json` au moment de la génération.

## Structure : problème → solution → impact, en 15 minutes

La soutenance dure 15 minutes (± 5) devant un évaluateur qui joue le Lead Data Scientist. Minutage indicatif
(dans les notes de la slide 1) :

| Partie | Slides | Minutes | Contenu |
|---|---|---|---|
| Problème | 1-2 | 1 | la demande, les deux fonctions, l'architecture visée |
| Données | 3-4 | 2 | jeu simulé, doublons, noms de pays ; fusion impossible et ACP sans structure |
| Entraînement et MLflow | 5-9 | 5 | validation par pays, comparaison et optimisation, captures MLflow, test final, variables |
| MLOps et CI/CD | 10-11 | 4 | pipeline en étapes et configuration, API et Docker, workflow et gestion des échecs |
| Impact métier | 12-14 | 3 | recommandation face à un classement fixe, ce qu'on peut promettre, conclusion |

Chaque titre énonce un **message** (« Évaluer sur des pays jamais vus, sinon le modèle triche ») plutôt qu'un sujet
(« Validation »). La slide 10 sert de schéma d'architecture globale, demandé par le guide.

Contrôle visuel : ouvrir le `.pptx` dans PowerPoint (pas de rendu automatique sur cette machine).
