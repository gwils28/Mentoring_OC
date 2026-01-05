# CLAUDE.md — Mentoring_OC

Supports de mentorat OpenClassrooms : un dossier par parcours, un sous-dossier `Pxx-nom-du-projet` par projet.
Public visé : apprenants **débutants**. Tout le contenu est en français.

## Règles

- `_mentor_notes/` (énoncés et guides mentor OC) est **gitignoré** : contenu réservé aux mentors. Ne jamais le
  copier ailleurs dans le repo ; le kit mentor reformule.
- `data/raw/` est gitignoré : chaque projet télécharge ses données et vérifie leur SHA-256 (`src/<pkg>/io.py`).
  Si l'empreinte change, les chiffres des supports ne sont plus garantis.
- Chaque projet est un projet `uv` autonome (`pyproject.toml` + `uv.lock` dans son dossier, Python 3.12).
- Les notebooks sont versionnés **exécutés** : les relancer après toute modification du code.
- Toute affirmation chiffrée d'un support (README, kit, slides, page web) doit provenir d'une sortie du notebook
  ou de `data/processed/` : on vérifie avant d'écrire.
- Chaque projet contient un `PLAN.md`, figé avant les résultats ; les écarts vont dans le README (« ce qui a changé
  par rapport au plan »).

## Commandes (depuis le dossier d'un projet)

```bash
uv sync --frozen                         # environnement exact
uv run pytest                            # tests du package
uv run ruff check src tests && uv run ruff format --check src tests
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/*.ipynb pedagogie/*.ipynb
```

## Pièges

- Les notebooks importent le package du projet (`edstats`, …) : lancer Jupyter via `uv run`, sinon `ImportError`.
- pandas 3 : copy-on-write activé et dtype `str` par défaut ; `fillna("")` sur une colonne float émet un warning.
