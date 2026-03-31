# P01 — Requêtez des services IA

**Parcours AI Engineer · OpenClassrooms · premier projet : appeler un modèle pré-entraîné par API**

Une agence de marketing de mode (ModeTrends) veut repérer automatiquement les vêtements portés sur des photos
d'influenceurs. Première brique : la **segmentation** (quel pixel appartient à quel vêtement). On teste le modèle
`sayeed99/segformer_b3_clothes`, appelé par l'API serverless de Hugging Face, sur 50 photos annotées, puis on chiffre
le traitement de 500 000 images en 30 jours.

## Par où commencer ?

| Vous êtes… | Ouvrez |
|---|---|
| **Mentor**, avant une séance | [kit-mentor/](kit-mentor/) : ce qu'il faut savoir avant la séance 1 (adresse d'API périmée, crédits, fuite de données), déroulé, questions d'oral, erreurs fréquentes, grille, trame de bilan |
| **Apprenant**, en début de projet | la page interactive [site/index.html](site/index.html) (étapes, ateliers IoU et budget, quiz, check-list) |
| **Apprenant**, bloqué sur une notion | [pedagogie/](pedagogie/) : 8 fiches, une notion chacune, exécutables **sans token** |
| Curieux des pratiques actuelles | [ALLER_PLUS_LOIN.md](ALLER_PLUS_LOIN.md) (inférence locale, appels parallèles, endpoints dédiés, modèles récents) |
| À la recherche de la référence | [notebooks/segmentation_vetements_corrige.ipynb](notebooks/segmentation_vetements_corrige.ipynb), [src/segvet/](src/segvet/) et [presentation/](presentation/) |

> Le corrigé sert au mentor à **comparer** ; on ne le transmet pas à l'apprenant avant son bilan. Ses fichiers ne
> suivent pas le nommage de dépôt OpenClassrooms (`Nom_Prenom_1_notebook_mmaaaa`…), réservé aux livrables de l'apprenant.

## Résultats du corrigé

| Étape | Résultat |
|---|---|
| Données | 50 photos (46 en 400 × 600 px) et 50 masques, 18 classes ; le fond occupe 78 % des pixels |
| API | adresse actuelle `router.huggingface.co/hf-inference/…` (celle du notebook fourni est périmée depuis 2025) ; 150 appels sur 150 réussis ; 0,71 s par image en médiane, 1,24 s au 95ᵉ centile |
| Envoi | JPEG réduit à 512 px : 53 Ko, 8 fois plus léger que le PNG d'origine, pour 0,005 point d'IoU de moins |
| Qualité | **mIoU vêtements 0,79** (IC 95 % : 0,76 – 0,82) ; jupe 0,94, pantalon 0,90, haut 0,88, robe 0,80, ceinture 0,57 ; règle fixée à l'avance : « non disqualifié pour un pilote » |
| Limite | les 50 images et masques figurent à l'identique dans le jeu sur lequel le modèle a été affiné : score **optimiste**, qui ne mesure pas la généralisation |
| Coût, 500 000 images / 30 j | serverless < 17 $ (majorant tiré de la facture réelle) · machine CPU dédiée ≈ 50 $ · par lots ≈ 18 $ · GPU T4 360 $ |

