# Grille d'évaluation commentée

Grille de travail du mentor, reformulée et regroupée par compétence. Cocher à la lecture des livrables.

Légende : 🟢 acquis · 🟠 à consolider (on en parle au bilan, non bloquant) · 🔴 bloquant (à corriger avant validation)

Rappel : projet d'entraînement, pas de soutenance. Un 🔴 se corrige avant le bilan ; plusieurs 🟠 ne bloquent pas le
passage au projet suivant.

## A. Configurer l'environnement de travail

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Environnement reproductible | environnement virtuel + fichier de dépendances (requirements.txt, pyproject) avec requests, Pillow, Matplotlib, NumPy | `pyproject.toml`, `uv.lock`, corrigé § 1 |
| ☐ | Token sécurisé | lu depuis `.env` avec python-dotenv ; `.env` dans `.gitignore` ; aucun `hf_` dans le code **ni dans les sorties** | `.env.example`, corrigé § 2, fiche 2 |
| ☐ | Code propre | fonctions nommées, commentaires utiles, pas de code mort ni de chemins absolus d'une autre machine | `src/segvet/api.py` |
| ☐ | Notebook structuré | une section par étape du projet, titre et phrase de conclusion par section | corrigé (plan en tête) |

**Token** : 🟢 `.env` + `.gitignore` + jamais affiché ; 🟠 `.env` correct mais token affiché une fois dans une
sortie effacée depuis (vérifier qu'il l'a révoqué) ; 🔴 token en clair dans le code ou dans le dépôt.

## B. Choisir et configurer un modèle pré-entraîné

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Accès à l'API | appels réussis vers `segformer_b3_clothes` à l'adresse actuelle ; réponses exploitées pour les 50 images | corrigé § 4, `notebooks/00_collecte_api.ipynb` |
| ☐ | Timeout | une valeur explicite par requête | `SegformerClient(timeout=30)` |
| ☐ | Limite de débit | pause ou plafond de N requêtes par minute, justifié | `RateLimiter`, fiche 4 |
| ☐ | Erreurs | les erreurs passagères (429, 503, timeout) sont réessayées ; les autres arrêtent avec un message ; une image en échec ne fait pas perdre les autres | corrigé § 4.2, fiche 4 |
| ☐ | Images optimisées | taille réduite et format compatible, choix expliqué | corrigé § 6.5 |
| ☐ | Visualisation avant / après | image originale et segmentation côte à côte, couleurs constantes, légende | corrigé § 5, fiche 5 |

**Gestion des erreurs** : 🟢 timeout + limite + nouvelles tentatives ciblées ; 🟠 timeout et pause fixe sans
distinguer les codes HTTP ; 🔴 aucun timeout ni pause, ou boucle qui plante sur la première erreur.

**Visualisation** : 🟢 photo / annotation / prédiction avec la même palette ; 🟠 avant / après sans l'annotation
(on ne peut pas juger) ; 🔴 masques déformés ou sans légende.

## C. Simplifier et synthétiser (présentation)

| ✓ | Critère | Ce qu'on vérifie | Corrigé |
|---|---|---|---|
| ☐ | Métrique pertinente | IoU ou Dice par classe ; l'exactitude par pixel n'est pas la seule mesure | corrigé § 6.2, fiche 6 |
| ☐ | Rapport de performance | un chiffre de synthèse, les points forts et faibles par vêtement, des exemples réussis et ratés | corrigé § 6, rubrique « performances » (slides 4-5 du corrigé) |
| ☐ | Méthode de validation | rôle de train / val / test, et ce qu'ils deviennent ici (pas d'entraînement : test seul) | corrigé § 7, fiche 7 |
| ☐ | Budget 500 000 images / 30 j | un chiffre, son calcul, ses hypothèses et la source des prix | corrigé § 8, fiche 8 |
| ☐ | Passage à l'échelle | débit nécessaire, payer à l'usage ou louer une machine | corrigé § 8, rubrique « passage à l'échelle » (slide 7 du corrigé) |
| ☐ | Synthèse | un public non technique comprend la conclusion en une slide | rubrique « bilan » (slide 9 du corrigé) |

**Budget** : 🟢 calcul explicite et sourcé, au moins deux façons de payer ; 🟠 un seul chiffre bien calculé mais sans
source ; 🔴 aucun budget, ou un budget sans calcul.

**Évaluation** : 🟢 IoU/Dice par classe + limite de l'évaluation (50 images, déjà vues par le modèle) ; 🟠 IoU global
sans détail par vêtement ; 🔴 aucune mesure chiffrée, seulement des figures.

## Bonus (ne compte pas, se valorise au bilan)

- Fuite de données repérée (les 50 images sont dans le jeu d'entraînement du modèle).
- Modèle testé en local avec `transformers`, comparé à l'API.
- Rubrique conformité (slide 7 du modèle, optionnelle ; slide 8 du corrigé) traitée : RGPD (photos de personnes, minimisation, floutage) et AI Act.
