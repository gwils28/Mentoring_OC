# Kit mentor — P01 « Analysez les données de systèmes éducatifs »

Premier projet technique du parcours. L'apprenant découvre pandas sur un jeu de données volumineux et
désordonné (EdStats, Banque mondiale). Il doit montrer deux choses : une **démarche méthodique** de tri et de
nettoyage, et des **choix d'indicateurs reliés au besoin métier**.

| Quand | Fichier | Pour quoi faire |
|---|---|---|
| Avant la 1ʳᵉ séance | [01_deroule_des_seances.md](01_deroule_des_seances.md) | planifier les séances (temps plein ou alternance) |
| Pendant les séances | [02_questions_oral.md](02_questions_oral.md) | questions à poser, réponses attendues, relances |
| Quand ça coince | [03_erreurs_frequentes.md](03_erreurs_frequentes.md) | diagnostiquer et orienter vers la bonne fiche |
| À la réception des livrables | [04_grille_evaluation.md](04_grille_evaluation.md) | vérifier chaque critère, avec où le trouver dans le corrigé |
| Séance bilan | [05_trame_bilan.md](05_trame_bilan.md) | trame de compte-rendu prête à remplir |

## Repères

- **Charge** : environ 60 h (moitié encadrée, moitié en autonomie). Temps plein : moins de 2 semaines, 1 séance puis le
  bilan. Alternance : moins de 4 semaines, 3 séances puis le bilan.
- **Pas de soutenance** : c'est le mentor qui valide le projet en séance bilan. On ne bloque pas le passage au
  projet suivant pour des points non critiques.
- **Livrables** : un notebook, une présentation, un `pyproject.toml` (uv).
- **Le corrigé est public** (repo GitHub). Plutôt que de le cacher, le dire à l'apprenant et lui demander de ne
  pas l'ouvrir avant son bilan : il sert au mentor à **comparer**.
- **Quand donner quoi** : la page interactive dès le début (son labo 2 reste replié tant que l'apprenant n'a pas
  proposé sa propre méthode) ; les fiches 1 à 4 à la demande, quand une notion bloque ; la **fiche 5 seulement après**
  que l'apprenant a proposé sa propre méthode de sélection des pays (partie 3, étape 2), car elle montre celle du
  corrigé.
- **Partager la page interactive** : `site/index.html` affiché sur GitHub n'est que du code. Envoyer à l'apprenant
  le lien de la version web (artifact Claude, privé par défaut : le partager depuis son menu Share), ou lui faire
  ouvrir le fichier téléchargé dans un navigateur.
- **Adapter le niveau** : un apprenant qui code déjà sera surtout challengé sur la statistique et le métier ; un
  apprenant à l'aise en statistique, sur la qualité du code (fonctions, nommage, absence de hardcoding).
  En cas de prérequis manifestement absents, alerter l'équipe pédagogique **tôt**.

## Ressources du dossier à utiliser en séance

| Ressource | Usage |
|---|---|
| [Notebook corrigé](../notebooks/projet_edstats_corrige.ipynb) | référence : ne pas le donner, s'en servir pour **comparer les chiffres** |
| [Fiches pédagogiques](../pedagogie/) | à dérouler en partage d'écran sur une notion mal comprise (30-45 min chacune) |
| [Page interactive](../site/index.html) | à envoyer à l'apprenant en début de projet : vue d'ensemble et quiz |
| [Aller plus loin](../ALLER_PLUS_LOIN.md) | pour les apprenants rapides, ou en fin de bilan |

## Chiffres de référence (corrigé)

Pour repérer rapidement une erreur dans le travail de l'apprenant. Ses chiffres peuvent légitimement différer selon
ses choix ; un **ordre de grandeur** très différent mérite en revanche une question.

| Élément | Valeur |
|---|---|
| Tailles brutes | Data 886 930 × 70 ; Country 241 × 32 ; Series 3 665 × 21 ; FootNote 643 638 × 5 ; Country-Series 613 × 4 |
| Doublons | 0 dans les 5 fichiers (exacts et sur la clé) |
| Faux pays | 25 agrégats ; Gibraltar et Nauru n'ont pas de région mais sont de vrais territoires |
| Liste ou jointure | 1 pays d'écart (VGB, absent de Country) |
| Indicateurs | 3 665 → 751 (familles métier) → 314 (≥ 60 % renseignés sur 2010-2014) → 15 → 5 non redondants |
| Années utiles | 2010-2014 ; 2015-2017 presque vides ; 2020-2100 = projections |
| Indicateurs finaux | internet (% population), population 15-24 ans, croissance démographique, PIB total, chômage |
| Score | 3 critères en rangs : marché connecté 50 %, maturité numérique 30 %, dynamique 20 % ; 161 pays notés |
| Arbitrage | maturité et dynamique anti-corrélées : ρ = −0,66 |
| Robustesse | autour des poids : 8 pays dans le top 10 ≥ 89 % du temps ; tirage uniforme : seuls Royaume-Uni (74 %) et France (59 %) > 50 % |
