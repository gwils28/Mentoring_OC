# Kit mentor — P02 « Entraînez-vous avec SQL et créez votre BDD »

Souvent le **premier contact** de l'apprenant avec une base de données : tables, types, clés, SQL. Le projet tient
en trois gestes, dans cet ordre : **modéliser** (dictionnaire + schéma), **charger** (et prouver qu'on n'a rien
perdu), **interroger** (12 besoins métier). Le premier est le plus important : un mauvais type ou une mauvaise clé
se paie jusque dans les requêtes.

| Quand | Fichier | Pour quoi faire |
|---|---|---|
| Avant la 1ʳᵉ séance | [01_deroule_des_seances.md](01_deroule_des_seances.md) | planifier les séances (temps plein ou alternance) |
| Pendant les séances | [02_questions_oral.md](02_questions_oral.md) | questions à poser, réponses attendues, relances |
| Quand ça coince | [03_erreurs_frequentes.md](03_erreurs_frequentes.md) | diagnostiquer, surtout les erreurs nées dans le tableur |
| À la réception des livrables | [04_grille_evaluation.md](04_grille_evaluation.md) | vérifier chaque critère, avec renvoi au corrigé |
| Séance bilan | [05_trame_bilan.md](05_trame_bilan.md) | scénario de démonstration en direct + trame de compte-rendu |

## Repères

- **Charge** : environ 60 h. Temps plein : moins de 2 semaines, 1 séance puis le bilan. Alternance : moins de
  4 semaines, 3 séances puis le bilan.
- **Pas de soutenance** : le mentor valide en séance bilan, après une **démonstration en direct** des requêtes.
- **Livrables de l'apprenant** : un dictionnaire des données (tableur) et une présentation (contexte, préparation
  des données, extrait du dictionnaire, schéma, capture de la base, requêtes et résultats commentés).
- **Outils de l'apprenant** : un tableur (Excel, Google Sheets, Power Query) pour préparer les CSV, SQLite Studio
  pour la base. Pas de Python attendu.
- **Rassurer** : le vocabulaire (entité, clé étrangère, 3NF) déroute au début ; c'est normal et passager.

## Ressources du dossier

| Ressource | Usage |
|---|---|
| [Corrigé](../notebooks/dataimmo_corrige.ipynb) | pour **comparer** les chiffres ; ne pas le transmettre avant le bilan |
| [Requêtes SQL du corrigé](../sql/requetes/) | une par besoin, à ouvrir dans SQLite Studio |
| [Base SQLite du corrigé](../data/processed/dataimmo.sqlite) | ouvrir dans SQLite Studio pour rejouer une requête de l'apprenant |
| [Dictionnaire du corrigé](../livrables/dictionnaire_donnees.xlsx) | comparer colonne par colonne |
| [Fiches pédagogiques](../pedagogie/) | 9 fiches, une notion chacune, SQL copiable dans SQLite Studio (fiches 6 à 9 : sur la base de l'apprenant ou la base de démonstration) |
| [Présenter un résultat](../../transverse/presenter_un_resultat.md) | fiche transverse du parcours : de la requête à la phrase métier |

**Quand donner quoi** : fiches 1 à 4 en début de projet (modéliser), fiche 5 au chargement, fiches 6 à 9 à la
demande pendant les requêtes. Aucune fiche ne résout un des 12 besoins : on peut les donner sans risque. Le corrigé
est public (repo GitHub) : le dire à l'apprenant et lui demander de ne pas l'ouvrir avant le bilan.

## Chiffres de référence (corrigé)

Les chiffres de l'apprenant peuvent légitimement différer selon ses choix ; un écart **expliqué** est acceptable,
un écart qu'il ne sait pas expliquer mérite une question.

| Élément | Valeur du corrigé | Variante acceptable |
|---|---|---|
| Lignes chargées | vente 34 169 · bien 34 169 · commune 3 125 · région 19 | commune : plus de 3 125 si toutes les communes du référentiel sont chargées |
| Ventes sans valeur foncière | 18 (gardées, valeur `NULL`) | supprimées si c'est dit (34 151 ventes) |
| B1 appartements vendus | 31 378 | — |
| B2 par région | Île-de-France 13 995 (45 %), PACA 3 649, ARA 3 253 ; 17 régions | — |
| B3 par nombre de pièces | 2 p. 31,18 % · 3 p. 28,57 % · 1 p. 21,48 % (sur les appartements) | sur toutes les ventes : 2 p. 28,63 % |
| B4 top départements (€/m²) | 75 (12 053), 92, 94, 06, 74, 93, 78, 69, 2A, 33 | médiane : 17 remplace 33 |
| B5 maison Île-de-France | 3 745 €/m² (1 059 maisons) | médiane 3 244 |
| B6 appartement le plus cher | 9 000 000 € (Paris 16e, 9,10 m²) : **anomalie** à commenter | — |
| B7 évolution T1 → T2 | +3,68 % (16 776 → 17 393) | appartements seuls : +3,87 % |
| B8 régions, > 4 pièces | Île-de-France 8 770 €/m², puis La Réunion (n = 2) | ≥ 4 pièces : Île-de-France 6 702 ; classement modifié |
| B9 communes ≥ 50 ventes au T1 | 48 | « plus de 50 » : 47 |
| B10 écart 2 p. / 3 p. | −12,4 % (4 909 → 4 300 €/m²) | +14,2 % dans l'autre sens ; ≈ −5 % à géographie égale |
| B11 top 3 de 5 départements | 15 communes, dont 5 sur 1 seule vente | avec au moins 5 ventes : autre liste |
| B12 ventes pour 1 000 hab. | Paris 2e 5,88 | population totale : mêmes 20 communes |

## Deux écarts du corrigé avec l'ébauche fournie à l'apprenant

1. **Code postal** : le corrigé le range dans `bien` (adresse), l'ébauche dans `commune`. Les deux sont acceptés ;
   ce qui compte est que l'apprenant sache répondre à « Nice a 4 codes postaux : où sont-ils dans ta base ? ».
2. **Code commune** : texte sur 3 caractères dans le corrigé, entier dans l'ébauche. Accepté si l'apprenant sait
   pourquoi « 004 » devient 4 et comment il reconstruit la clé.
