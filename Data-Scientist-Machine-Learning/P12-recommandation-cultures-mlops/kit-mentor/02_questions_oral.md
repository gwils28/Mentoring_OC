# Questions d'oral

Format : **question** → ce qu'on attend → 🚩 signal d'alerte → 🔁 relance si l'apprenant bloque.
Choisir 2 ou 3 questions par section. Laisser au moins 3 secondes de réflexion avant de relancer.

## 1. Données et fusion

**Une ligne de ton jeu consolidé, c'est quoi ?**
→ Un pays, une culture, une année ; clé vérifiée unique.
🚩 « Une observation » ; ou 28 242 lignes sans avoir vu les doublons.
🔁 « Combien de fois trouves-tu le blé indien de 2000 dans `yield_df.csv` ? »

**Comment as-tu fusionné les deux jeux ?**
→ Constat qu'il n'y a ni pays ni année dans le jeu synthétique ; fusion par culture testée et jugée sans intérêt
(colonnes constantes), ou usage séparé ; la vraie fusion est celle des fichiers FAO entre eux.
🚩 Des pays attribués aux régions « North / South… », ou une jointure par culture qui ajoute des colonnes constantes
présentées comme des « variables enrichies ».
🔁 « Montre-moi les valeurs de la colonne que la fusion a ajoutée, culture par culture. »

**As-tu perdu des pays en route ?**
→ Oui, à chaque jointure ; nombre de lignes avant / après ; noms harmonisés pour récupérer les États-Unis, la Russie…
🔁 « Les États-Unis sont-ils dans ta table finale ? »

**Ce jeu « Agriculture Crop Yield », tu lui fais confiance ?**
→ Il est simulé : cultures identiques, catégories à parts égales, rendements négatifs, relation presque linéaire.
🔁 « Quel est le rendement moyen du coton et celui du riz ? »

## 2. ACP et variables clés

**Qu'a donné ton ACP ?**
→ Valeurs propres toutes ≈ 1 : pas de structure, pas de réduction possible ; axes non interprétables.
🚩 « CP1 est l'axe de l'irrigation » ; ACP sans standardisation (la pluie écrase tout).
🔁 « Que vaut la deuxième valeur propre par rapport à la première ? Qu'est-ce que ça veut dire ? »

**Alors, quelles sont les variables clés ?**
→ Sur le jeu synthétique : pluie, puis engrais et irrigation (règles de la simulation, comparées par écart-type) ; sur le jeu FAO : la culture domine, puis
température et pesticides (taille du pays), la pluie apporte peu. Mesuré par un modèle, pas par l'ACP.
🚩 Variables clés tirées de l'ACP ; coefficients bruts comparés entre unités différentes ; « les pesticides
augmentent le rendement ».

## 3. Modélisation et MLflow (compétence 1)

**Quelle est ta métrique principale, et pourquoi ?**
→ Une seule, choisie avant (RMSE, MAE ou RMSE du log), justifiée (cultures d'échelles différentes → log ou erreur
relative). Les autres en complément.
🚩 Trois métriques dont on choisit la meilleure après coup.

**À quoi compares-tu ton modèle ?**
→ Une référence naïve (moyenne ou médiane par culture) ; un modèle qui ne bat pas la référence n'apporte rien.
🔁 « Si je prédis juste le rendement habituel de chaque culture, quelle erreur j'obtiens ? »

**Comment as-tu découpé tes données ?**
→ Par pays (`GroupKFold`, test sur des pays mis de côté), ou au moins une justification de l'usage visé.
🚩 Découpage aléatoire et R² ≥ 0,9.
🔁 « Ton test contient-il des pays vus à l'entraînement ? Que se passe-t-il pour un pays nouveau ? »

**Pourquoi ces hyperparamètres, et pourquoi ces plages ?**
→ Lien avec le surapprentissage (profondeur, taille minimale des feuilles), plages larges puis resserrées ;
recherche systématique (grille ou aléatoire).
🚩 « J'ai pris les valeurs par défaut » ; « j'ai essayé à la main jusqu'à ce que ce soit bien ».

**Que verrait-on dans MLflow si `min_samples_leaf` valait 1 ? Pourquoi ?**
→ Erreur d'entraînement très basse, erreur sur pays nouveaux très haute : l'arbre isole chaque pays (mémorisation).
🚩 Le nom de l'hyperparamètre, sans le mécanisme.
🔁 « Que fait une feuille d'une seule ligne face à un pays qu'elle n'a jamais vu ? »