Constat principal : techniquement **faisable**, qualité **prometteuse** mais à confirmer sur des photos jamais vues
par le modèle, coût **faible**. Les plus mauvaises images sont des vêtements ambigus (short, tunique) : définir les
classes avec les équipes mode compte autant que le choix du modèle. Tous les chiffres, avec leurs variantes
acceptables, sont dans le [kit mentor](kit-mentor/README.md#chiffres-de-référence-corrigé).

## Lancer le projet

```bash
uv sync --frozen                     # environnement exact (Python 3.12, versions de uv.lock)
uv run pytest                        # tests du package segvet (aucun appel réseau)
uv run jupyter lab
```

Les réponses de l'API sont **en cache** dans `data/processed/` : le corrigé et les fiches se ré-exécutent sans token
ni crédit. Pour refaire les appels : copier `.env.example` en `.env`, y mettre un token Hugging Face (droit
« Make calls to Inference Providers »), supprimer `data/processed/predictions/` et les journaux, puis exécuter
`notebooks/00_collecte_api.ipynb`.

```bash
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb pedagogie/*.ipynb
uv sync --group local && uv run --group local python scripts/mesure_inference_locale.py 2   # modèle en local (CPU)
```

Le groupe `local` installe `torch` en version CPU : disponible pour Linux, Windows et les Mac à puce Apple, pas pour
les Mac Intel.

Régénérer la présentation : voir [presentation/README.md](presentation/README.md).

## Organisation

```text
├── PLAN.md                 protocole figé avant le premier appel (relu par le statisticien)
├── src/segvet/             io (téléchargement + SHA-256), api (client robuste), masks, cache, metrics,
│                           evaluation (vue fusionnée, bootstrap, règle de décision), cost, local, viz
├── tests/                  tests sur une fausse API et des matrices construites à la main
├── notebooks/              00_collecte_api (seul notebook qui appelle l'API) · corrigé
├── pedagogie/              01 environnement · 02 secret · 03 API · 04 client robuste · 05 images et masques
│                           06 IoU et Dice · 07 valider un modèle · 08 du chronomètre au budget
├── kit-mentor/             séances, questions, erreurs, grille, bilan
├── presentation/           livrable 2 (.pptx généré, même trame que le support OpenClassrooms)
├── site/                   page interactive pour les apprenants
├── scripts/                mesure de l'inférence locale
├── data/processed/         prédictions de l'API en cache (3 variantes d'envoi), journaux d'appels, réponse brute d'exemple
└── data/raw/               données brutes (non versionnées, téléchargées et vérifiées automatiquement)
```

## Ce qui a changé par rapport au plan

| Plan | Réalité | Pourquoi |
|---|---|---|
| 2 variantes d'envoi : JPEG 512 et PNG d'origine | 3 variantes : + JPEG pleine taille, en annexe | un bug du premier passage envoyait du JPEG pleine taille à la place du PNG ; gardée, elle isole l'effet de la résolution (c'est elle, pas la compression, qui coûte 0,005 d'IoU) |
| Une collecte | deux collectes, la seconde fait foi | le premier journal comptait l'attente du limiteur de débit dans la latence (pics de 36 s) ; bug corrigé avec un test, tout recollecté ; prédictions identiques au pixel près entre les deux passages. Le journal fautif est gardé comme contre-exemple (fiche 8) |
| Coût A : temps de calcul × prix du matériel | facture réelle extrapolée : < 0,01 $ pour 301 requêtes → < 17 $ | Hugging Face ne publie ni prix par seconde pour hf-inference, ni temps de calcul dans les réponses ; c'est un majorant, valable si la facturation est linéaire |
| Inférence locale : hors corrigé | utilisée pour l'hypothèse de débit des scénarios B et B' (0,90 s par image sur 2 cœurs, doublée par prudence) | le débit d'une machine dédiée ne se déduit pas de la latence de l'API |
| Équivalence JPEG / PNG : IC apparié dans ±0,01 | conclue avec la graine du plan, mais à la limite : selon la graine, la borne basse va de −0,0096 à −0,0102 | la conclusion retenue est « perte d'environ 0,005, petite et probablement réelle » plutôt qu'une équivalence franche |
| — | vérification de la fuite de données (masques comparés aux 17 706 du jeu d'affinage) | découverte pendant l'exploration ; elle a fixé la formulation « estimation optimiste » avant les résultats |

## Limites

- **50 images, toutes déjà vues par le modèle** : le seul vrai test serait un jeu de photos ModeTrends nouvelles,
  annotées et découpées par influenceur.
- **Annotation ambiguë** : robe, tunique, short… les deux pires images sont des désaccords de définition.
- **Gauche et droite** : le modèle les confond souvent ; le corrigé les fusionne (sans importance pour une marque).
- **Prix** : lus le 24 octobre 2026 ; le majorant serverless repose sur un affichage arrondi au centime.
- **Photos de personnes réelles** : visages floutés dans toutes les figures versionnées.
