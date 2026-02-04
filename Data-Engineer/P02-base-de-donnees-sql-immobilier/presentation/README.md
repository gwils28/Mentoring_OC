# Présentation — livrable 2 du corrigé

| Fichier | Rôle |
|---|---|
| `dataimmo_laplace_immo.pptx` | support de présentation (23 slides, avec des notes orateur sur chaque slide) |
| `export_resultats.py` | exporte de la base le SQL et le résultat de chaque besoin, les comptages et un aperçu des tables |
| `resultats.json` | sortie de l'export, lue par `build_deck.js` |
| `build_deck.js` | génère le `.pptx` : thème, layouts, sections et contenu |
| `theme_colors.js` | injecte la palette dans le thème PowerPoint |
| `figures/` | schéma relationnel généré depuis `sql/schema.sql` |

```bash
uv run python presentation/export_resultats.py   # depuis le dossier du projet
cd presentation && npm ci && npm run build
```

Aucun chiffre n'est saisi à la main dans les tableaux : ils viennent de la base. Les phrases de lecture reprennent
le notebook corrigé, et `build_deck.js` s'arrête si un chiffre qu'elles citent ne correspond plus à `resultats.json`.

## Structure (rubriques attendues par OpenClassrooms)

1. **Contexte** : le POC de Laplace Immo (slides 1-2)
2. **Transformation des données** : sources, pièges, extrait du dictionnaire, schéma 3NF (slides 3-5)
3. **La base** : aperçu des tables (à la place d'une capture d'écran), preuve du chargement par `COUNT(*)`,
   RGPD et sauvegarde (slides 6-8)
4. **Les 12 besoins** : une slide par besoin (deux pour le besoin 11, dont la requête est longue), avec la requête, le résultat et une
   phrase métier (slides 9-21)
5. **Conclusion** : trois messages pour la direction, limites et prochaines étapes (slides 22-23)

Chaque titre de slide énonce un **message** et non un sujet : « L'Île-de-France concentre 45 % des appartements
vendus » plutôt que « Besoin 2 ».
