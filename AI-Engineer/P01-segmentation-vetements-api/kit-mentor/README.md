# Kit mentor — P01 AI Engineer « Requêtez des services IA »

Le **premier projet** du parcours, souvent le premier contact de l'apprenant avec une API et un modèle
pré-entraîné. Le script attendu est court (20 à 30 lignes selon le guide OpenClassrooms) ; la valeur du projet est
ailleurs : **garder le token secret**, **écrire un appel qui résiste aux erreurs**, **mesurer** la qualité au lieu de
l'admirer, et **chiffrer** un passage à l'échelle. Le piège caché du projet : les 50 images de test font partie des
données d'entraînement du modèle (voir « Ce qu'il faut savoir avant la 1ʳᵉ séance »).

| Quand | Fichier | Pour quoi faire |
|---|---|---|
| Avant la 1ʳᵉ séance | [01_deroule_des_seances.md](01_deroule_des_seances.md) | planifier les séances (temps plein ou alternance) |
| Pendant les séances | [02_questions_oral.md](02_questions_oral.md) | questions à poser, réponses attendues, relances |
| Quand ça coince | [03_erreurs_frequentes.md](03_erreurs_frequentes.md) | diagnostiquer : token, URL, crédits, masques, métriques |
| À la réception des livrables | [04_grille_evaluation.md](04_grille_evaluation.md) | vérifier chaque critère, avec renvoi au corrigé |
| Séance bilan | [05_trame_bilan.md](05_trame_bilan.md) | déroulé du bilan et trame de compte-rendu |

## Repères

- **Charge** : 40 h supervisées et 40 h personnelles. Temps plein : un peu plus de 2 semaines, 2 séances puis le
  bilan. Alternance : un peu plus de 4 semaines, 4 séances puis le bilan.
- **Pas de soutenance** : projet d'entraînement, validé par le mentor en séance bilan. Rien de critique → on ne
  bloque pas le passage au projet suivant.
- **Livrables de l'apprenant** : un notebook (réponses de l'API + visualisations) et une présentation complétée à
  partir du modèle fourni par OpenClassrooms (8 slides, la 7ᵉ sur la conformité est optionnelle).
- **Outils** : Python, `requests`, Pillow, Matplotlib, NumPy, `python-dotenv` ; un compte Hugging Face.
- **Variante pour les plus à l'aise** (prévue par le guide) : faire tourner le modèle en local avec `transformers`
  (voir [ALLER_PLUS_LOIN.md](../ALLER_PLUS_LOIN.md) § 1).

## Ce qu'il faut savoir avant la 1ʳᵉ séance

1. **L'adresse de l'API du notebook fourni est périmée.** `api-inference.huggingface.co/models/...` ne répond plus
   depuis 2025 ; l'adresse actuelle est
   `https://router.huggingface.co/hf-inference/models/sayeed99/segformer_b3_clothes` (vérifiée en octobre 2026). Le
   dire dès la séance 1 évite une heure de recherche inutile.
