# Kit mentor — P12 Data Scientist ML « Concevez un système de recommandations pour une agriculture optimisée par les données »

Un projet **long** (70 h supervisées + 70 h personnelles) et **large** : données, modèle, MLflow, API, interface,
Docker, CI/CD. La grille ne porte que sur deux compétences : **optimiser l'entraînement** (hyperparamètres, MLflow)
et **automatiser le déploiement** (pipeline MLOps, CI/CD). Le reste de l'énoncé (fusion, ACP, interface) est le
chemin pour y arriver. Le piège caché : **les données ne permettent pas ce que l'énoncé promet** (fusion par pays,
ACP « qui identifie les variables clés », recommandation de la culture « la plus rentable »). Un bon apprenant le
voit, le démontre et le dit ; un apprenant moyen fabrique une fusion et des conclusions qui ne tiennent pas.

| Quand | Fichier | Pour quoi faire |
|---|---|---|
| Avant la 1ʳᵉ séance | [01_deroule_des_seances.md](01_deroule_des_seances.md) | planifier les séances (temps plein ou alternance) et l'ordre des chantiers |
| Pendant les séances | [02_questions_oral.md](02_questions_oral.md) | questions à poser, réponses attendues, relances ; simulation de soutenance |
| Quand ça coince | [03_erreurs_frequentes.md](03_erreurs_frequentes.md) | diagnostiquer : doublons, jointure, validation, MLflow, Docker, CI |
| À la réception des livrables | [04_grille_evaluation.md](04_grille_evaluation.md) | vérifier chaque critère, avec renvoi au corrigé |
| Soutenance et bilan | [05_trame_bilan.md](05_trame_bilan.md) | jouer le Lead Data Scientist, débriefer, rédiger le compte-rendu |

## Repères

- **Charge** : temps plein 4 semaines, 3 séances puis la soutenance ; alternance 8 semaines, 7 séances.
- **Soutenance de 30 min** : 15 min de présentation (± 5), 10 min de discussion, 5 min de débrief. L'évaluateur
  joue le Lead Data Scientist de l'entreprise. Moins de 10 min ou plus de 20 min : refus possible.
- **Livrables** : (1) captures MLflow, (2) notebooks ou scripts d'entraînement, (3) pipeline MLOps (scripts ou
  YAML, Dockerfile), (4) pipeline CI/CD (YAML), (5) rapport métier en PDF pour un public non technique.
- **Outils** : pandas, scikit-learn, MLflow, FastAPI, Streamlit, Docker, GitHub Actions (ou GitLab CI).
- **Ordre conseillé** (repris du guide) : d'abord l'optimisation tracée dans MLflow, puis le pipeline et l'API,
  enfin la CI/CD. Un apprenant qui commence par Docker n'aura pas de modèle à mettre dedans.

## Ce qu'il faut savoir avant la 1ʳᵉ séance

1. **Le jeu « Agriculture Crop Yield » est synthétique.** 1 000 000 de lignes, aucune valeur manquante, des
   catégories à parts égales, 231 rendements négatifs ; les 6 cultures ont toutes un rendement moyen de 4,65 t/ha.
   Une régression linéaire explique 91,3 % du rendement avec pluie, température, engrais (+1,50 t/ha) et irrigation
   (+1,20 t/ha). Ni pays ni année.
2. **La fusion « par pays et année » proposée par l'énoncé est impossible.** La seule clé commune est la culture
   (4 cultures en commun) et les colonnes ajoutées sont constantes. Accepter **toute stratégie justifiée** : jointure
   par culture avec ce constat, ou usage séparé des deux jeux. Refuser une fusion inventée (pays attribués au hasard
   aux régions, etc.).
