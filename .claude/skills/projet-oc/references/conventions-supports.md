# Conventions des supports

## Arborescence d'un projet

```text
Pxx-nom-du-projet/
├── README.md  PLAN.md  ALLER_PLUS_LOIN.md  pyproject.toml  uv.lock  .python-version
├── src/<package>/   tests/   notebooks/   pedagogie/   kit-mentor/   presentation/   site/
├── data/processed/          (versionné : sorties légères du corrigé)
├── data/raw/                (gitignoré, immuable : hook de protection)
└── _mentor_notes/           (gitignoré : énoncé + guide mentor OC)
```

## Fiche pédagogique (`pedagogie/NN_sujet.ipynb`)

1. Titre « Fiche N — … », puis un tableau : 🎯 Objectif (observable) · ⏱️ Durée · 🧰 Prérequis · 🔗 Dans le projet
   (étape de l'énoncé).
2. Encadré « **L'idée clé** » en 2 ou 3 phrases.
3. Sections numérotées : intuition ou exemple **sur les vraies données**, puis démonstration exécutable.
4. Au moins un **⚠️ piège**, démontré par un contre-exemple exécutable.
5. **✍️ À toi de jouer** : énoncé, cellule vide, solution dans `<details><summary>💡 Voir une solution</summary>`
   avec l'explication du *pourquoi*.
6. **✅ À retenir** : 4 à 6 points numérotés.
Public : débutant complet. Une notion nouvelle à la fois. Tutoiement dans les fiches, vouvoiement sur la page web.

## Kit mentor (`kit-mentor/`)

`README.md` (tableau « quand / fichier / pour quoi faire », repères, ressources, **chiffres de référence**) ·
`01_deroule_des_seances.md` (temps plein et alternance, minutage) · `02_questions_oral.md` (question → attendu →
🚩 signal d'alerte → 🔁 relance) · `03_erreurs_frequentes.md` (erreur, repérage, pourquoi, remède avec un lien
vers la fiche) · `04_grille_evaluation.md` (grille **reformulée**, 🟢 / 🟠 / 🔴, lien vers la section du corrigé) ·
`05_trame_bilan.md` (préparation, déroulé, trame de compte-rendu, formulations).

## Présentation

`presentation/build_deck.js` (pptxgenjs, layouts, sections, notes orateur sur chaque slide) + `theme_colors.js`,
avec `package.json` et `package-lock.json` versionnés (`node_modules/` gitignoré). Les titres de slide énoncent un
message. La structure narrative va dans `presentation/README.md`. Pas de version web de la présentation : le `.pptx`
suffit (décision de l'utilisateur, oct. 2026).

## Page interactive (`site/index.html`)

Artifact HTML adapté au thème clair et sombre, utilisable sur mobile. Contenu type : la demande du client, les étapes
du projet (onglets : à faire / piège / question du mentor / fiche), l'entonnoir chiffré, 1 ou 2 **labos
interactifs** sur les notions clés (avec les vraies données du corrigé embarquées en JSON), un quiz avec
explications, la check-list des livrables (stockage local). Contrôle : syntaxe JS vérifiée avec
`node --check` + une capture avec Chrome headless.

## Commits et dates

- Un sujet par commit, avec un message en français au format « Pxx : … ».
- Les dates sont fixées avec `GIT_AUTHOR_DATE` et `GIT_COMMITTER_DATE` (fuseau +01:00), du lundi au vendredi,
  entre 9 h et 19 h. Un projet couvre environ 2 semaines de jours ouvrés ; le projet suivant commence le lundi qui
  suit. Pour trouver le prochain créneau : `git log -1 --format=%ad --date=iso`.
- E-mail de commit : l'adresse noreply GitHub, configurée localement dans le repo (sinon le push est refusé).
- Ne jamais réécrire un historique déjà poussé.
