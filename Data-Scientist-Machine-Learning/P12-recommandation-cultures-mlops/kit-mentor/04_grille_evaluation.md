# Grille d'évaluation commentée

Grille de travail du mentor et de l'évaluateur, reformulée à partir du guide et regroupée par compétence. Cocher à
la lecture des livrables, puis pendant la soutenance.

Légende : 🟢 acquis · 🟠 à consolider (on en parle, non bloquant) · 🔴 bloquant (refus si non corrigé)

Une compétence est validée si **tous** ses critères sont au moins 🟠. Refus aussi si la présentation dure moins de
10 min ou plus de 20 min (tolérance ± 20 % selon les cas), ou en cas de plagiat.

## Compétence 1 — Ajuster les paramètres des procédures d'entraînement pour optimiser la performance

Livrables : captures MLflow, notebooks ou scripts d'entraînement.

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Au moins deux expérimentations distinctes | Plusieurs expériences ou familles de runs (comparaison de modèles, optimisation…) visibles dans MLflow | 4 expériences, `presentation/figures/mlflow_*.png` |
| ☐ | Métriques lisibles | Colonnes de métriques visibles, runs nommés ; métrique principale identifiée (RMSE, MAE, R², RMSE du log…), score sur données jamais vues, écart entraînement / test | `mlflow_1` et `mlflow_2`, export `data/processed/mlflow_runs.csv` |
| ☐ | Résultats interprétés et justifiés | Une conclusion par expérience, en mots ; lien avec le métier | Corrigé étape 2, § 3 et § 8 |
| ☐ | Code fonctionnel et reproductible | S'exécute de bout en bout ; graine fixée ; versions figées | `uv run agrireco all`, `config.yaml`, `uv.lock` |
| ☐ | Hyperparamètres ajustés systématiquement | GridSearch, RandomSearch (ou Optuna…), plages justifiées | `config.yaml` (section `search`), `train.run_search` |
| ☐ | Comparaison référence / optimisé | Une référence naïve et le gain du modèle optimisé ; choix du modèle justifié | Corrigé étape 2, § 3 (figure `cv_modeles`) |
| ☐ | Modèle final sauvegardé sans erreur | Fichier rechargé, prédiction identique | `models/model.joblib`, corrigé étape 2, § 6 |

**Validation** : 🟢 découpage par pays (ou justifié), référence, recherche systématique, conclusions argumentées ;
🟠 découpage aléatoire mais reconnu comme limite à l'oral, ou interprétation un peu courte ; 🔴 une seule
expérience, aucune recherche systématique, captures sans métriques, ou code qui ne s'exécute pas.

**Point d'attention** : un score très élevé (R² ≥ 0,9) obtenu avec doublons ou découpage aléatoire n'est pas un
motif de refus en soi si le reste est rigoureux, mais il doit être discuté. Un apprenant qui ne sait pas l'expliquer
n'a pas acquis « résultats interprétés et justifiés ».

## Compétence 2 — Automatiser le déploiement en intégrant les évolutions du modèle

Livrables : pipeline MLOps, pipeline CI/CD, soutenance.

### Dépôt de code et intégration

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Étapes clés automatisées | Prétraitement, entraînement, évaluation lancés par des scripts ou commandes, sans manipulation manuelle | `agrireco prepare / train / evaluate / all` |
| ☐ | Étapes isolées | Prétraitement ≠ entraînement ≠ évaluation, reliés par des fichiers | `src/agrireco/` |
| ☐ | Configuration centralisée | YAML ou paramètres en ligne de commande, pas de valeurs en dur | `config.yaml` |
| ☐ | Scripts organisés et documentés | Structure lisible, docstrings ou README, commentaires utiles | README du projet, docstrings |

### Efficacité de l'automatisation

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Environnement reproductible | Dockerfile et/ou requirements.txt (versions figées) ; testé sur une machine ou un conteneur neuf | `api/Dockerfile`, `api/requirements.txt`, `docker-compose.yml` |

### Conformité du pipeline CI/CD

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Fichier YAML du workflow | GitHub Actions, GitLab CI… ; déclencheurs clairs | `.github/workflows/dsml-p12-agrireco.yml` |
| ☐ | Tests unitaires intégrés | `pytest` lancé par le workflow ; tests des fonctions critiques de l'API | job `qualite`, `tests/test_api.py` |
| ☐ | Étapes critiques couvertes | Test → build → déploiement (registre d'images, au moins documenté) | jobs `qualite` → `image` (push GHCR) |
| ☐ | Logs et notifications en cas d'échec | Un échec arrête la suite et prévient (e-mail, résumé, Slack…) | job `alerte`, `docs/ci_cd.md` |

**Validation** : 🟢 workflow complet test → build → publication, échec démontré, environnement reproductible ;
🟠 déploiement seulement documenté, notification limitée à l'e-mail par défaut ; 🔴 pas de YAML, pas de tests dans
le workflow, ou pipeline d'entraînement non automatisé (notebook unique à exécuter à la main).

## Ce qui n'est pas noté mais se discute

- **Étape 1 (fusion, ACP, CSV consolidé)** : pas de critère propre, mais une fusion inventée ou une ACP surinterprétée
  fragilise « résultats interprétés et justifiés ». Accepter toute stratégie de fusion **démontrée**.
- **Interface Streamlit** : attendue par l'énoncé ; une interface minimale suffit.
- **Rapport métier** : vérifier qu'il est lisible par un non-spécialiste, sans causalité ni rentabilité affirmées
  sans données. Il porte la traduction métier attendue en compétence 1.
- **Recommandation** : la grille ne demande pas qu'elle soit bonne ; elle demande des résultats comparés et
  justifiés. Une recommandation qui ne bat pas un classement fixe, dite honnêtement, vaut mieux qu'un « gain »
  mesuré contre le seul hasard.
