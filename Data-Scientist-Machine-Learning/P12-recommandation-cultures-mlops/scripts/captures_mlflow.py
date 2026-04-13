"""Livrable 1 : captures d'écran de l'interface MLflow, régénérables, et export des runs en CSV.

À lancer après `agrireco all` (les identifiants de runs changent à chaque entraînement) :

    uv run python scripts/captures_mlflow.py

Démarre un serveur MLflow local, pilote Chrome sans interface (protocole DevTools) puis enregistre
`presentation/figures/mlflow_*.png` et `data/processed/mlflow_runs.csv` (les chiffres visibles sur les
captures). Nécessite Google Chrome.
"""

import base64
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

import mlflow  # noqa: E402
import websocket  # noqa: E402

PROJECT = Path(__file__).resolve().parents[1]
DB = PROJECT / "mlruns" / "mlflow.db"
FIGURES = PROJECT / "presentation" / "figures"
EXPORT = PROJECT / "data" / "processed" / "mlflow_runs.csv"
METRIC = "metrics.%60cv_rmse_log_mean%60"
# Colonnes ajoutées ; les attributs par défaut (Dataset, Source, Models) sont décochés pour laisser la place
METRICS = [
    "Dataset",
    "Source",
    "Models",
    "cv_rmse_log_mean",
    "cv_rmse_log_std",
    "train_rmse_log_mean",
    "gap_val_minus_train",
]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait(url: str, timeout: float = 60) -> None:
    end = time.time() + timeout
    while time.time() < end:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except OSError:
            time.sleep(0.3)
    raise TimeoutError(url)


class Browser:
    """Chrome sans interface, piloté par le protocole DevTools (pas de dépendance à Selenium)."""

    def __init__(self, width: int = 1920, height: int = 900):
        self.port, self.profile = _free_port(), tempfile.mkdtemp()
        chrome = shutil.which("google-chrome") or shutil.which("chromium")
        if chrome is None:
            raise SystemExit("Google Chrome ou Chromium introuvable : nécessaire pour ce script.")
        self.proc = subprocess.Popen(
            [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             f"--remote-debugging-port={self.port}", "--remote-allow-origins=*",
             f"--user-data-dir={self.profile}", "about:blank"],
            stderr=subprocess.DEVNULL,
        )  # fmt: skip
        _wait(f"http://127.0.0.1:{self.port}/json/version")
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json"))
        page = next(t for t in tabs if t["type"] == "page")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], suppress_origin=True)
        self.n = 0
        self.cmd(
            "Emulation.setDeviceMetricsOverride",
            width=width,
            height=height,
            deviceScaleFactor=1,
            mobile=False,
        )

    def cmd(self, method: str, **params):
        self.n += 1
        self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.n:
                return msg.get("result", {})

    def js(self, expression: str):
        return (
            self.cmd("Runtime.evaluate", expression=expression, returnByValue=True)
            .get("result", {})
            .get("value")
        )

    def click_text(self, text: str, attr: bool = False) -> bool:
        test = (
            f"b.getAttribute('aria-label') === {text!r}"
            if attr
            else f"b.innerText.trim().startsWith({text!r})"
        )
        sel = f"[...document.querySelectorAll('button,[role=button]')].find(b => {test})"
        return bool(
            self.js(f"(() => {{ const b = {sel}; if (b) {{ b.click(); return true }} return false }})()")
        )

    def show_columns(self, names: list[str]) -> None:
        """Ouvre le menu « Columns », bascule les colonnes demandées, referme le menu."""
        self.click_text("Columns")
        time.sleep(1)
        for name in names:
            # Menu en arbre : on coche la case située juste avant le libellé de la colonne
            self.js(
                "(() => { const t = [...document.querySelectorAll('[class*=tree-node-content-wrapper]')]"
                f".find(e => e.innerText.trim() === {name!r}); if (!t) return;"
                " const box = t.parentElement.querySelector('[class*=tree-checkbox]');"
                " (box || t).click(); })()"
            )
            time.sleep(0.3)
        self.cmd(
            "Input.dispatchKeyEvent", type="keyDown", key="Escape", code="Escape", windowsVirtualKeyCode=27
        )
        self.cmd(
            "Input.dispatchKeyEvent", type="keyUp", key="Escape", code="Escape", windowsVirtualKeyCode=27
        )
        time.sleep(1)

    def goto(self, url: str, wait: float = 5) -> None:
        self.cmd("Page.navigate", url=url)
        time.sleep(wait)
        self.click_text("Close", attr=True)  # panneau « Assistant » de MLflow, inutile sur une capture
        time.sleep(0.5)

    def shot(self, path: Path) -> None:
        data = self.cmd("Page.captureScreenshot", format="png")["data"]
        path.write_bytes(base64.b64decode(data))
        print("capture :", path.relative_to(PROJECT))

    def close(self) -> None:
        self.proc.kill()
        shutil.rmtree(self.profile, ignore_errors=True)


