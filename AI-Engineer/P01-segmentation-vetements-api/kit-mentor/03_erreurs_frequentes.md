# Erreurs fréquentes : diagnostic et remédiation

La plupart des blocages de ce projet arrivent **avant** le premier masque : environnement, token, adresse de l'API,
crédits. Demander d'afficher le **code de réponse** HTTP (`response.status_code`) et le **texte** de l'erreur
résout la moitié des cas en une minute.

| # | Erreur | Comment la repérer | Pourquoi c'est un problème | Remédiation |
|---|---|---|---|---|
| 1 | `ModuleNotFoundError` dans Jupyter alors que « c'est installé » | l'import marche dans le terminal, pas dans le notebook | Jupyter utilise un autre Python | `print(sys.executable)`, installer dans cet environnement, ou choisir le bon noyau (fiche 1 § 2) |
| 2 | Token écrit dans le code | `api_token = "hf_…"` dans une cellule | il part sur GitHub au premier commit | `.env` + `python-dotenv` + `.gitignore` (fiche 2) |
| 3 | Token visible dans une **sortie** de notebook | `print(token)` ou un dictionnaire d'en-têtes affiché | les sorties sont enregistrées dans le `.ipynb` | effacer la sortie, **révoquer** le token, `git grep "hf_"` avant chaque commit (fiche 2, piège) |
| 4 | `.env` committé malgré tout | `git ls-files` liste `.env` | `.gitignore` ajouté **après** le premier commit du fichier | `git rm --cached .env`, révoquer le token |
| 5 | Adresse de l'API périmée | erreur de connexion ou 404 avec `api-inference.huggingface.co` | adresse remplacée en 2025 | `https://router.huggingface.co/hf-inference/models/sayeed99/segformer_b3_clothes` (fiche 3) |
| 6 | Réponse 402 | `Payment Required` | compte sans crédits d'inférence | acheter quelques crédits, compte PRO, ou modèle en local ([ALLER_PLUS_LOIN.md](../ALLER_PLUS_LOIN.md) § 1) |
| 7 | Réponse 401 ou 403 | `Unauthorized` / `Forbidden` | token mal copié, ou sans le droit « Inference Providers » | recréer le token avec ce droit ; tester avec `whoami` (fiche 2 § 4) |
| 8 | Image ouverte en mode texte | `UnicodeDecodeError` | une image se lit en octets | `open(chemin, "rb")` (fiche 3, piège) |
| 9 | Mauvais `Content-Type` | 400 ou réponse vide | PNG envoyé avec `image/jpeg` (ou l'inverse) | aligner l'en-tête sur le format réellement envoyé |
| 10 | Pas de `timeout` | le notebook reste figé sur une image | `requests` attend indéfiniment par défaut | `requests.post(..., timeout=30)` (fiche 4) |
| 11 | Boucle qui plante à la 30ᵉ image | exception non rattrapée, résultats perdus | une erreur passagère arrête tout | `try/except` par image, journal des échecs, relancer les manquantes (fiche 4) |
| 12 | Réessayer une 401 en boucle | le script « tourne » sans fin ou longtemps | une erreur d'identité ne se corrige pas en attendant | réessayer seulement 429, 5xx, timeout (fiche 4, piège) |
| 13 | Pas de pause entre les appels | 429 en série sur 50 images | quota dépassé | `time.sleep` ou limiteur N requêtes par minute (fiche 4 § 4) |
| 14 | Masques redimensionnés en bilinéaire | des classes « fantômes » sur les contours | l'interpolation invente des valeurs intermédiaires | `Image.NEAREST` (fiche 5, piège) |
| 15 | Largeur et hauteur inversées | masque déformé ou `ValueError` de forme | Pillow `size` = (l, h), NumPy `shape` = (h, l) | fiche 5 § 1 |
| 16 | Label inconnu rangé en silence dans le fond | `CLASS_MAPPING.get(label, 0)` du notebook fourni | une classe mal orthographiée disparaît sans erreur | lever une erreur sur un label inconnu |
| 17 | Couleurs différentes d'une figure à l'autre | le haut est bleu ici, vert là | `cmap` recalculé sur les classes présentes | une table de couleurs fixe pour les 18 classes (fiche 5 § 2) |
| 18 | « 96 % de précision » comme seule mesure | exactitude par pixel annoncée | le fond fait 78 % des pixels | IoU par classe (fiche 6, piège) |
| 19 | Moyenne d'IoU où les classes absentes comptent 0 | mIoU anormalement bas | une classe absente de l'image n'est ni réussie ni ratée | classe absente = pas de score (`NaN`) ; inventée = 0 (fiche 6 § 2) |
| 20 | Train / val / test « découpés » sur les 50 images pour un modèle qu'on n'entraîne pas | jeux d'entraînement inutilisés | rien n'est entraîné : tout est du test | expliquer la méthode pour un futur affinage, sur des images nouvelles, découpées par personne (fiche 7) |
| 21 | Score présenté comme « le modèle marche sur nos photos » | conclusion sans réserve | les 50 images font partie des données d'entraînement du modèle | « estimation optimiste » (fiche 7, piège) |
| 22 | Budget sans calcul ni source | « environ 100 € » | invérifiable | volume × temps × prix, prix datés et sourcés (fiche 8) |
| 23 | Images × prix horaire | budget de 35 000 $ | unités mélangées | passer par les heures de machine (fiche 8, piège) |
| 24 | Latence qui compte les pauses | latences de 30 s isolées | le chronomètre englobe le `sleep` | chronométrer seulement la requête (fiche 8, piège) |

## Profils

- **Découvre la programmation** : avancer par petites victoires (un appel, une image, une figure). Fiches 1, 3 et 5
  en séance ; la fiche 4 peut se limiter au timeout et à une pause fixe.
- **Développeur expérimenté** : le script sera vite fait. Exiger la gestion des codes HTTP, des fonctions testées,
  une évaluation chiffrée avec sa limite (fuite de données) et proposer l'inférence locale.
- **Data scientist en reconversion** : à l'aise sur les métriques, souvent moins sur les secrets et les erreurs
  réseau. Insister sur les fiches 2 et 4.
