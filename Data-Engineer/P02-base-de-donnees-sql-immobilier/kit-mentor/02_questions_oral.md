# Questions d'oral

Format : **question** → ce qu'on attend → 🚩 signal d'alerte → 🔁 relance si l'apprenant bloque.
Choisir 2 ou 3 questions par section.

## 1. Comprendre les données

**Dans le fichier des valeurs foncières, que représente une ligne ?**
→ Une vente d'un bien (une mutation), à une date, pour un prix.
🔁 « Si le même appartement était revendu en mai, combien de lignes aurait-il ? »

**Pourquoi as-tu gardé (ou supprimé) cette variable ?**
→ Gardée si un besoin du compte-rendu en a besoin, ou si elle décrit l'adresse ; supprimée si elle est vide,
redondante ou personnelle. L'apprenant doit pouvoir relier chaque variable gardée à un besoin.
🚩 « Je l'ai gardée au cas où » pour une dizaine de colonnes vides.

**Le code département est-il un nombre ?**
→ Non, une étiquette : « 2A », « 2B », « 971 » ; « 01 » perdrait son zéro.
🚩 Colonne `INTEGER` et la Corse absente de la base sans que l'apprenant l'ait remarqué.
🔁 « Montre-moi les ventes du département 2A dans ta base. »

## 2. Modéliser

**Pourquoi pas le code postal comme clé de la commune ?**
→ Il n'est pas unique : le notebook le montre, 05100 regroupe à lui seul Briançon, Montgenèvre et Névache.
🔁 « Filtre le fichier sur le code postal 5100 : combien de communes vois-tu ? »

**Nice a 4 codes postaux : où sont-ils dans ta base ?**
→ Soit dans `bien` (chaque adresse garde le sien), soit un seul dans `commune` (les autres sont perdus) ; les
deux sont défendables si l'apprenant connaît le coût de son choix.

**Où est stocké le nom de la région, et combien de fois ?**
→ Une fois, dans `region` ; la commune ne garde que `id_region`. C'est la 3NF.
🚩 `nom_region` dans `commune` ou dans `bien`.
🔁 « Si la région change de nom, combien de lignes modifies-tu ? »

**Quelle est la nature de `id_codedep_codecommune` dans ton dictionnaire ?**
→ Concaténée (département + commune), avec sa règle de calcul écrite.

**Le nom de l'acquéreur : qu'en as-tu fait, et pourquoi ?**
→ Supprimé (minimisation) : donnée personnelle sans utilité pour les besoins. Bonus : savoir que la base n'est pas
anonyme pour autant (adresse + date + prix). Savoir dire la différence avec la
pseudonymisation (remplacer par un identifiant ; la donnée reste personnelle).
🚩 Colonne présente dans le dictionnaire ou dans la base.

## 3. Charger

**Démontre que tes clés primaires sont uniques.**
→ « Supprimer les doublons » dans le tableur sur la colonne clé, ou une requête
`SELECT cle, COUNT(*) … GROUP BY cle HAVING COUNT(*) > 1` qui ne renvoie rien.

**Démontre que tu n'as perdu aucune ligne.**
→ `COUNT(*)` de chaque table, comparé au nombre de lignes du CSV moins l'en-tête : 34 169, 34 169, 3 125, 19.
🔁 « Et si tu trouves 33 918 ventes, qu'est-ce qui a pu se passer ? » (la Corse, 251 ventes)

**L'ordre des colonnes de ton CSV correspond-il à ta table ?**
→ Oui, vérifié en affichant quelques lignes après l'import : une date ressemble à une date.

**Montre-moi qu'une clé étrangère refuse une commune inconnue.**
→ `PRAGMA foreign_keys = ON;` puis un `INSERT` avec une commune inexistante : refusé.
🚩 L'apprenant ne sait pas que SQLite ignore les FK par défaut.

## 4. Interroger

**Avant d'écrire la requête du besoin 2, décompose-le à voix haute.**
→ Quoi : compter des ventes. Filtres : appartements, 1er semestre. Regroupement : par région. Chemin des jointures :
vente → bien → commune → région.

**WHERE ou HAVING ici ?**
→ WHERE pour filtrer des lignes (le T1), HAVING pour filtrer des groupes (au moins 50 ventes).
🔁 « Au moment où SQLite lit le WHERE, est-ce que COUNT(*) existe déjà ? »

**Combien de lignes attends-tu après cette jointure ?**
→ Autant que de ventes (34 169), puisque chaque vente a un bien, chaque bien une commune, chaque commune une région.

**Pourquoi ton pourcentage vaut 0 ?**
→ Division entière : `COUNT(*) / total` entre entiers. Multiplier par `100.0` avant.

**Ton classement de régions : la 2ᵉ est-elle vraiment la 2ᵉ plus chère ?**
→ La Réunion est 2ᵉ sur 2 ventes : une moyenne sur 2 valeurs ne permet pas de classer. Afficher le nombre de
ventes à côté de chaque moyenne.

**Ton appartement à 9 M€ pour 9 m² : qu'en dis-tu au directeur ?**
→ C'est une anomalie (erreur de saisie ou vente de plusieurs locaux) : on la signale, on ne la présente pas comme
un résultat.

**Que dirais-tu au directeur général de ce résultat ?**
→ Une phrase métier, sans vocabulaire SQL, avec une limite si nécessaire.
🚩 « J'ai fait un GROUP BY sur la région. »