def export_runs() -> dict[str, str]:
    """Exporte les runs (paramètres, métriques) en CSV et renvoie les identifiants utiles aux captures."""
    mlflow.set_tracking_uri(f"sqlite:///{DB}")
    experiments = {e.name: e.experiment_id for e in mlflow.search_experiments() if e.name.startswith("p12-")}
    runs = mlflow.search_runs(list(experiments.values()))
    names = {v: k for k, v in experiments.items()}
    runs.insert(0, "experiment", runs["experiment_id"].map(names))
    keep = ["experiment", "tags.mlflow.runName", "run_id"] + [
        c for c in runs if c.startswith(("params.", "metrics."))
    ]
    runs[keep].sort_values(["experiment", "tags.mlflow.runName"]).to_csv(EXPORT, index=False)
    print("export :", EXPORT.relative_to(PROJECT), f"({len(runs)} runs)")
    latest = runs.sort_values("start_time", ascending=False).drop_duplicates("tags.mlflow.runName")
    by_name = dict(zip(latest["tags.mlflow.runName"], latest["run_id"], strict=True))
    return {"experiments": experiments, "runs": by_name}


def main() -> None:
    if not DB.exists():
        raise SystemExit(f"{DB} introuvable : lancer d'abord `uv run agrireco all`.")
    FIGURES.mkdir(parents=True, exist_ok=True)
    ids = export_runs()
    exp, runs = ids["experiments"], ids["runs"]
    port = _free_port()
    env = {**os.environ, "MLFLOW_DISABLE_AGENT_HINT": "1"}
    server = subprocess.Popen(
        ["mlflow", "server", "--backend-store-uri", f"sqlite:///{DB}",
         "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env,
    )  # fmt: skip
    base = f"http://127.0.0.1:{port}"
    browser = None
    try:
        _wait(f"{base}/health")
        browser = Browser()
        sort = f"?orderByKey={METRIC}&orderByAsc=true"

        # 1. Liste des runs de la comparaison, métriques en colonnes, triés par RMSE-log
        browser.goto(f"{base}/#/experiments/{exp['p12-01-comparaison']}/runs{sort}")
        browser.click_text("Model training")
        time.sleep(1)
        browser.show_columns(METRICS + ["alpha", "n_estimators"])
        browser.shot(FIGURES / "mlflow_1_comparaison.png")

        # 2. Optimisation : les 3 recherches et leurs 65 essais, triés par RMSE-log
        browser.goto(f"{base}/#/experiments/{exp['p12-02-optimisation']}/runs{sort}")
        browser.show_columns(METRICS + ["modele", "min_samples_leaf", "max_depth", "learning_rate"])
        browser.shot(FIGURES / "mlflow_2_optimisation.png")

        # 3. Comparaison côte à côte : référence + meilleurs réglages des 3 modèles optimisés
        compare = [runs["baseline-depart"], runs["ridge-recherche"], runs["random_forest-recherche"],
                   runs["hist_gb-recherche"]]  # fmt: skip
        exps = [exp["p12-01-comparaison"], exp["p12-02-optimisation"]]
        browser.goto(
            f"{base}/#/compare-runs?runs={json.dumps(compare)}&experiments={json.dumps(exps)}", wait=6
        )
        # Le tableau des paramètres et métriques est sous le graphique : on capture une page plus haute
        browser.cmd(
            "Emulation.setDeviceMetricsOverride", width=1920, height=2000, deviceScaleFactor=1, mobile=False
        )
        time.sleep(2)
        browser.shot(FIGURES / "mlflow_3_comparaison_modeles.png")
        browser.cmd(
            "Emulation.setDeviceMetricsOverride", width=1920, height=900, deviceScaleFactor=1, mobile=False
        )

        # 4. Variantes de variables
        browser.goto(f"{base}/#/experiments/{exp['p12-03-variantes-variables']}/runs{sort}")
        browser.show_columns(METRICS + ["features"])
        browser.shot(FIGURES / "mlflow_4_variantes.png")

        # 5. Détail du run final : paramètres, métriques du test, modèle enregistré
        final = next(k for k in runs if k.endswith("-test-final"))
        browser.goto(f"{base}/#/experiments/{exp['p12-04-modele-final']}/runs/{runs[final]}", wait=6)
        browser.shot(FIGURES / "mlflow_5_run_final.png")
    finally:
        if browser:
            browser.close()
        server.terminate()


if __name__ == "__main__":
    main()
