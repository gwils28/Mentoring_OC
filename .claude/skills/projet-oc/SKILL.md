---
name: projet-oc
description: Procédure pour traiter un projet OpenClassrooms de bout en bout dans le repo Mentoring_OC (récupérer l'énoncé et le guide mentor, cadrer, réaliser le corrigé, produire notebooks pédagogiques, kit mentor, présentation, page interactive et « aller plus loin », faire relire par les subagents, committer avec la convention de dates). À utiliser dès que l'utilisateur demande de traiter, reprendre ou compléter un projet d'un parcours.
---

# Traiter un projet OpenClassrooms

Référence de qualité : `Data-Engineer/P01-analyse-systemes-educatifs/`. En cas de doute sur un format, copie sa
structure. Conventions détaillées des supports : [references/conventions-supports.md](references/conventions-supports.md).

## 0. Récupérer l'énoncé (Claude in Chrome, session mentor de l'utilisateur)

- Page du projet : `https://openclassrooms.com/fr/paths/<parcours>/projects/<id>/...`. Liste les sous-pages avec
  `javascript_tool` (liens contenant `/projects/<id>/`). Les pages utiles sont les exercices ou étapes,
  « Livrables et bilan », `mentor-guide` (grille d'évaluation détaillée) et l'évaluation.
- Les pages se chargent lentement : attendre environ 3 s avant `get_page_text`. Les étapes sont des **accordéons** :
  cliquer en JS sur les `main button, main summary, main [aria-expanded]` dont le texte contient « Étape », puis
  relire la page. Les encadrés « Conseils mentor » ne sont visibles qu'avec un compte mentor.
- Sauvegarder énoncé + guide dans `<projet>/_mentor_notes/enonce_et_guide_mentor.md` (gitignoré). Ne **jamais**
  recopier ce contenu ailleurs : le kit mentor le reformule.
- Fermer les onglets ouverts.

## 1. Cadrer (avant tout code)

1. Télécharger et explorer les vraies données : tailles, clés, valeurs manquantes, pièges. Les chiffres des supports
   viendront de là.
2. Appeler **`product-owner`** en mode cadrage : livrables, critères d'acceptation, traçabilité vers la grille.
3. Écrire `PLAN.md` : question métier, protocole d'analyse (tableau décision / choix / justification), livrables
   avec leur preuve de fin, vérifications, hors périmètre.
4. Appeler **`statisticien`** sur le protocole du `PLAN.md` **avant** de produire des résultats (projets d'analyse
   ou de ML).
5. Interroger l'utilisateur seulement sur ce qui change le résultat (`AskUserQuestion`).

## 2. Réaliser le corrigé

- Projet `uv` autonome (`uv init --package --python 3.12 --no-workspace .`, puis **supprimer le `.git` que
  `uv init` crée**). Dépendances avec `uv add`.
- Code réutilisable dans `src/<package>/` : `io.py` (téléchargement + SHA-256), et des modules par sujet.
  **Tests d'abord** (`tests/`). Pour du code non trivial, déléguer à **`expert-data-engineering`**.
- Notebook corrigé dans `notebooks/`, **généré depuis un script du scratchpad puis exécuté**
  (`uv run jupyter nbconvert --to notebook --execute --inplace`). Lire les sorties, puis écrire les
  interprétations à partir des valeurs réelles.
- Figures : style commun (`viz.apply_style()`), validé avec le skill `dataviz` ; export dans
  `presentation/figures/`.
- Appeler **`statisticien`** sur les résultats (il recalcule les chiffres clés), et **`expert-data-engineering`** en
  relecture du package si besoin.

## 3. Produire les supports

| Support | Où | Relecteur |
|---|---|---|
| Notebooks pédagogiques (une notion par fiche) | `pedagogie/` | `pedagogue`, puis `statisticien` pour les notions statistiques |
| Kit mentor (README, déroulé, questions, erreurs, grille, bilan) | `kit-mentor/` | `pedagogue` |
| Présentation `.pptx` générée par script + version web (artifact Slides) | `presentation/` | `pedagogue` (storytelling) |
| Page interactive pour les apprenants (artifact) | `site/index.html` | `pedagogue` |
| Pratiques actuelles du marché | `ALLER_PLUS_LOIN.md` | `expert-data-engineering` (+ `statisticien`) |
| README du projet : par où commencer, résultats, écarts au plan, limites | `README.md` | `product-owner` |

Lance les relecteurs **en parallèle** quand ils portent sur des fichiers différents. Applique les constats 🔴 et
🟠 ; pour les 🟢, décide toi-même et dis-le.

## 4. Recette et livraison

1. **`product-owner`** en mode recette : rien n'est « fini » sans sa décision « accepté ».
2. Vérifications finales : `uv run pytest -q`, `ruff`, tous les notebooks réexécutés sans erreur,
   `git ls-files | grep -E "_mentor_notes|data/raw"` vide.
3. Commits **par sujet**, datés selon [la convention](references/conventions-supports.md#commits-et-dates), puis
   `git push`.
4. Mettre à jour le `README.md` racine (tableau des parcours) et le `README.md` du parcours.

## Pièges connus

- Les nombres cités dans un support doivent venir d'une sortie : vérifie-les avant d'écrire. Sur P01, plusieurs
  formulations plausibles étaient fausses (« la Chine vaut 1 en min-max », « Pearson s'effondre »).
- Une matrice issue d'un `pivot_table` a des index et colonnes de même nom : `stack()` plante (test dédié dans P01).
- Pas de LibreOffice sur la machine : le `.pptx` se valide par schéma et extraction du texte ; le contrôle visuel se
  fait sur la version web.
- Les artifacts sont privés : rappeler à l'utilisateur de les partager depuis le menu Share.