**Qu'as-tu appris de tes expériences MLflow ?**
→ Une phrase par expérience : « la forêt par défaut mémorise les pays », « les modèles optimisés sont au coude à
coude », « la culture explique l'essentiel ; les conditions ajoutent un gain réel mais modeste ».
🚩 Une description des captures sans conclusion.

**Je recharge ton modèle sur ma machine dans six mois : qu'est-ce qui peut casser ?**
→ Version de scikit-learn (ou de pandas) différente : on fige les versions, on note la version dans le modèle, on
teste le rechargement (même prédiction).
🚩 « Il suffit de faire joblib.load. »

## 4. Pipeline MLOps et reproductibilité (compétence 2)

**Montre-moi ton pipeline, schéma en main : étapes, entrées, sorties.**
→ Préparer → entraîner → évaluer, séparés, reliés par des fichiers ; une configuration centralisée.
🚩 Un seul notebook de 80 cellules.

**Si je clone ton dépôt sur une machine neuve, que dois-je faire pour obtenir ton modèle ?**
→ Une ou deux commandes (`uv sync`, `agrireco all`, ou `docker build`), versions figées, données vérifiées.
🔁 « Et si l'URL des données change ? Et si la version de scikit-learn change ? »

**Que se passe-t-il si un fichier attendu manque ?**
→ Message clair et arrêt (code de sortie non nul), pas une trace de 40 lignes au milieu du pipeline.

## 5. API, interface, CI/CD (compétence 2)

**J'envoie une température de 300 °C à ton API : que se passe-t-il ?**
→ Refus 422 grâce à la validation (Pydantic).
🚩 Une prédiction renvoyée.

**Je supprime scikit-learn de l'environnement de ton interface : marche-t-elle encore ? Pourquoi ?**
→ Oui : l'interface ne fait qu'appeler l'API ; tout le ML est derrière l'API.
🚩 « Non, elle charge le modèle. »

**Décris ton workflow CI. Que se passe-t-il si un test échoue ?**
→ Tests → build → (publication) ; un échec arrête la suite, rien n'est publié ; notification (e-mail GitHub,
résumé, Slack…). Idéalement : il l'a provoqué une fois.
🚩 Les étapes ne dépendent pas les unes des autres ; un mot de passe dans le YAML.
🔁 « Montre-moi un run rouge. »

**Tes tests passent, mais l'image Docker ne démarre pas en production : comment ta CI aurait-elle pu le voir ?**
→ Un test d'intégration : le conteneur construit est lancé et appelé dans la CI (`/health`, `/predict`).
🔁 « Tes tests appellent-ils le code, ou l'image construite ? »

**Comment surveillerais-tu ton pipeline une fois en production ?**
→ Journaux et alertes d'échec, suivi des entrées (dérive : conditions hors des plages vues), suivi de l'erreur quand
les rendements réels arrivent, réentraînement contrôlé.

## 6. Impact métier et soutenance (simulation, rôle du Lead Data Scientist)

**Un exploitant te demande ce que l'outil peut faire pour lui : que lui réponds-tu, sans jargon ?**
→ Rendement moyen national avec une erreur typique d'environ 37 % (la moitié des cas au-delà) ; pas une prédiction pour sa parcelle ; pas de
rentabilité.
🚩 Jargon (« RMSE de 0,61 ») sans traduction.

**Quelles cultures recommandes-tu, et quel gain anticipes-tu ?**
→ Classement par rendement relatif ; gain mesuré face au hasard **et** à un classement fixe ; limites dites.
🚩 « Le modèle recommande la culture la plus rentable » ; un gain en euros sans prix.
🔁 « Ton classement fait-il mieux qu'une liste fixe, la même pour tout le monde ? »

**Pourquoi ce modèle plutôt qu'un autre ?**
→ Règle de choix fixée avant (meilleur score, ou plus simple à score équivalent) ; écarts dans le bruit reconnus.

**Questions anti-plagiat (du guide)** : « Comment as-tu fait pour [ta fusion / ta recherche d'hyperparamètres] ? »,
« Quelles étapes as-tu suivies pour construire ton workflow ? ». Un apprenant qui a fait le travail raconte ses
erreurs ; un apprenant qui a recopié décrit le résultat.

**Questions bonus (non bloquantes)** : ta « meilleure erreur » ? Que faudrait-il pour une mise en production réelle ?
Quels indicateurs métier ajouterais-tu (prix, coûts, risque) ?