2. **Les crédits.** Un compte Hugging Face gratuit n'a pas de crédits d'inférence inclus ; le compte PRO en a 2 $
   par mois ([grille des Inference Providers](https://huggingface.co/docs/inference-providers/pricing), lue le
   24 octobre 2026 ; elle change souvent). Sans crédits, l'API répond **402**. Le projet coûte quelques centimes : en pratique,
   moins de 0,01 $ pour 301 appels. Plan B sans crédits : le modèle en local (même résultat, voir ci-dessous).
3. **La fuite de données.** Les 50 images et masques fournis se retrouvent **à l'identique** dans le jeu public sur
   lequel le modèle a été affiné (ATR, 17 706 images). Le score obtenu par l'apprenant est donc optimiste et ne
   mesure pas la généralisation. Ce n'est pas une faute de l'apprenant : c'est une question de bilan pour ceux qui
   sont à l'aise (« ce chiffre prouve-t-il que le modèle marchera sur les photos de ModeTrends ? »). La fiche 7 le
   démontre.
4. **Photos de personnes réelles** : bon réflexe à valoriser, flouter les visages dans ce qui est publié (slide 7,
   RGPD).

## Ressources du dossier

| Ressource | Usage |
|---|---|
| [Corrigé](../notebooks/segmentation_vetements_corrige.ipynb) | pour **comparer** les chiffres ; ne pas le transmettre avant le bilan |
| [Collecte des réponses](../notebooks/00_collecte_api.ipynb) | le seul notebook qui appelle l'API (avec token) |
| [Package `segvet`](../src/segvet/) | client robuste (`api.py`), métriques (`metrics.py`), évaluation, chiffrage |
| [Présentation du corrigé](../presentation/) | même trame que le modèle OpenClassrooms, à montrer **après** le bilan |
| [Fiches pédagogiques](../pedagogie/) | 8 fiches, une notion chacune, exécutables **sans token** |
| [Page interactive](../site/index.html) | à partager aux apprenants : étapes, labos IoU et budget, quiz |
| [Aller plus loin](../ALLER_PLUS_LOIN.md) | inférence locale, endpoint dédié, modèles récents, AI Act |

**Quand donner quoi** : fiches 1 et 2 dès la séance 1 (environnement, token), fiches 3 et 4 pendant le script,
fiche 5 pour la visualisation, fiches 6 à 8 avant l'évaluation et le chiffrage. Aucune fiche ne contient le script
complet du projet ni ses résultats chiffrés (les fiches 6 et 8 calculent sur d'autres données ou des prix d'exemple).
Seule exception : la **fiche 7 révèle la fuite de données**. Si vous comptez en faire la question bonus du bilan,
donnez-la après que l'apprenant a présenté son évaluation. Le corrigé est public (dépôt GitHub) : le dire à l'apprenant et lui demander de ne pas l'ouvrir
avant le bilan.

## Chiffres de référence (corrigé)

Les chiffres de l'apprenant peuvent différer selon ses choix (taille d'envoi, métrique, gauche et droite séparées
ou non) ; un écart **expliqué** est acceptable, un écart qu'il ne sait pas expliquer mérite une question.

| Élément | Valeur du corrigé | Variante acceptable |
|---|---|---|
| Données | 50 images (46 en 400 × 600 px) et 50 masques, 18 classes ; fond = 78 % des pixels | — |
| Appels | 50 / 50 réussis par variante d'envoi, aucune nouvelle tentative nécessaire | quelques 503 au démarrage, gérés |
| Poids envoyé | JPEG 512 px : 53 Ko (médiane) ; PNG d'origine : 426 Ko | PNG d'origine accepté si l'apprenant le justifie |
| Latence | 0,71 s en médiane, 1,24 s au 95ᵉ centile (JPEG 512) | de l'ordre de la seconde ; dépend du réseau |
| Exactitude par pixel | 0,96 (un « modèle » tout en fond : 0,78) | — |
| **mIoU vêtements** (9 familles, gauche + droite fusionnées) | **0,79** (IC 95 % : 0,76 – 0,82) | moyenne des IoU par image : 0,75 |
| mIoU 18 classes | 0,65 (gauche et droite comptées à part) | plus bas si l'écharpe ou les petites classes pèsent |
| IoU par famille | jupe 0,94 · pantalon 0,90 · haut 0,88 · chapeau 0,85 · robe 0,80 · chaussures 0,75 · sac 0,73 · lunettes 0,70 · ceinture 0,57 | — |
| JPEG 512 vs PNG | Δ mIoU = −0,005 (perte minime, due à la résolution) ; JPEG 8 fois plus léger | — |
| Coût, 500 000 images / 30 j | serverless < 17 $ (majorant mesuré) · CPU dédié 24 h/24 ≈ 50 $ · CPU par lots ≈ 18 $ · GPU T4 24 h/24 = 360 $ | tout budget dont l'apprenant sait refaire la multiplication |
| Débit nécessaire | 11,6 images par minute | — |
