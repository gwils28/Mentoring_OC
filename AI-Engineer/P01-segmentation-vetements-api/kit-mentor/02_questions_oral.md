# Questions d'oral

Format : **question** → ce qu'on attend → 🚩 signal d'alerte → 🔁 relance si l'apprenant bloque.
Choisir 2 ou 3 questions par section. Laisser au moins 3 secondes de réflexion avant de relancer.

## 1. Environnement et secret

**Si je clone ton dépôt sur mon ordinateur, que dois-je taper pour retrouver ton environnement ?**
→ `pip install -r requirements.txt` (ou `uv sync`), avec des versions figées.
🚩 « Il faut installer requests, Pillow… » sans fichier de dépendances.

**Où est ton token, et comment es-tu sûr qu'il n'est pas sur GitHub ?**
→ Dans `.env`, listé dans `.gitignore` ; vérifié avec `git check-ignore .env` ou en regardant le dépôt en ligne.
🚩 Le token en clair dans une cellule, même « supprimée ensuite », ou dans une sortie de notebook.
🔁 « Ouvre ton fichier .ipynb dans un éditeur de texte et cherche hf_. »

**Si ton token fuit demain, que fais-tu ?**
→ Le révoquer sur Hugging Face, en créer un autre ; effacer le commit ne suffit pas.
🚩 « Je supprime le commit » sans révoquer.
🔁 « Quelqu'un a pu copier le dépôt entre-temps : le token est-il encore utilisable ? »

**Quels droits as-tu donnés au token ?**
→ Le minimum (lecture, ou « appeler les Inference Providers »).
🔁 « Que pourrait faire quelqu'un qui volerait un token avec droit d'écriture ? »

## 2. Appeler l'API

**Décris ta requête : à qui, quoi, comment ?**
→ POST vers l'adresse du modèle, en-tête `Authorization: Bearer …` et `Content-Type`, corps = octets de l'image.

**Que contient la réponse, concrètement ?**
→ Une liste JSON, un élément par classe détectée : `label`, `score`, `mask` (PNG encodé en base64).
🚩 « Ça renvoie l'image segmentée. »
🔁 « Affiche `type(reponse)` et `reponse[0].keys()`. »

**Ton script traite 50 images. La 30ᵉ renvoie une erreur 503 : que se passe-t-il ?**
→ Le script attend puis réessaie ; s'il échoue encore, il note l'erreur et passe à l'image suivante.
🚩 Le notebook plante et les 29 résultats sont perdus.

**Et si l'erreur est une 401 ?**
→ Réessayer ne sert à rien : token faux ; arrêt immédiat avec un message clair.
🚩 La même boucle de nouvelles tentatives que pour une 503.
🔁 « Si tu réessaies dans 16 secondes, qu'est-ce qui aura changé pour ton token ? »

**Pourquoi un `timeout` ? Pourquoi une pause entre les appels ?**
→ Sans timeout, une requête peut bloquer indéfiniment ; la pause (ou un plafond de N requêtes par minute) évite le
refus du serveur (429) et le blocage du compte.

**Pourquoi réduire les images avant de les envoyer ?**
→ Moins d'octets, requête plus rapide ; le modèle travaille de toute façon en 512 × 512.
🔁 « Combien pèse une image de ton dossier ? Et ce que tu envoies ? »

## 3. Visualiser et mesurer

**Comment as-tu fusionné les masques de chaque classe en une seule image ?**
→ Une carte d'identifiants : chaque pixel reçoit le numéro de sa classe ; le fond par défaut.

**Comment as-tu redimensionné les masques ?**
→ Au plus proche voisin (NEAREST).
🚩 Interpolation bilinéaire : des classes « fantômes » sur les contours (fiche 5).

**Ton modèle a 96 % de pixels bien classés. C'est bien ?**
→ Pas forcément : le fond fait 78 % des pixels, un modèle « tout en fond » aurait déjà 78 %. On mesure chaque
classe (IoU).
🔁 « Que vaudrait l'exactitude d'un modèle qui ne prédit que du fond ? »

**Explique l'IoU à quelqu'un qui n'a jamais fait de maths.**
→ La part de surface que la silhouette prédite et la silhouette dessinée ont en commun.
🚩 « C'est le pourcentage de bons pixels » (c'est l'exactitude, pas l'IoU).
🔁 « Dessine deux rectangles qui se chevauchent : quelle surface est au numérateur, laquelle au dénominateur ? »

**Pourquoi la ceinture a-t-elle un IoU plus bas que le pantalon ?**
→ Objet fin : un décalage d'un pixel sur le contour coûte beaucoup en proportion.

**Un IoU de 0,79 sur 50 images : combien aurais-tu obtenu sur 50 autres images ?**
→ Autre chose : avec 50 images, le chiffre a une marge d'incertitude (le corrigé l'estime par bootstrap : de 0,76 à
0,82, fiche 6 § 4). Et sur des images que le modèle n'a jamais vues, sans doute moins, car celles-ci ont servi à
l'entraîner (fiche 7).
🚩 « Pareil, c'est le score du modèle. »
🔁 « Si tu retirais au hasard 10 images et en recopiais 10 autres, le score bougerait-il ? »

## 4. Valider

**À quoi servent les jeux d'entraînement, de validation et de test ?**
→ Apprendre / régler / mesurer une fois sur du jamais vu.
🚩 Validation et test confondus (« on teste plusieurs fois pour choisir le meilleur réglage »).
🔁 « Si tu choisis tes réglages en regardant le test, que vaut encore le test ? »

**Ici, tu n'as rien entraîné : à quoi te servent les 50 images ?**
→ À tester seulement.

**Question bonus (apprenant à l'aise) : ces 50 images, le modèle les a-t-il déjà vues ?**
→ Oui : elles sont dans le jeu public ATR sur lequel il a été affiné. Le score est donc optimiste ; il faudrait des
photos ModeTrends nouvelles, découpées par influenceur.
🔁 « Va lire la fiche du modèle sur Hugging Face : sur quelles données a-t-il été entraîné ? D'où viennent tes
images ? »

## 5. Chiffrer et présenter

**Comment as-tu obtenu ton budget pour 500 000 images ?**
→ Volume × temps (ou prix) par image, avec la source de chaque prix et sa date.
🚩 Un chiffre sans calcul, ou « gratuit » sans parler des crédits.

**Combien d'images par minute faut-il traiter ?**
→ 500 000 / (30 × 24 × 60) ≈ 11,6.
🚩 Un débit calculé sur 30 jours de 8 heures sans le dire, ou pas de débit du tout.
🔁 « Combien de minutes y a-t-il dans 30 jours ? »

**Payer à l'usage ou louer une machine : quand change-t-on d'avis ?**
→ À l'usage tant que le volume est faible ou irrégulier ; machine dédiée (par lots) quand le volume devient grand
et régulier.

**Si la directrice IA n'a que 30 secondes, que lui dis-tu ?**
→ Techniquement faisable, qualité prometteuse mais à confirmer sur ses propres photos, coût faible (de l'ordre de
quelques dizaines de dollars par mois au plus : moins de 17 $ en serverless d'après le corrigé).
