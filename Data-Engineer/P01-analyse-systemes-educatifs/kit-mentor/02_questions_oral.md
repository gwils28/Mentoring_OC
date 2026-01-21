# Questions d'oral

Format : **question** → ce qu'on attend → 🚩 signal d'alerte → 🔁 relance si l'apprenant bloque.
Inutile de tout poser : choisir 2 ou 3 questions par section selon le niveau de l'apprenant.

## 0. Compréhension du projet

**Que demande Mark, en une phrase ?**
→ Savoir si les données EdStats aident à choisir des pays pour l'expansion d'academy, et lesquels ont un fort
potentiel (aujourd'hui et demain).
🚩 « Faire un notebook pandas » : le livrable est confondu avec l'objectif.
🔁 « Si tu étais Mark, que ferais-tu de ton notebook ? »

**Qui sont les clients d'academy, et quelles données le diraient ?**
→ Lycéens et étudiants, connectés, capables de payer : effectifs scolarisés, population jeune, accès à internet,
revenu.

## 1. Exploration (partie 1)

**Dans `Data`, que représente une ligne ? Comment le prouves-tu ?**
→ Un couple (pays, indicateur), avec les années en colonnes ; preuve : 0 doublon sur ces deux colonnes.
🚩 « Une ligne = un pays ».
🔁 « Combien de lignes pour la France ? Pourquoi autant ? »

**Pourquoi certaines lignes de `Country` ne sont-elles pas des pays ? Comment les as-tu trouvées ?**
→ Ce sont des agrégats (Monde, zones, groupes de revenu) : pas de région, codes spéciaux.
🚩 Suppression par numéro de ligne (`iloc`, `drop([5, 57, …])`).
🔁 « Et si je trie le tableau avant d'exécuter ton code ? » (voir [fiche 1 §5](../pedagogie/01_maille_et_qualite.ipynb))

**As-tu vérifié ta règle sur ses exceptions ?**
→ Gibraltar et Nauru n'ont pas de région mais sont de vrais territoires.
Question **bonus** : la plupart des apprenants ne le voient pas. Si c'est le cas, c'est un point d'amélioration,
pas un point bloquant.

**Liste et `~isin()`, ou inner join : quelle différence de résultat, et laquelle préfères-tu ?**
→ 1 pays d'écart (VGB, présent dans Data mais pas dans Country). La liste noire laisse passer ce qu'elle ne connaît
pas ; la liste blanche le bloque.

**Que fais-tu des valeurs manquantes ? Pourquoi ne pas tout supprimer avec `dropna()` ?**
→ Elles sont massives (86 % de cellules vides dans Data) ; `dropna()` viderait le fichier. On les mesure, on choisit
les années et les indicateurs les mieux remplis, puis on agrège.

## 2. Réduction du périmètre (partie 2)

**Pourquoi tous ces filtres ?**
→ Plus de 3 600 indicateurs, c'est trop pour une analyse humaine : il faut un périmètre exploitable, utile au
métier **et** assez renseigné.

**Pourquoi y a-t-il des valeurs pour 2050 ?**
→ Ce sont des projections (Wittgenstein), pas des observations : on ne les mélange pas avec les données réelles.
🚩 Moyenne calculée sur 1970-2100.

**Comment as-tu choisi tes années ? Et ton seuil de remplissage ?**
→ Un graphique ou un tableau du remplissage par année, puis un seuil **argumenté** (« 60 % : en dessous, plus de
40 % des couples (pays, année) seraient vides »).
🔁 « Si tu passes ton seuil de 60 % à 50 %, combien d'indicateurs gagnes-tu ? Lesquels t'intéressent ? »
Un seuil « raisonnable » est un seuil justifié par une mesure et modifiable en un seul endroit, pas un seuil
« juste ».

**Pourquoi agréger pour ne plus être à la maille (pays, indicateur, année) ?**
→ Pour comparer des pays, il faut **une** valeur par pays et par indicateur.
🚩 Un `groupby(...).mean()` sur toutes les colonnes d'années, projections comprises.

**Moyenne ou médiane pour agréger les années ? Sur combien d'années au minimum ?**
→ Médiane : robuste à une année aberrante. Au moins 3 années, sinon la valeur n'est pas fiable.

**Pourquoi le hardcoding fait-il perdre du temps ?**
→ Une valeur écrite en dur à plusieurs endroits doit être modifiée partout ; un index de ligne change dès qu'on trie
ou filtre. Les paramètres se regroupent en tête du notebook.
🔁 « Je te demande de passer de 2010-2014 à 2011-2015 : combien d'endroits de ton notebook modifies-tu ? »

## 3. Analyse (partie 3)

**Pearson et Spearman : quelle différence ? Lequel as-tu choisi, et pourquoi ?**
→ Pearson mesure une relation linéaire et est sensible aux extrêmes ; Spearman, calculé sur les rangs, mesure une
relation monotone et résiste aux extrêmes. Pour des populations ou des PIB très asymétriques, on préfère Spearman.
🔁 Montrer les 4 cas de la [fiche 3](../pedagogie/03_correlations.ipynb).

**Pourquoi deux variables très corrélées sont-elles redondantes ? Laquelle gardes-tu ?**
→ L'une apporte presque la même information que l'autre. On garde la plus utile au métier, et on le **dit**.
Question piège : « une corrélation de 0 veut-elle dire qu'il n'y a aucun lien ? » (non : pensez à une relation en U).

**Si j'ajoute 10 pays sans valeur pour cet indicateur, quelles lignes de `describe()` changent ?**
→ Aucune : `describe()` ignore les valeurs manquantes, `count` compris (il ne compte que les valeurs renseignées).
C'est une façon de vérifier que l'apprenant a compris `count` sans lui faire réciter le tableau.

**Explique chaque ligne de `describe()`.**
→ `count` = valeurs renseignées (et non le nombre total de lignes) ; quartiles = 25 / 50 / 75 % des pays en dessous ;
moyenne ≫ médiane ⇒ asymétrie à droite.
🚩 « `count`, c'est le nombre de pays ».

**Comment repères-tu des valeurs extrêmes ? Les supprimes-tu ?**
→ Comparer la moyenne et la médiane, le max et Q3 ; boxplot. On ne supprime que les valeurs **impossibles**.

**Pourquoi écrire des fonctions ?**
→ Pour ne pas copier-coller : un seul endroit à corriger, un traitement identique pour tous, un code lisible.
🔁 « Tu veux ajouter la médiane sur tes 5 histogrammes : combien de fois modifies-tu ton code ? »

**Comment as-tu choisi tes pays ? Que se passe-t-il si on change tes poids ?**
→ Une méthode chiffrée (top-k communs, moyenne pondérée…). Les apprenants avancés testent la sensibilité aux poids.
🚩 Additionner des critères d'unités différentes (population + pourcentage) sans normalisation.
🔁 « Ton premier pays est-il premier parce qu'il est bon partout, ou parce qu'un seul critère l'écrase ? »

**Ta recommandation dit-elle que l'internet *cause* le potentiel d'un pays ?**
→ Non : ce sont des associations. Le score trie, il ne prédit pas.

## 4. Présentation et environnement

**Raconte ta présentation en 3 phrases à quelqu'un qui ne connaît pas pandas.**
→ Le problème, ce que disent les données, la recommandation avec ses limites.
🚩 Commencer par « j'ai importé pandas » ou dérouler le notebook cellule par cellule.
🔁 « Quelle est la seule slide que Mark doit retenir ? »

**Pourquoi `pyproject.toml` ? Que fait `uv sync` ? À quoi sert `uv.lock` ?**
→ `pyproject.toml` déclare les dépendances ; `uv.lock` fige les versions exactes ; `uv sync` recrée l'environnement à
l'identique, chez n'importe qui.
🚩 « Pour installer pandas » sans notion de reproductibilité.
