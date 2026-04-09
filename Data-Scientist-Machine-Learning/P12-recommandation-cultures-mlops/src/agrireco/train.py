"""Étape « train » : comparaison, optimisation des hyperparamètres et sélection, suivies dans MLflow.

Trois expériences MLflow :
- p12-01-comparaison : référence, Ridge, forêt aléatoire, gradient boosting avec leurs réglages de départ ;
- p12-02-optimisation : recherche systématique (grille pour Ridge, 30 tirages aléatoires pour les arbres),
  un run enfant par configuration essayée ;
- p12-03-variantes-variables : le modèle retenu avec moins de variables (ce qu'ajoute chacune).
Tous les modèles sont évalués sur les **mêmes plis**, groupés par pays : les comparaisons sont appariées.
"""

import json
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import make_scorer
from sklearn.model_selection import GridSearchCV, GroupKFold, RandomizedSearchCV, cross_validate

from agrireco import metrics, modeling, prepare, split

RMSE_LOG = make_scorer(metrics.rmse_log, greater_is_better=False)
EXPERIMENTS = {
    "comparison": "p12-01-comparaison",
    "search": "p12-02-optimisation",
    "variants": "p12-03-variantes-variables",
}


def setup_mlflow(mlruns: Path) -> None:
    mlruns.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(f"sqlite:///{mlruns / 'mlflow.db'}")


def _experiment(name: str, mlruns: Path) -> None:
    """Active l'expérience.

    Les runs d'une exécution précédente du pipeline sont archivés (suppression logique, récupérable dans
    l'interface) : l'expérience reflète toujours la dernière exécution, et les captures aussi.
    """
    exp = mlflow.get_experiment_by_name(name)
    if exp is None:
        mlflow.create_experiment(name, artifact_location=(mlruns / "artifacts" / name).as_uri())
    else:
        for run_id in mlflow.search_runs([exp.experiment_id])["run_id"]:
            mlflow.delete_run(run_id)
    mlflow.set_experiment(name)


def load_train_test(cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    path = cfg["paths"]["processed"] / "dataset_consolide.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} introuvable : lancer d'abord `agrireco prepare`.")
    df = prepare.add_model_features(pd.read_csv(path))
    return split.group_test_split(df, cfg["split"]["test_size"], cfg["seed"])


