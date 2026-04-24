# Déroulé des séances

Principe : **un chantier par séance**, dans l'ordre du guide (modèle et MLflow → pipeline et API → CI/CD), et une
simulation de soutenance avant la vraie. Chaque séance commence par 5 minutes « avancement, difficultés, ce que tu as
compris de l'attendu » et finit par une liste d'actions écrite par l'apprenant.

## Temps plein (4 semaines, 3 séances + soutenance)

### Séance 1 — Données et cadrage (semaine 1, 45 min)

| Minutes | Contenu |
|---|---|
| 0-5 | Avancement, questions préparées par l'apprenant |
| 5-15 | « Reformule-moi la demande. » Les deux fonctions (prédire, recommander), les 5 livrables, ce qui est noté (deux compétences) |
| 15-30 | Ses premières observations sur les deux jeux. Faire trouver : jeu synthétique (cultures identiques), doublons de `yield_df.csv`, noms de pays. Fiches 1 et 2 |
| 30-40 | Stratégie de fusion : « Quelle clé commune ? » Laisser conclure que la fusion par pays est impossible. ACP : fiche 3 |
| 40-45 | Actions : CSV consolidé avec journal des lignes, ACP lue honnêtement, première référence naïve |

### Séance 2 — Modèle et MLflow (semaine 2, 45 min)

| Minutes | Contenu |
|---|---|
| 0-10 | Montre-moi ton découpage train / test. Si aléatoire : fiche 4, faire refaire en direct avec `GroupKFold` |
| 10-25 | Ses expériences MLflow à l'écran : quelle métrique, pourquoi ; une référence ? au moins 2 expériences ? graine ? Fiche 5 |
| 25-35 | « Quel hyperparamètre a compté, et pourquoi cette plage ? » « Que dirais-tu à un agriculteur ? » |
| 35-45 | Structurer le code en étapes (préparer / entraîner / évaluer), configuration centralisée (fiche 6). Actions : modèle final sauvegardé, test unique |

### Séance 3 — API, Docker, CI/CD (semaine 3, 45 min)

| Minutes | Contenu |
|---|---|
| 0-15 | Démonstration de son API (`/docs`) et de l'interface. Entrée absurde → 422 ? Fiche 7 |
| 15-30 | Lecture de son workflow CI : ordre des étapes, `needs`, secrets, que se passe-t-il si un test échoue ? Fiche 8 |
| 30-40 | « Lance ton pipeline dans un conteneur neuf » (ou sur un autre poste) : reproductible ? |
| 40-45 | Actions : rapport métier (fiche 9 pour la recommandation), support de soutenance, plan minuté |

### Semaine 4 — Simulation de soutenance (30 min, peut remplacer une partie de la séance 3 si le temps manque)

Jouer le Lead Data Scientist avec le minutage réel : 15 min de présentation chronométrée, 10 min de questions
(choisir dans [02_questions_oral.md](02_questions_oral.md) § 6), 5 min de retour. Points à vérifier : plan
problème → solution → impact ; une slide d'architecture globale ; 5 min entraînement / 5 min MLOps / 5 min CI/CD et
impact ; captures MLflow lisibles.

## Alternance (8 semaines, 7 séances + soutenance)

| Séance | Semaine | Chantier | Fiches |
|---|---|---|---|
| 1 | 1 | Lecture de l'énoncé, environnement, premier regard sur les deux jeux | 1 |
| 2 | 2 | Doublons, harmonisation des pays, CSV consolidé, ACP | 2, 3 |
| 3 | 3 | Référence naïve, découpage par pays, premiers modèles | 4 |
| 4 | 4 | Optimisation des hyperparamètres et MLflow (captures) | 5 |
| 5 | 5 | Pipeline en étapes, configuration, modèle sauvegardé ; début de l'API | 6, 7 |
| 6 | 6-7 | Interface, Dockerfile, workflow CI/CD, échec simulé | 8 |
| 7 | 7-8 | Recommandation, rapport métier, simulation de soutenance | 9 |

En alternance, l'apprenant perd vite le fil entre deux séances : lui demander de tenir un **journal de bord** (une
ligne par expérience : ce qui a été essayé, le score, ce qu'il en conclut). C'est aussi la meilleure préparation à
la question « comment avez-vous choisi vos hyperparamètres ? ».

## Si l'apprenant est en retard

Priorités, dans l'ordre de la grille : (1) expériences comparées dans MLflow avec une référence et une recherche
systématique ; (2) étapes du pipeline séparées et environnement reproductible ; (3) workflow YAML avec tests et
build. L'interface Streamlit et le déploiement réel passent après : une interface minimale suffit, le déploiement
est facultatif mais conseillé par l'énoncé.
