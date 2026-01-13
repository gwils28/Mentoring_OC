# Déroulé des séances

Principe : en séance, **l'apprenant parle et partage son écran**, et le mentor questionne. Le mentor ne code à sa
place que pour montrer une méthode (lire une erreur, chercher dans une documentation), jamais pour produire un
livrable.

## Parcours temps plein : 1 séance + bilan

### Séance 1 (vers le milieu du projet, après la partie 1 et le début de la partie 2)

| Minutes | Contenu | Support |
|---|---|---|
| 0-5 | Météo : avancement, temps passé, blocages | — |
| 5-15 | « Raconte-moi le projet comme si j'étais Mark » : contexte, livrables, niveau attendu | [questions §0](02_questions_oral.md#0-compréhension-du-projet) |
| 15-30 | Partage d'écran sur le notebook : maille de chaque fichier, faux pays, valeurs manquantes | [questions §1](02_questions_oral.md#1-exploration-partie-1) |
| 30-45 | Choix des familles d'indicateurs et des années : faire **justifier** chaque filtre | [questions §2](02_questions_oral.md#2-réduction-du-périmètre-partie-2) |
| 45-55 | Une notion fragile ? Dérouler la fiche correspondante | [fiches](../pedagogie/) |
| 55-60 | 3 actions concrètes pour la suite, écrites par l'apprenant | — |

### Bilan : voir [05_trame_bilan.md](05_trame_bilan.md)

## Parcours alternance : 3 séances + bilan

| Séance | Moment | Objectif | Focus |
|---|---|---|---|
| 1 | début, avant de coder | cadrer | comprendre la demande de Mark ; installer l'environnement (uv, JupyterLab) ; charger les 5 fichiers ; « une ligne = ? » |
| 2 | fin de la partie 1 | méthode | faux pays (les 2 méthodes), valeurs manquantes, premières réductions ; montrer comment déboguer |
| 3 | partie 3 en cours | analyse | corrélations, distributions, méthode de sélection des pays ; plan de la présentation |
| Bilan | après dépôt | valider | [05_trame_bilan.md](05_trame_bilan.md) |

## Bonnes pratiques de séance

- **Faire reformuler** plutôt qu'expliquer : « avec tes mots, que mesure Spearman ? »
- **Demander les chiffres** : « combien de lignes ce filtre a-t-il supprimées ? » Un apprenant qui ne sait pas
  répondre n'a pas encore le réflexe de tracer ses filtres.
- **Montrer comment chercher** : copier l'erreur dans un moteur de recherche, lire la *signature* d'une fonction dans
  la documentation pandas (entrées, sorties, paramètres). L'objectif est l'autonomie.
- **IA générative** : à ce stade, déconseiller de lui faire écrire ou déboguer le code. Le projet sert à
  construire les réflexes de base (voir [ALLER_PLUS_LOIN.md](../ALLER_PLUS_LOIN.md#9-lia-générative-dans-le-workflow-data)
  pour en parler en fin de projet).
- **Débutants complets** : les recentrer sur « Python pour la data » (pandas, matplotlib). Ce n'est pas le moment
  d'approfondir les classes, les décorateurs ou les générateurs.
- **Apprenants rapides** : `apply` + `lambda` + `groupby`, fonctions dans un module `.py` séparé, analyses
  bivariées (`pairplot`, `boxplot` par région), Plotly, traitement des outliers.