def group_folds(train: pd.DataFrame, n_splits: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    cv = GroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    return list(cv.split(train, groups=train["country"]))


def cv_scores(model, train: pd.DataFrame, folds) -> dict[str, np.ndarray]:
    """RMSE-log par pli, en validation et en entraînement (pour l'écart)."""
    res = cross_validate(
        model, train, train["yield_t_ha"], cv=folds, scoring=RMSE_LOG, return_train_score=True
    )
    return {"val": -res["test_score"], "train": -res["train_score"]}


def _log_cv(scores: dict[str, np.ndarray]) -> None:
    mlflow.log_metrics(
        {
            "cv_rmse_log_mean": float(scores["val"].mean()),
            "cv_rmse_log_std": float(scores["val"].std(ddof=1)),
            "train_rmse_log_mean": float(scores["train"].mean()),
            "gap_val_minus_train": float(scores["val"].mean() - scores["train"].mean()),
        }
    )
    for i, s in enumerate(scores["val"]):
        mlflow.log_metric("cv_rmse_log_fold", float(s), step=i)


def run_comparison(cfg, train, folds) -> dict[str, np.ndarray]:
    _experiment(EXPERIMENTS["comparison"], cfg["paths"]["mlruns"])
    out = {}
    for name, params in cfg["models"].items():
        with mlflow.start_run(run_name=f"{name}-depart"):
            mlflow.set_tags(
                {"etape": "comparaison", "modele": name, "mlflow.note.content": f"{name}, réglages de départ"}
            )
            mlflow.log_params(
                {"modele": name, "features": ",".join(cfg["features"]), "seed": cfg["seed"], **params}
            )
            model = modeling.build_model(name, params, cfg["features"], cfg["seed"])
            scores = cv_scores(model, train, folds)
            _log_cv(scores)
            out[name] = scores["val"]
    return out


def _search(name: str, cfg: dict, folds):
    space = {f"regressor__model__{k}": v for k, v in cfg["search"][name].items()}
    model = modeling.build_model(name, {}, cfg["features"], cfg["seed"])
    common = {"scoring": RMSE_LOG, "cv": folds, "return_train_score": True, "n_jobs": -1, "refit": False}
    if name == "ridge":
        return GridSearchCV(model, space, **common)
    return RandomizedSearchCV(
        model, space, n_iter=cfg["search"]["n_iter"], random_state=cfg["seed"], **common
    )


def run_search(cfg, train, folds) -> dict[str, dict]:
    """Optimise Ridge et les deux modèles d'arbres.

    Renvoie, par modèle, le meilleur réglage et ses scores par pli.
    """
    _experiment(EXPERIMENTS["search"], cfg["paths"]["mlruns"])
    best = {}
    for name in ("ridge", "random_forest", "hist_gb"):
        search = _search(name, cfg, folds)
        search.fit(train, train["yield_t_ha"])
        res = pd.DataFrame(search.cv_results_)
        n_folds = len(folds)
        with mlflow.start_run(run_name=f"{name}-recherche") as parent:
            mlflow.set_tags({"etape": "optimisation", "modele": name, "methode": type(search).__name__})
            for i, row in res.iterrows():
                params = {
                    k.removeprefix("param_regressor__model__"): row[k] for k in res if k.startswith("param_")
                }
                with mlflow.start_run(run_name=f"{name}-essai-{i:02d}", nested=True):
                    mlflow.set_tags({"etape": "optimisation", "modele": name, "parent": parent.info.run_id})
                    mlflow.log_params({"modele": name, **params})
                    mlflow.log_metrics(
                        {
                            "cv_rmse_log_mean": -row["mean_test_score"],
                            "cv_rmse_log_std": row["std_test_score"],
                            "train_rmse_log_mean": -row["mean_train_score"],
                            "gap_val_minus_train": row["mean_train_score"] - row["mean_test_score"],
                        }
                    )
            i_best = int(res["rank_test_score"].idxmin())
            params = {k.removeprefix("regressor__model__"): v for k, v in res.loc[i_best, "params"].items()}
            folds_val = np.array([-res.loc[i_best, f"split{f}_test_score"] for f in range(n_folds)])
            folds_train = np.array([-res.loc[i_best, f"split{f}_train_score"] for f in range(n_folds)])
            mlflow.log_params({f"best_{k}": v for k, v in params.items()})
            _log_cv({"val": folds_val, "train": folds_train})
            mlflow.set_tag(
                "mlflow.note.content", f"Meilleur réglage {name} sur {len(res)} essais (CV groupée par pays)"
            )
        best[name] = {
            "params": _jsonable(params),
            "folds": folds_val.tolist(),
            "train_folds": folds_train.tolist(),
        }
    return best


def run_variants(cfg, train, folds, name: str, params: dict) -> dict[str, np.ndarray]:
    _experiment(EXPERIMENTS["variants"], cfg["paths"]["mlruns"])
    out = {}
    for variant, features in cfg["feature_variants"].items():
        with mlflow.start_run(run_name=f"{name}-{variant}"):
            mlflow.set_tags({"etape": "variantes", "modele": name, "variante": variant})
            mlflow.log_params({"modele": name, "features": ",".join(features), **params})
            scores = cv_scores(modeling.build_model(name, params, features, cfg["seed"]), train, folds)
            _log_cv(scores)
            out[variant] = scores["val"]
    return out


def _jsonable(params: dict) -> dict:
    return {k: (v.item() if hasattr(v, "item") else v) for k, v in params.items()}


def run_train(cfg: dict) -> dict:
    setup_mlflow(cfg["paths"]["mlruns"])
    train, test = load_train_test(cfg)
    folds = group_folds(train, cfg["split"]["cv_folds"], cfg["seed"])
    comparison = run_comparison(cfg, train, folds)
    best = run_search(cfg, train, folds)
    candidates = {"baseline": comparison["baseline"], **{k: np.array(v["folds"]) for k, v in best.items()}}
    selected = modeling.select_model(candidates)
    params = best.get(selected, {}).get("params", {})
    variants = run_variants(cfg, train, folds, selected, params)
    selection = {
        "selected": selected,
        "params": params,
        "n_train_countries": int(train["country"].nunique()),
        "n_test_countries": int(test["country"].nunique()),
        "n_train_rows": len(train),
        "n_test_rows": len(test),
        "test_countries": sorted(test["country"].unique()),
        "test_crops": int(test["crop"].nunique()),
        "comparison_folds": {k: v.tolist() for k, v in comparison.items()},
        "search": best,
        "candidate_folds": {k: np.asarray(v).tolist() for k, v in candidates.items()},
        "variant_folds": {k: v.tolist() for k, v in variants.items()},
    }
    out = cfg["paths"]["processed"] / "selection.json"
    out.write_text(json.dumps(selection, indent=2, ensure_ascii=False), encoding="utf-8")
    return selection
