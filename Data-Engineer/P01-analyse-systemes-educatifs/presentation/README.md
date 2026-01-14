# Présentation — livrable 2 du corrigé

| Fichier | Rôle |
|---|---|
| `academy_expansion_edstats.pptx` | support de soutenance (11 slides, avec des notes orateur sur chaque slide) |
| `build_deck.js` | génère le `.pptx` : thème, layouts, sections et contenu |
| `theme_colors.js` | injecte la palette dans le thème PowerPoint |
| `figures/` | graphiques exportés par le notebook corrigé et la fiche 5 |

Une version web de la même présentation existe aussi (artifact Claude, privée par défaut ; on la partage depuis son menu Share).

```bash
npm ci            # installe pptxgenjs (version figée dans package-lock.json)
node build_deck.js
```

Les chiffres des slides proviennent du notebook corrigé : si le notebook change, mettre à jour `build_deck.js`.

## Structure narrative (storytelling)

1. **Le problème** : la demande de Mark (slides 1-2)
2. **Les données** : ce qu'on a et comment on l'a réduit, chaque filtre chiffré (slides 3-5)
3. **L'analyse** : redondances, distributions, méthode de score (slides 6-8)
4. **La tension** : maturité contre croissance, deux familles de marchés (slide 9)
5. **La réponse** : recommandation, robustesse, limites, prochaines étapes (slides 10-11)

Chaque titre de slide énonce un **message** et non un sujet : « De 3 665 indicateurs à 5 » plutôt que
« Nettoyage des données ».
