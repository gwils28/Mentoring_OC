# Aller plus loin — appeler un modèle d'IA en production

Le projet fait le strict nécessaire : un client HTTP robuste, 50 images, une évaluation et un chiffrage. Voici ce
qu'on ajoute dans un projet réel, avec, pour chaque piste, une commande pour l'essayer depuis ce dossier.

## 1. Faire tourner le modèle chez soi (prévu par le guide OpenClassrooms pour les plus à l'aise)

Le même modèle se télécharge et s'exécute en local avec `transformers`. Dans ce projet, c'est un groupe de
dépendances optionnel (`torch` en version CPU, pour ne pas télécharger CUDA) :

```bash
uv sync --group local
uv run --group local python scripts/mesure_inference_locale.py 2     # 2 = nombre de cœurs utilisés
```

Mesure faite pour le corrigé (`data/processed/mesure_inference_locale.json`) : **0,90 s par image sur 2 cœurs**
(1,81 s sur un seul), et des masques identiques à ceux de l'API pour au moins 99,98 % des pixels. C'est un très fort
indice que l'API exécute bien ce modèle, et c'est le **plan B** d'un apprenant sans crédits d'inférence. Le code tient en
quelques lignes (`src/segvet/local.py`) : charger le préprocesseur et le modèle, prédire, agrandir les scores à la
taille de l'image, prendre la classe la plus probable par pixel.

**Quand préférer le local ?** Données sensibles qui ne doivent pas quitter l'entreprise, gros volumes réguliers,
besoin de maîtriser la version exacte du modèle. **Quand préférer l'API ?** Prototype, volume faible ou irrégulier,
pas de compétence d'exploitation dans l'équipe.

## 2. Le client officiel plutôt que `requests`

Hugging Face fournit un client Python qui connaît les adresses, l'authentification et le format des réponses
(`huggingface_hub`, installé avec le groupe `local` : lancer avec `uv run --group local python`) :

```python
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()                                              # copie HF_TOKEN du fichier .env dans l'environnement
client = InferenceClient(provider="hf-inference")          # lit HF_TOKEN dans l'environnement
masques = client.image_segmentation("data/raw/top_influenceurs_2024/IMG/image_0.png",
                                    model="sayeed99/segformer_b3_clothes")
print([(m.label, m.score) for m in masques])
```

Il ne remplace pas la réflexion sur les quotas et les erreurs, mais il évite de suivre soi-même les changements
d'adresse (comme celui de 2025 qui a cassé le notebook fourni). Écrire le client à la main, comme dans le projet,
reste le meilleur moyen de **comprendre** ce qu'il fait.

## 3. Des appels plus rapides : en parallèle, sans dépasser le quota

Notre client envoie une image à la fois : 0,71 s par image, soit environ 84 images par minute au mieux. Pour aller
plus vite, on lance plusieurs requêtes **en même temps**, en gardant un plafond :

- `concurrent.futures.ThreadPoolExecutor(max_workers=4)` autour de `client.segment` : le plus simple, mais notre
  `RateLimiter` n'est pas prévu pour plusieurs fils d'exécution (deux fils peuvent passer en même temps) : le
  protéger par un `threading.Lock` autour de `wait()` ;
- `httpx.AsyncClient` + `asyncio.Semaphore(4)` : appels asynchrones, utile au-delà de quelques dizaines en parallèle ;
- les bibliothèques `tenacity` (nouvelles tentatives déclaratives) et `aiolimiter` (limite de débit asynchrone)
  remplacent nos 40 lignes faites main.

Le limiteur reste indispensable : le quota du service ne change pas parce qu'on parallélise.

## 4. Passer à l'échelle : une machine dédiée qui s'éteint seule

À 500 000 images par mois, le corrigé compare le paiement à l'usage et la location d'une machine. Les
**Inference Endpoints** de Hugging Face déploient n'importe quel modèle du Hub sur une machine réservée (CPU ou GPU),
avec une option de **mise à l'arrêt automatique** après une période sans requête (*scale to zero*) : on ne paie que
les heures où des lots tournent, ce qui correspond au scénario B' du corrigé. Les grands clouds proposent
l'équivalent (AWS SageMaker, Google Vertex AI, Azure Machine Learning).

Pour un traitement **par lots** (pas de temps réel), on n'a même pas besoin d'API : un job planifié charge le
modèle, traite les images de la journée, écrit les masques et s'arrête (voir le parcours Data Engineer pour
l'orchestration).

