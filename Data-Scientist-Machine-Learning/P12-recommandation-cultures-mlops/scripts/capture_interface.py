"""Captures de l'interface Streamlit branchée sur l'API (présentation, README).

    uv run python scripts/capture_interface.py

Lance l'API (uvicorn) et l'interface (Streamlit) en local, pilote Chrome sans interface, enregistre
`presentation/figures/interface_prediction.png` et `interface_recommandation.png`, puis arrête tout.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from captures_mlflow import FIGURES, PROJECT, Browser, _free_port, _wait  # noqa: E402


def main() -> None:
    api_port, app_port = _free_port(), _free_port()
    env = {**os.environ, "API_URL": f"http://127.0.0.1:{api_port}"}
    api = subprocess.Popen(
        ["uvicorn", "api.main:app", "--port", str(api_port)], cwd=PROJECT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )  # fmt: skip
    app = subprocess.Popen(
        ["streamlit", "run", "app/app.py", "--server.port", str(app_port), "--server.headless", "true",
         "--browser.gatherUsageStats", "false"],
        cwd=PROJECT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )  # fmt: skip
    browser = None
    try:
        _wait(f"http://127.0.0.1:{api_port}/health")
        _wait(f"http://127.0.0.1:{app_port}")
        browser = Browser(width=1100, height=1300)
        url = f"http://127.0.0.1:{app_port}"

        browser.goto(url, wait=6)
        browser.click_text("Interroger le modèle")
        time.sleep(4)
        browser.shot(FIGURES / "interface_prediction.png")

        browser.goto(url, wait=6)
        browser.js(
            "(() => { const l = [...document.querySelectorAll('label')]"
            ".find(e => e.innerText.trim() === 'Recommandation'); if (l) l.click(); })()"
        )
        time.sleep(2)
        browser.click_text("Interroger le modèle")
        time.sleep(5)
        browser.shot(FIGURES / "interface_recommandation.png")
    finally:
        if browser:
            browser.close()
        app.terminate()
        api.terminate()


if __name__ == "__main__":
    main()