3. **L'ACP sur le jeu synthétique ne trouve rien** : valeurs propres toutes ≈ 1. C'est la bonne réponse. Ce qui
   doit inquiéter : un apprenant qui interprète les axes ou le cercle des corrélations, ou qui en tire les « variables
   clés » (l'ACP ne regarde pas la cible).
4. **`yield_df.csv` contient des doublons** : 28 242 lignes pour 13 130 clés (pays, culture, année), à cause de
   plusieurs stations de température par pays. En reconstruisant depuis les fichiers bruts avec des noms de pays
   harmonisés : 15 794 lignes, 119 pays (les États-Unis, la Russie et la Chine continentale sont perdus sinon).
5. **La validation aléatoire est très optimiste.** Une forêt aléatoire par défaut : RMSE du log 0,28 en validation
   aléatoire, 0,79 sur des pays jamais vus dans le corrigé (0,72 dans la fiche 4, conditions un peu différentes) :
   pas mieux que la simple médiane de la culture (0,73). Un R² de 0,9 ou plus
   annoncé fièrement signale presque toujours ce problème (ou les doublons).
6. **Les conditions sont nationales** : pluie constante par pays, pesticides en tonnes totales. Le modèle prédit un
   rendement moyen national, pas celui d'une parcelle.
7. **Pas de prix** : « la culture la plus rentable » n'est pas calculable avec ces données. Attendu : le dire, et
   classer par un rendement **relatif** (les t/ha ne se comparent pas entre cultures) ou ajouter des prix externes en
   le justifiant.
8. **La recommandation ne bat pas un classement fixe** dans le corrigé (et probablement pas chez l'apprenant). Ce
   n'est pas un échec du projet : c'est un résultat, s'il est mesuré honnêtement. La grille ne demande pas un modèle
   qui recommande bien ; elle demande des expériences comparées, interprétées et justifiées.

## Chiffres de référence (corrigé)

Issus de `data/processed/resultats.json` (graine 42, 24 pays de test). Un apprenant qui fait d'autres choix
(autre découpage, autres variables, `yield_df.csv` dédoublonné sans harmoniser les noms) obtiendra d'autres
chiffres : ce qui compte, ce sont les **ordres de grandeur** et la **cohérence** avec sa méthode.

| Quantité | Corrigé | Variantes acceptables |
|---|---|---|
| Lignes / pays / cultures / années | 15 794 / 119 / 10 / 1990-2013 | 13 130 lignes et 101 pays sans harmonisation des noms (à signaler) |
| CV par pays, référence médiane de la culture | RMSE-log 0,734 | — |
| CV par pays, Ridge / forêt optimisée / boosting optimisé | 0,641 / 0,634 / 0,638 | 0,60 à 0,70 selon les variables et les plis |
| Forêt par défaut, CV aléatoire / par pays | 0,28 / 0,79 | toute CV aléatoire ≪ CV par pays |
| Fiche 4 (119 pays, 100 arbres) | 0,28 / 0,72, au niveau de la référence (0,72 en fiche 5) | — |
| Test (24 pays), modèle retenu (Ridge, α = 10) | RMSE-log 0,608 (IC 0,53-0,68), erreur relative médiane 37 % | 0,51 à 0,67 selon le tirage des pays |
| R² (log) global au test | 0,62 | en R² brut (t/ha) on trouve autre chose : demander lequel |
| Recommandation : bonne 1ʳᵉ place, modèle / classement fixe / hasard | 37,5 % / 39,6 % / 17,2 % | écart au classement fixe indiscernable de zéro |
| Écart modèle − classement fixe | −2,1 points (IC −10,2 à +7,5) | tout écart dont l'intervalle contient zéro : « pas mieux qu'une liste fixe » |
| Biais moyen au test | +0,54 t/ha, mais négatif dans 17 tirages de pays sur 20 | signe instable selon le tirage : ne pas l'interpréter |
| Facteur typique prédiction / réalité | 1,47 (70 % des cas à moins d'un facteur 1,8) | — |
| Hyperparamètre décisif | `min_samples_leaf` (50) pour les arbres | `max_depth` faible, régularisation forte : même idée |

## Ressources du dossier

| Ressource | Usage |
|---|---|
| [Corrigé, étape 1](../notebooks/01_exploration_fusion.ipynb) | exploration, pièges, ACP, fusion ; **ne pas transmettre avant la soutenance** |
| [Corrigé, étape 2](../notebooks/02_modelisation_mlflow.ipynb) | comparaison, optimisation, MLflow, test, recommandation |
| [Package `agrireco`](../src/agrireco/) et [`config.yaml`](../config.yaml) | pipeline `prepare → train → evaluate`, une commande `uv run agrireco all` |
| [API](../api/main.py), [interface](../app/app.py), [`docker-compose.yml`](../docker-compose.yml) | démonstration en séance : `docker compose up --build` |
| [CI/CD](../docs/ci_cd.md) | workflow commenté, échecs simulés, notifications |
| [Rapport métier](../livrables/rapport_metier.pdf) | exemple de rapport non technique (7 pages) |
| [Présentation](../presentation/) | support de soutenance du corrigé, à montrer **après** la soutenance |
| [Fiches pédagogiques](../pedagogie/) | 9 fiches, une notion chacune, sur les vraies données |
| [Page interactive](../site/index.html) | à partager aux apprenants : étapes, labos, quiz, check-list |
| [Aller plus loin](../ALLER_PLUS_LOIN.md) | registre de modèles, suivi de dérive, prix, incertitude, hébergement |

**Quand donner quoi** : fiches 1 à 3 dès la séance 1 (maille, jointure, ACP) ; fiches 4 et 5 pour la modélisation
et MLflow ; fiche 6 pour structurer le pipeline ; fiches 7 et 8 pour l'API, Docker et la CI ; fiche 9 pour la
recommandation et le rapport. Aucune fiche ne résout un livrable : elles enseignent la notion sur un autre angle
(arbre de décision pour l'optimisation, table de correspondance commencée mais pas complète, paires de cultures
pour juger un classement, workflow minimal) ; les fiches 4, 5 et 9 utilisent la fusion du package, en le signalant. Le dépôt est public : rappeler que le corrigé ne se transmet pas avant la soutenance.
