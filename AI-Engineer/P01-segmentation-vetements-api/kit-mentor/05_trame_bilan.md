# Trame de la séance bilan

Pas de soutenance : c'est le mentor qui valide. La séance suit les 4 temps prévus par OpenClassrooms
(autoévaluation, difficultés, points forts, suite), avec une courte démonstration au début.

## Avant la séance (20 min)

1. Télécharger les livrables (notebook, présentation) ; vérifier le nommage `Nom_Prenom_1_notebook_mmaaaa`, etc.
2. Parcourir la [grille](04_grille_evaluation.md) ; noter les 🔴 éventuels.
3. Chercher le token : ouvrir le `.ipynb` dans un éditeur de texte, rechercher `hf_`.
4. Comparer ses chiffres aux [chiffres de référence](README.md#chiffres-de-référence-corrigé) ; préparer une
   question pour chaque écart qu'il n'explique pas.

## Déroulé (45 min)

| Minutes | Temps | Contenu |
|---|---|---|
| 0–8 | Démonstration | L'apprenant exécute **une** cellule d'appel en direct (ou montre la réponse JSON en cache) et commente une figure avant / après |
| 8–20 | Autoévaluation | On parcourt sa fiche d'autoévaluation ; il justifie chaque critère coché ; on pose 2 ou 3 [questions](02_questions_oral.md) |
| 20–28 | Difficultés | Ce qui a été le plus dur, comment il l'a débloqué (les crédits, l'adresse de l'API, le base64 reviennent souvent) |
| 28–36 | Points forts | Ce qu'il a aimé faire, ce qui lui a paru simple ; valoriser les initiatives (fuite repérée, inférence locale, slide 7) |
| 36–45 | Suite | 2 ou 3 actions concrètes pour le projet suivant ; ressources |

## Questions de synthèse, à choisir

- « En 30 secondes, que réponds-tu à la directrice IA ? » (attendu : faisable, prometteur à confirmer, coût faible)
- « Qu'est-ce qui pourrait faire exploser le budget ? » (volume, images en pleine taille, GPU inutile, nouvelles
  tentatives en boucle)
- « Que faudrait-il pour affirmer que le modèle marche sur les photos de ModeTrends ? » (photos nouvelles annotées,
  découpées par influenceur)

## Trame de compte-rendu (à copier sur la plateforme)

> **Bilan du projet.** [Prénom] a livré un notebook [structuré en sections / à restructurer] qui appelle le modèle
> segformer_b3_clothes par l'API Hugging Face [avec / sans] gestion des erreurs (timeout, limite de requêtes,
> nouvelles tentatives) et un token [correctement protégé / à protéger]. La visualisation [compare photo,
> annotation et prédiction / mérite d'ajouter l'annotation]. L'évaluation [repose sur l'IoU par vêtement / reste
> qualitative] et le budget pour 500 000 images [est calculé et sourcé / reste à justifier].
>
> **Points d'amélioration et recommandations.** [1 à 3 points précis, ex. : « distinguer les erreurs à réessayer
> (503) de celles à corriger (401) » ; « citer la source et la date de chaque prix »].
>
> **Ressources.** [fiches pédagogiques ciblées, ex. fiche 4 « Un client qui ne plante pas »] ; documentation des
> Inference Providers de Hugging Face.
>
> **Encouragements.** [une qualité observée, ex. : « la rapidité avec laquelle tu as compris le format base64 » ;
> « le soin apporté à la protection du token » ; « tu as repéré seul que les images de test étaient déjà connues
> du modèle »].

## Formulations utiles

- Plutôt que « c'est faux » : « montre-moi d'où vient ce chiffre ».
- Sur la fuite de données (apprenant à l'aise) : « ton calcul est juste ; la question est ce qu'il prouve ».
- Sur un 🟠 : « ce n'est pas bloquant pour passer au projet suivant ; c'est le point à travailler en premier ».
