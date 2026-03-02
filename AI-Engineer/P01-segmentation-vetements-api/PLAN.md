# PLAN — P01 AI Engineer « Requêtez des services IA »

Plan figé **avant** le premier appel à l'API (méthode : explorer → planifier → coder → vérifier → committer).
Les écarts constatés pendant la réalisation sont consignés dans le README, section « Ce qui a changé par rapport au plan ».

## Question métier

Une agence de marketing de mode veut repérer automatiquement les vêtements portés sur des photos d'influenceurs.
Première brique : la **segmentation** (quel pixel appartient à quel vêtement).
1. Le modèle pré-entraîné `sayeed99/segformer_b3_clothes`, appelé par l'API serverless de Hugging Face, segmente-t-il
   correctement les vêtements des 50 photos annotées fournies ?
2. Combien coûterait le traitement de **500 000 images en 30 jours** ?

## Ce que l'exploration a déjà établi

- 50 images RGB (46 en 400 × 600 px) et 50 masques annotés en niveaux de gris, 18 classes (0 = fond … 17 = écharpe),
  numérotées comme les labels du modèle. Toutes les classes apparaissent au moins une fois ; l'écharpe dans 3 images.
- Le modèle redimensionne toute image en 512 × 512 avant de la traiter. Le fond occupe 78,4 % des pixels annotés.
- Une image fait 97 × 412 px (les autres de 397 à 400 px de large) : à regarder avant de conclure sur elle.
- Adresse de l'API : `https://router.huggingface.co/hf-inference/models/sayeed99/segformer_b3_clothes`
  (l'adresse `api-inference.huggingface.co` du notebook d'origine n'est plus en service).
- Annotation : « gauche » = gauche de la personne (bras gauche du côté droit de l'image dans 42 images sur 42).
- **Fuite de données** : les 50 images et leurs 50 masques figurent à l'identique dans
  `mattmdjaga/human_parsing_dataset` (ATR, 17 706 images), le jeu sur lequel le modèle a été affiné. Le code
  d'entraînement publié par l'auteur de la famille de modèles ne réserve que 0,6 % des images au test.

## Protocole (fixé avant de voir les résultats)

| Décision | Choix | Justification |
|---|---|---|
| Image envoyée | JPEG qualité 90, plus grand côté ≤ 512 px | Le modèle travaille en 512 × 512 : envoyer plus grand alourdit la requête sans rien apporter |
| Comparaison | Masque prédit ramené à la taille de l'annotation (plus proche voisin), comparaison pixel à pixel | On évalue dans le repère de la vérité terrain, sans inventer de classes intermédiaires |
| Métrique principale | **IoU par classe**, calculé sur la matrice de confusion cumulée sur les 50 images | IoU = métrique standard en segmentation ; le cumul évite qu'une classe présente sur 20 pixels d'une image pèse autant qu'une classe de 30 000 pixels |
| **Métrique principale (unique)** | **mIoU vêtements** : moyenne des IoU des 9 familles de vêtements vues dans au moins 5 images, en vue fusionnée (chapeau, lunettes, haut, jupe, pantalon, robe, ceinture, chaussures gauche + droite, sac) | Ce qui intéresse le métier, ce sont les vêtements ; un seul chiffre principal évite de choisir après coup celui qui arrange |
| Annexes | mIoU 18 classes, IoU par classe des 18 classes, écharpe (3 images) publiée à part avec ses effectifs | Transparence sans multiplier les chiffres « principaux » |
| Seconde métrique | Dice (= F1 au niveau pixel) par classe | Demandé par l'énoncé ; lié à l'IoU (Dice = 2 IoU / (1 + IoU)), donc même classement |
| Fusion gauche / droite | Chaussures, bras et jambes : on **somme** les lignes et colonnes de la matrice de confusion (on ne moyenne pas deux IoU) | Une marque se moque de savoir quelle chaussure est la gauche ; une inversion gauche/droite n'est pas une erreur de vêtement |
| Métrique écartée | Exactitude par pixel : affichée une fois, comme contre-exemple | Le fond occupe 78 % des pixels : un modèle qui ne prédit que du fond aurait déjà une exactitude de 0,78 |
| Classes absentes | IoU non défini si la classe n'est ni dans la vérité ni dans la prédiction (exclu de la moyenne) ; IoU = 0 si elle est prédite sans être présente | Une « hallucination » doit coûter, une absence partout ne doit rien changer |
| Incertitude | Intervalle bootstrap percentile à 95 % : on tire 50 images avec remise, on recalcule la matrice cumulée (2 000 tirages, graine 0) ; part des tirages où une classe disparaît publiée | 50 images seulement : un chiffre sans intervalle surinterprète. L'intervalle ne couvre que la variabilité des 50 images, ni la fuite de données ni le changement de type de photos |
| Classes rares | Chaque IoU est publié avec le nombre d'images où la classe est présente ; sous 5 images, la classe sort du mIoU principal | L'écharpe (3 images) pèserait autant que le haut (41 images) |
| Par image (diagnostic seulement) | mIoU vêtements par image, vue fusionnée, sur les classes présentes dans la vérité ou la prédiction | Montre la variabilité et sert à choisir les exemples visuels (meilleur, médian, pire) ; trop sensible aux petites zones pour servir de métrique |
| Fuite de données | Formulation imposée : « performance sur des images vues à l'entraînement : estimation optimiste, qui ne mesure pas la généralisation ». Comparaison avec la fiche du modèle **qualitative** seulement | Avec 0,6 % de test, on attend 0,3 image sur 50 hors entraînement. Un score supérieur à la fiche du modèle serait compatible avec de la mémorisation et ne prouverait rien |
| **Règle de décision (arbitraire, fixée avant)** | « Non disqualifié pour un pilote » si la borne basse de l'IC du mIoU vêtements ≥ 0,60 **et** si haut, pantalon, robe, jupe et chaussures ont chacun un IoU ≥ 0,50 ; sinon « insuffisant ». Le mot « convient » est interdit sans test sur des images nouvelles | Avec la fuite, un mauvais score est informatif (échec même sur des images connues), un bon score ne l'est pas |
| Train / val / test | Pas d'entraînement ici : les 50 images sont un test. Protocole proposé pour la suite : images ModeTrends nouvelles, découpage **par influenceur** (70 / 15 / 15), test verrouillé jusqu'à la fin | Découper par personne évite qu'une même tenue soit en entraînement et en test |
| Optimisation | Sensibilité appariée : chaque image est aussi envoyée en PNG d'origine, en alternant l'ordre JPEG / PNG d'une image à l'autre. Δ mIoU vêtements par bootstrap apparié (mêmes tirages) ; marge d'équivalence fixée à \|Δ\| < 0,01 ; on compare aussi octets envoyés et latence | Vérifie que « JPEG 512 » ne coûte pas en qualité ; la conclusion porte sur ce réglage, pas sur « la compression » en général (résolution et compression changent ensemble) |
| Robustesse client | Timeout 30 s, au plus 30 requêtes par minute, 4 nouvelles tentatives sur 429 / 5xx / timeout (attente 2, 4, 8, 16 s ou `Retry-After`), arrêt immédiat sur 401 / 402 / 403 / 404 | Critères de la grille ; réessayer une erreur d'authentification ne sert à rien |
| Reproductibilité | Réponses de l'API mises en cache dans `data/processed/` (masques PNG + journal des appels) ; les notebooks relisent le cache | Les notebooks se ré-exécutent sans token et donnent toujours les mêmes chiffres |
| Coût, scénario A | Serverless : 500 000 × temps de calcul par image × prix du matériel. Temps : en-tête de l'API s'il existe, sinon latence médiane mesurée (qui majore le temps facturé). Médiane et 95ᵉ centile publiés hors appels retentés, ceux-ci comptés à part | Mode de facturation de hf-inference ; la latence client inclut réseau, file d'attente et démarrages à froid |
| Coût, scénario B | Endpoint dédié allumé en continu : 720 h × prix horaire. Le débit d'une instance dédiée est une **hypothèse** (il ne se déduit pas de la latence serverless) | Au-delà d'un certain volume, payer la machine coûte moins cher que payer à la requête |
| Coût, scénario B' | Même endpoint, traitement par lots quelques heures par jour avec mise à l'arrêt automatique ; heures nécessaires = 500 000 × temps par image / 3 600 | Le besoin moyen (500 000 / 30 j ≈ 11,6 images par minute) ne justifie pas une machine allumée 720 h |
| Prix | Grille tarifaire Hugging Face lue le 2026-10-24, citée avec sa date | Les prix changent |

## Livrables et emplacement

| Livrable | Chemin | Preuve que c'est fini |
|---|---|---|
| Corrigé — notebook (livrable 1) | `notebooks/segmentation_vetements_corrige.ipynb` | Exécuté de bout en bout sans token, à partir du cache |
| Corrigé — présentation (livrable 2) | `presentation/` (.pptx généré par script, même trame que le support fourni, sans le copier) | Schéma validé, texte extrait relu, contrôle visuel par le mentor |
| Corrigé — environnement | `pyproject.toml` + `uv.lock` + `.env.example` | `uv sync --frozen` puis `uv run pytest` |
| Collecte des réponses | `notebooks/00_collecte_api.ipynb` (seul notebook qui appelle l'API) | Journal des 100 appels dans `data/processed/` |
| Code réutilisable | `src/segvet/` + `tests/` | `uv run pytest` vert, aucun appel réseau dans les tests |
| Notebooks pédagogiques | `pedagogie/` (8 fiches) | Exécutés, sorties versionnées |
| Kit mentor | `kit-mentor/` | Relu par le pédagogue |
| Page interactive | `site/index.html` → artifact | `node --check`, capture Chrome headless clair et sombre |
| Aller plus loin | `ALLER_PLUS_LOIN.md` | Relu par l'expert data engineering |

## Vérifications

- **Code** : tests sur une fausse session HTTP (codes 200, 401, 429, 503, timeout), sur le limiteur de débit (jamais
  plus de N appels sur une minute glissante), sur des matrices de confusion construites à la main.
- **Données** : SHA-256 du zip ; appariement image / masque vérifié ; tailles identiques image / masque.
- **Résultats** : IoU recalculé indépendamment par le statisticien sur 2 ou 3 images ; cohérence Dice ↔ IoU.
- **Confidentialité** : aucun token dans le code ni dans les sorties ; `.env` gitignoré ; visages floutés dans
  les figures versionnées (photos de personnes réelles).

## Hors périmètre

Pas d'entraînement ni d'affinage du modèle ; pas d'analyse stylistique ni d'agrégation de tendances (fonctionnalités 2
et 3 du projet ModeTrends) ; pas d'images collectées sur les réseaux sociaux. L'inférence locale avec `transformers`
est décrite dans « aller plus loin », pas dans le corrigé.
