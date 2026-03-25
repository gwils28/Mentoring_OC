# Présentation — livrable 2 du corrigé

| Fichier | Rôle |
|---|---|
| `segmentation_vetements_modetrends.pptx` | support de présentation (9 slides, notes orateur sur chaque slide) |
| `export_resultats.py` | recalcule depuis le cache les chiffres cités (IoU, latence, coûts…) |
| `resultats.json` | sortie de l'export, lue par `build_deck.js` |
| `build_deck.js` | génère le `.pptx` : thème, layouts, sections et contenu |
| `theme_colors.js` | injecte la palette dans le thème PowerPoint |
| `figures/` | figures exportées par le notebook corrigé (visages floutés) |

```bash
uv run python presentation/export_resultats.py   # depuis le dossier du projet
cd presentation && npm ci && npm run build
```

Aucun chiffre n'est saisi à la main : ceux des slides viennent de `resultats.json`, et `build_deck.js` s'arrête si
un chiffre cité dans une phrase ne correspond plus à l'export.

## Structure : la trame du support fourni par OpenClassrooms

Le deck suit les rubriques du modèle de présentation remis à l'apprenant, dans le même ordre, sans en reprendre le
texte (le modèle n'est pas redistribué ici).

1. **Titre** : la réponse en trois mots (faisable, prometteur, peu coûteux) — slide 1
2. **Le projet** : la mission dans le projet global, les deux questions — slide 2
3. **Fonctionnement** : de la photo à la carte des vêtements, et la robustesse du client — slide 3
4. **Performances** : mIoU vêtements, IoU par famille, meilleur et pire cas — slides 4 et 5
5. **Méthode de validation** : la fuite de données, et le protocole train / val / test proposé — slide 6
6. **Passage à l'échelle et coût** : trois façons de payer pour 500 000 images — slide 7
7. **Conformité** (rubrique optionnelle) : RGPD, AI Act — slide 8
8. **Bilan** : recommandation et prochaines étapes — slide 9

Chaque titre énonce un **message** (« Les erreurs viennent surtout de vêtements ambigus ») plutôt qu'un sujet
(« Résultats »). Contrôle visuel : ouvrir le `.pptx` dans PowerPoint (pas de rendu automatique sur cette machine).
