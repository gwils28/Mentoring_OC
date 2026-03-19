# Déroulé des séances

Le projet tient en quatre gestes, dans cet ordre : **s'installer** (environnement, token), **appeler** (une image,
puis 50, sans planter), **mesurer** (voir, puis compter), **chiffrer** (temps par image → budget). Les deux premiers
sont rapides pour un apprenant qui code déjà ; les deux derniers font la différence au bilan.

## Temps plein (≈ 2 semaines) : 2 séances + bilan

### Séance 1 — Démarrage (fin de la 1ʳᵉ semaine) · 45 min

| Minutes | Contenu | Support |
|---|---|---|
| 0–5 | Où en es-tu ? Cours suivis, environnement installé ? | — |
| 5–15 | Reformuler le brief : **deux** questions (le modèle segmente-t-il bien ? combien coûte le passage à 500 000 images ?) et **deux** livrables | brief OpenClassrooms |
| 15–25 | Vérifier en direct : `sys.executable`, versions installées, `.env` présent **et** ignoré par git (`git check-ignore .env`) | fiches 1 et 2 |
| 25–35 | Prévenir : adresse de l'API périmée dans le notebook fourni, crédits (402), premier appel sur **une** image | fiche 3 |
| 35–45 | Objectif de la séance 2 : les 50 images traitées, une figure avant / après | — |

### Séance 2 — Robustesse et mesure (milieu de la 2ᵉ semaine) · 45 min

| Minutes | Contenu | Support |
|---|---|---|
| 0–10 | Montrer la boucle sur 50 images : timeout ? pause entre les appels ? que se passe-t-il si la 30ᵉ échoue ? | fiche 4 |
| 10–20 | Regarder ensemble 3 figures avant / après : couleurs cohérentes ? légende ? masques à la bonne taille ? | fiche 5 |
| 20–35 | Passer du « ça a l'air bien » à un chiffre : IoU, Dice, pourquoi pas l'exactitude par pixel | fiche 6 |
| 35–40 | Train / validation / test, et la question « ces images, le modèle les a-t-il déjà vues ? » | fiche 7 |
| 40–45 | Préparer le chiffrage : quelles données mesurer **maintenant** (temps par image, poids envoyé) pour le budget | fiche 8 |

### Bilan (semaine suivante) · 45 min → [05_trame_bilan.md](05_trame_bilan.md)

## Alternance (≈ 4 semaines) : 4 séances + bilan

| Séance | Semaine | Thème | Fiches |
|---|---|---|---|
| 1 | 1 | Brief, environnement, token sécurisé | 1, 2 |
| 2 | 2 | Premier appel, lecture de la réponse (JSON, base64), passage à 50 images | 3, 4 |
| 3 | 3 | Visualisation avant / après, métriques IoU et Dice | 5, 6 |
| 4 | 4 | Méthode de validation (train / val / test), chiffrage, préparation de la présentation | 7, 8 |
| Bilan | 5 | Autoévaluation, difficultés, points forts, suite | — |

## Adapter au profil

- **Débute en Python** : viser un notebook propre et un appel qui marche ; le client robuste peut rester simple
  (timeout + pause fixe entre deux appels). Fiches 1, 3 et 5 en séance. Le guide OpenClassrooms insiste : montrer
  **comment on cherche** (lire l'erreur, la documentation Hugging Face, la réponse JSON) plutôt que donner la
  solution.
- **Développeur à l'aise** : exiger la qualité (fonctions, gestion des codes HTTP, tests), proposer l'inférence
  locale et la question de la fuite de données ([ALLER_PLUS_LOIN.md](../ALLER_PLUS_LOIN.md)).
- **Bloqué par les crédits** : faire tourner le modèle en local (même modèle ; dans le corrigé, au moins 99,98 % des
  pixels identiques à ceux de l'API, voir `data/processed/mesure_inference_locale.json`) ; l'appel à l'API reste écrit dans le notebook, avec la réponse 402 expliquée.
