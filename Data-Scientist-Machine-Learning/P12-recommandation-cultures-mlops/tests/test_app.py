"""L'interface ne contient aucune logique de machine learning : elle se contente d'appeler l'API."""

import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app" / "app.py"
FORBIDDEN = {"sklearn", "joblib", "agrireco", "mlflow", "numpy"}


def test_app_imports_no_ml_library():
    tree = ast.parse(APP.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module.split(".")[0])
    assert imported.isdisjoint(FORBIDDEN), imported & FORBIDDEN
