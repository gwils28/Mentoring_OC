# Soutenance et bilan

## Préparation (20 min avant)

1. Lire les 5 livrables avec la [grille](04_grille_evaluation.md) ; noter les critères incertains, à vérifier à
   l'oral.
2. Ouvrir les captures MLflow : nombre d'expériences, métrique principale, référence, découpage.
3. Ouvrir le YAML du workflow : ordre des jobs, tests, build, publication, secrets.
4. Préparer 4 questions de discussion (une par thème de la soutenance : choix techniques, robustesse, impact
   métier, hyperparamètres) dans [02_questions_oral.md](02_questions_oral.md), dont une question méthodologique
   (« comment avez-vous fait pour… ») si un livrable semble trop lisse.

## Déroulé (30 min)

| Temps | Rôle de l'évaluateur | Ce qu'on observe |
|---|---|---|
| 0-15 | Lead Data Scientist, écoute, chronomètre | Plan problème → solution → impact ; MLflow lisible ; schéma d'architecture ; durée entre 10 et 20 min |
| 15-25 | Lead Data Scientist, challenge | Choix des modèles et des réglages ; échec d'une étape du pipeline ; utilité pour un exploitant ; hyperparamètre décisif |
| 25-30 | Sort du rôle : débrief | Points forts, points à travailler, décision expliquée |

Pendant la présentation, noter les affirmations chiffrées : on les vérifiera dans les captures ou le notebook à la
discussion. Interrompre seulement si la présentation dépasse 20 minutes.

## Débrief : formulations utiles

- Point fort méthodologique : « Tu as testé tes modèles sur des pays qu'ils n'avaient jamais vus : c'est exactement
  la situation d'un nouveau client, et c'est ce qui rend tes chiffres crédibles. »
- Honnêteté sur les données : « Tu as montré que la fusion demandée n'était pas possible au lieu de la forcer.
  En entreprise, c'est ce qu'on attend d'un data scientist : dire ce que les données permettent. »
- À consolider (découpage) : « Ton R² de 0,9 vient en partie de ce que le modèle reconnaît les pays. Refais
  l'évaluation par pays : le chiffre baissera, et il sera plus juste. »
- À consolider (recommandation) : « Ton classement bat le hasard ; la vraie question est : bat-il une liste fixe,
  la même pour tout le monde ? »
- À consolider (rapport) : « Ton rapport parle de RMSE à un directeur commercial. Traduis : "on se trompe d'environ
  37 % sur le rendement moyen, dans un cas typique". »
- Refus (si nécessaire) : « Le critère "hyperparamètres ajustés de façon systématique" n'est pas atteint : tu as
  comparé trois modèles avec leurs réglages par défaut. Il faut une recherche (grille ou aléatoire) tracée dans
  MLflow. Le reste est solide ; c'est ce point qu'on corrige. »

## Trame de compte-rendu

```text
Projet P12 — Système de recommandations agricoles (MLOps)      Date :            Durée présentation : __ min

Compétence 1 — Optimiser l'entraînement :        validée / non validée
  • Expériences MLflow (nombre, métrique principale, lisibilité) :
  • Référence et recherche d'hyperparamètres :
  • Découpage et généralisation :
  • Interprétation et justification :

Compétence 2 — Automatiser le déploiement :      validée / non validée
  • Pipeline (étapes, configuration, reproductibilité) :
  • API / Docker :
  • CI/CD (tests, build, déploiement, échec et notification) :

Données et impact métier :
  • Fusion et ACP (honnêteté sur les données) :
  • Recommandation (références, limites) :
  • Rapport métier (lisibilité, absence de causalité et de rentabilité inventées) :

Soutenance : structure, durée, réponses aux questions :

Points forts :
Axes de progrès :
Décision :
```

## Après la soutenance

Montrer le corrigé (présentation et notebooks) sur un ou deux points discutés, en particulier la comparaison
validation aléatoire / validation par pays et la référence « classement fixe ». Orienter vers
[ALLER_PLUS_LOIN.md](../ALLER_PLUS_LOIN.md) pour la suite (registre de modèles, suivi de dérive, prix).
