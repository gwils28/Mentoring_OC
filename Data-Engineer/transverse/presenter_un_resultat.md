# Présenter un résultat : de la requête à la phrase métier

Fiche transverse du parcours Data Engineer, utile à chaque projet qui se termine par une présentation
(P01, P02…). Exemple tiré de P02 (base DATAImmo).

> **L'idée clé.** Votre interlocuteur ne lira pas votre requête. Il retiendra **une phrase**. Votre travail est de
> choisir cette phrase, de la prouver, et de dire jusqu'où elle est vraie.

## 1. La structure d'une diapositive de résultat

Chaque résultat suit le même chemin, de haut en bas :

| Bloc | Contenu | Exemple (P02, besoin 10) |
|---|---|---|
| **Titre = le message** | une phrase complète, avec le chiffre clé | « L'écart de prix au m² entre 2 et 3 pièces tient surtout à la localisation » |
| **La question** | le besoin, reformulé simplement | Le m² d'un 3 pièces est-il moins cher que celui d'un 2 pièces ? |
| **La preuve** | le résultat (tableau court ou graphique), la requête en petit ou en annexe | 2 pièces 4 909 €/m², 3 pièces 4 300 €/m² : −12,4 % |
| **La limite** | ce que le chiffre ne dit pas | À géographie égale, l'écart n'est plus que d'environ 5 % ; à Paris seul, il disparaît |
| **La suite** | ce que l'on ferait ensuite, ou ce que l'on recommande | Comparer les prix à l'intérieur d'une même commune |

Un titre comme « Requête 10 » ou « Écart de prix 2/3 pièces » est un **sujet**, pas un message : le lecteur doit
deviner la conclusion.

## 2. Écrire pour un non-technicien

| À éviter | À écrire |
|---|---|
| « J'ai fait un GROUP BY sur la région avec un COUNT » | « L'Île-de-France concentre 45 % des ventes d'appartements de l'extrait » |
| « La moyenne de la colonne prix_m2 vaut 3 745 » | « Une maison francilienne se vend 3 745 € le m² » |
| « L'INNER JOIN donne 34 169 lignes » | « Aucune vente n'a été perdue pendant le chargement » |
| « RANK() OVER (PARTITION BY …) » | « Les 3 communes les plus chères de chaque département » |

Le vocabulaire technique a sa place : dans la partie méthode, en une diapositive, pour montrer la rigueur.

## 3. Dire jusqu'où le chiffre est vrai

Trois réflexes, chacun illustré dans P02 :

1. **Afficher l'effectif.** « La Réunion est la 2ᵉ région la plus chère » est faux si la moyenne porte sur
   2 ventes. Un chiffre sans son *n* ne se compare pas.
2. **Signaler les anomalies au lieu de les présenter.** Un appartement à 9 M€ pour 9 m² n'est pas « le plus
   luxueux » : c'est une erreur de saisie ou une vente mal décrite. Le dire montre qu'on regarde ses données.
3. **Distinguer constat et explication.** « Les ventes chutent en avril » est un constat. « À cause du
   confinement » est une explication plausible, mais non démontrée par la base : on écrit « coïncide avec ».

## 4. Construire le récit

Une présentation de projet raconte une histoire en quatre temps :

1. **Le problème** : ce que demande le client, en une diapositive.
2. **Les données et la méthode** : d'où viennent les chiffres, ce qu'on a fait pour qu'ils soient fiables
   (nettoyage, contrôles, preuve du chargement).
3. **Les résultats** : une diapositive par message, du plus important au moins important.
4. **La réponse et les limites** : ce que l'on recommande, ce qu'il faudrait vérifier, la prochaine étape.

Test final : lisez seulement les titres de vos diapositives, dans l'ordre. S'ils racontent l'histoire à eux
seuls, la présentation est prête.

## ✍️ À toi de jouer

Prends un de tes résultats et écris la diapositive en 5 blocs (titre-message, question, preuve, limite, suite).
Puis fais-la lire à quelqu'un qui ne connaît pas le projet : peut-il te redire le message en une phrase ?