## 5. Rendre l'inférence moins chère

- **Envoyer moins** : le corrigé l'a mesuré, un JPEG réduit à 512 px pèse 8 fois moins qu'un PNG pour une perte
  d'IoU minime (0,005).
- **Calculer moins** : exporter le modèle au format ONNX et le quantifier (poids en 8 bits) accélère souvent
  l'inférence sur CPU ; la bibliothèque `optimum` de Hugging Face exporte le modèle en une commande. L'export ONNX
  est désormais dans le paquet séparé `optimum-onnx`, qui exige `transformers` < 4.58 (incompatible avec le groupe
  `local`) : on le lance donc dans un environnement jetable
  (`uv run --no-project --with optimum-onnx optimum-cli export onnx --model sayeed99/segformer_b3_clothes
  --task semantic-segmentation onnx/`), puis on quantifie avec `onnxruntime`. À **re-mesurer** après coup : une
  quantification peut dégrader les objets fins comme la ceinture.
- **Traiter par paquets** : en local, passer 8 ou 16 images d'un coup au modèle exploite mieux le processeur ou le GPU.

## 6. Évaluer sans se tromper

- **Chercher les doublons** entre données d'entraînement et de test avant de conclure : le corrigé compare des
  empreintes exactes ; les empreintes *perceptuelles* (`imagehash`) retrouvent aussi les images recadrées ou
  recompressées.
- **Annoter un vrai jeu de test** avec des outils dédiés (CVAT, Label Studio), sur des photos représentatives,
  découpées **par personne**. Prévoir une consigne d'annotation écrite pour les cas ambigus (robe ou tunique ?
  short ou jupe ?) : les pires images du corrigé sont justement des cas ambigus.
- **Suivre la qualité dans le temps** : la mode change ; un modèle entraîné sur des photos d'il y a une dizaine d'années
  (le jeu ATR a été publié en 2015) peut se dégrader sur les tenues d'aujourd'hui. On ré-annote régulièrement un petit échantillon et on recalcule l'IoU.

## 7. Des modèles plus récents

| Famille | Idée | Intérêt ici |
|---|---|---|
| SegFormer (NVIDIA, 2021) | segmentation sémantique, classes fixes | le modèle du projet : léger, rapide, 18 classes |
| Mask2Former (Meta, 2022) | une seule architecture pour la segmentation sémantique, par instances et panoptique | distinguer **deux personnes** sur la même photo |
| SAM 2 (Meta, 2024) | segmente ce qu'on lui désigne (point, boîte) | contours très précis, mais ne nomme pas les vêtements |
| Détection à vocabulaire ouvert + SAM (ex. Grounding DINO + SAM) | on décrit en texte ce qu'on cherche (« veste en jean ») | des classes qui n'existent pas dans les 18 d'ATR |
| Sapiens (Meta, 2024) | modèles spécialisés sur le corps humain | découpage fin du corps, mais vêtements moins détaillés |

Le bon modèle est celui qui répond aux classes **dont ModeTrends a besoin** : la première étape d'un vrai projet est
d'écrire cette liste avec les équipes mode.

## 8. Secrets, conformité, traçabilité

- **Secrets** : en production, le token ne vit plus dans un `.env` mais dans un gestionnaire de secrets (GitHub
  Actions secrets, AWS Secrets Manager, HashiCorp Vault). Un contrôle avant chaque commit (`gitleaks`,
  `detect-secrets`, via `pre-commit`) bloque les fuites comme celle démontrée dans la fiche 2.
- **RGPD** : des photos de personnes sont des données personnelles. Minimisation (ne garder que les masques de
  vêtements), durée de conservation, et attention au lieu de traitement quand on envoie des images à un service
  hébergé. Une analyse d'impact (AIPD) est à mener avec le DPO avant la production.
- **AI Act** : entré en vigueur en août 2024, avec des obligations qui s'appliquent par étapes. Analyser des
  vêtements n'est pas, en soi, un usage à haut risque ; identifier des personnes à partir de leur image relève en
  revanche de règles strictes (biométrie). Ne jamais réutiliser la segmentation pour reconnaître les personnes.
- **Traçabilité** : noter pour chaque résultat la version exacte du modèle (le *commit* du dépôt Hugging Face),
  la date et les réglages d'envoi. Sans cela, deux mesures à six mois d'écart ne sont pas comparables.
