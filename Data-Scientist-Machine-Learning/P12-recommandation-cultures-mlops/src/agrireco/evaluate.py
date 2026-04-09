"""Étape « evaluate » : test unique sur les pays mis de côté, recommandation, sensibilité, modèle servi.

Lit `selection.json` (produit par « train »), écrit `resultats.json` et les tables détaillées dans
data/processed/, et le paquet servi par l'API dans models/. Expérience MLflow : p12-04-modele-final.
"""

import json

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_score

from agrireco import metrics, modeling, prepare, recommend, split
from agrireco.domain import fit_domain
from agrireco.service import Bundle, save_bundle
from agrireco.train import RMSE_LOG, _experiment, load_train_test, setup_mlflow

PERMUTED = {
    "culture": ["crop"],
    "température": ["avg_temp"],
    "pluie": ["rainfall_mm"],
    "pesticides": ["log10_pesticides_t"],
    "bloc climat + pesticides": ["avg_temp", "rainfall_mm", "log10_pesticides_t"],
}


def permutation_importance(model, test: pd.DataFrame, repeats: int, seed: int) -> pd.DataFrame:
    """Hausse de la RMSE-log quand on mélange une variable (ou un bloc, mélangé d'un seul tenant)."""
    rng = np.random.default_rng(seed)
    base = metrics.rmse_log(test["yield_t_ha"], model.predict(test))
    rows = []
    for name, cols in PERMUTED.items():
        for r in range(repeats):
            perm = rng.permutation(len(test))
            shuffled = test.copy()
            shuffled[cols] = test[cols].to_numpy()[perm]
            rows.append(
                {
                    "variable": name,
                    "repetition": r,
                    "hausse_rmse_log": metrics.rmse_log(test["yield_t_ha"], model.predict(shuffled)) - base,
                }
            )
    return pd.DataFrame(rows).groupby("variable")["hausse_rmse_log"].agg(["mean", "std"]).reset_index()


def _with_relative(df: pd.DataFrame, pred: np.ndarray, reference: pd.Series) -> pd.DataFrame:
    ref = df["crop"].map(reference).to_numpy()
    return df.assign(pred=pred, rel_obs=df["yield_t_ha"].to_numpy() / ref, rel_pred=pred / ref)


def recommendation_eval(
    train: pd.DataFrame, test: pd.DataFrame, pred: np.ndarray, cfg: dict, by_country=True
):
    """Évalue le classement du modèle face au hasard, au classement constant et à l'oracle."""
    reference = recommend.reference_yields(train, by_country=by_country)
    train_rel = train.assign(rel_obs=train["yield_t_ha"] / train["crop"].map(reference))
    t = _with_relative(test, pred, reference)
    t["const_score"] = recommend.constant_scores(t["crop"], recommend.constant_order(train_rel)).to_numpy()
    k = cfg["recommendation"]["min_crops"]
    g_model = recommend.evaluate_groups(t, "rel_pred", k)
    g_const = recommend.evaluate_groups(t, "const_score", k)
    g = g_model.merge(
        g_const[["country", "year", "top1_ok", "gain", "recommended"]],
        on=["country", "year"],
        suffixes=("", "_const"),
    )
    return t, g, reference


def filtered_eval(train: pd.DataFrame, t_rel: pd.DataFrame, cfg: dict) -> dict:
    """Règle produit de l'application (ajoutée après les résultats) : les cultures qu'aucun pays
    d'entraînement aux conditions proches ne pratique passent en fin de classement. Évaluée ici à titre
    exploratoire, sur les mêmes groupes du test."""
    domain = fit_domain(train)
    ctx = t_rel[["avg_temp", "rainfall_mm", "log10_pesticides_t"]].to_dict(orient="records")
    supported = np.array([domain.crop_supported(c, crop) for c, crop in zip(ctx, t_rel["crop"], strict=True)])
    t = t_rel.assign(score_filtre=t_rel["rel_pred"] - 1e6 * (~supported))
    g = recommend.evaluate_groups(t, "score_filtre", cfg["recommendation"]["min_crops"])
    gc = recommend.evaluate_groups(t, "const_score", cfg["recommendation"]["min_crops"])
    g = g.merge(gc[["country", "year", "top1_ok"]], on=["country", "year"], suffixes=("", "_const"))
    return {
        "filtre_part_lignes_test_non_appuyees": float((~supported).mean()),
        "filtre_taux_top1": float(g["top1_ok"].mean()),
        "filtre_diff_moins_constant_ic95": _boot(g, _diff_vs_constant, cfg),
    }


def _diff_vs_constant(g: pd.DataFrame) -> float:
    """Différence appariée de taux de bonne 1ʳᵉ place : modèle − classement constant."""
    return (g["top1_ok"].astype(float) - g["top1_ok_const"].astype(float)).mean()


def _boot(g, stat, cfg):
    return recommend.bootstrap_by_country(
        g, stat, cfg["recommendation"]["bootstrap"], cfg["recommendation"]["bootstrap_seed"]
    )


def run_evaluate(cfg: dict) -> dict:
    processed, seed = cfg["paths"]["processed"], cfg["seed"]
    setup_mlflow(cfg["paths"]["mlruns"])
    sel_path = processed / "selection.json"
    if not sel_path.exists():
        raise FileNotFoundError(f"{sel_path} introuvable : lancer d'abord `agrireco train`.")
    selection = json.loads(sel_path.read_text(encoding="utf-8"))
    name, params, features = selection["selected"], selection["params"], cfg["features"]
    train, test = load_train_test(cfg)
    if sorted(test["country"].unique()) != selection["test_countries"]:
        raise ValueError(
            "Le découpage des pays a changé depuis « train » (seed ou test_size modifiés ?) : relancer train."
        )

    # 1. Test unique sur les pays jamais vus
    model = modeling.build_model(name, params, features, seed).fit(train, train["yield_t_ha"])
    pred = model.predict(test)
    pred_train = model.predict(train)
    test_m = metrics.all_metrics(test["yield_t_ha"], pred)
    t = test.assign(pred=pred)
    per_crop = metrics.by_group(t, "crop")
    per_crop.to_csv(processed / "test_par_culture.csv", index=False)
    boot_rmse = recommend.bootstrap_by_country(
        t,
        lambda d: metrics.rmse_log(d["yield_t_ha"], d["pred"]),
        cfg["recommendation"]["bootstrap"],
        cfg["recommendation"]["bootstrap_seed"],
    )

    # Modèle « culture seule » (même famille, mêmes réglages) : ce qu'apportent les conditions
    crop_only = modeling.build_model(name, params, ["crop"], seed).fit(train, train["yield_t_ha"])
    crop_only_rmse = metrics.rmse_log(test["yield_t_ha"], crop_only.predict(test))
    baseline = modeling.build_model("baseline", {}, features).fit(train, train["yield_t_ha"])
    baseline_m = metrics.all_metrics(test["yield_t_ha"], baseline.predict(test))

    # Contre-exemple : validation croisée ALÉATOIRE (lignes mélangées, un pays des deux côtés)
    full = pd.concat([train, test], ignore_index=True)
    random_cv = -cross_val_score(
        modeling.build_model(name, params, features, seed),
        full,
        full["yield_t_ha"],
        cv=KFold(cfg["split"]["cv_folds"], shuffle=True, random_state=seed),
        scoring=RMSE_LOG,
        n_jobs=-1,
    )

    importance = permutation_importance(model, test, cfg["recommendation"]["permutation_repeats"], seed)
    importance.to_csv(processed / "importance_permutation.csv", index=False)

    # 2. Recommandation
    t_rel, groups, reference = recommendation_eval(train, test, pred, cfg)
    groups.to_csv(processed / "recommandation_groupes.csv", index=False)
    _, groups_rows, _ = recommendation_eval(train, test, pred, cfg, by_country=False)
    diff_ci = _boot(groups, _diff_vs_constant, cfg)
    reco = {
        "n_pays_evalues": int(groups["country"].nunique()),
        "n_pays_annees": len(groups),
        "cultures_par_groupe_moyenne": float(groups["k"].mean()),
        "taux_top1_modele": float(groups["top1_ok"].mean()),
        "taux_top1_modele_ic95": _boot(groups, lambda d: d["top1_ok"].mean(), cfg),
        "taux_top1_constant": float(groups["top1_ok_const"].mean()),
        "taux_top1_hasard": float(groups["chance"].mean()),
        "diff_modele_moins_constant": float(groups["top1_ok"].mean() - groups["top1_ok_const"].mean()),
        "diff_modele_moins_constant_ic95": diff_ci,
        "modele_utile_pour_recommander": bool(diff_ci[0] > 0),
        "gain_modele": float(groups["gain"].mean()),
        "gain_constant": float(groups["gain_const"].mean()),
        "gain_oracle": float(groups["oracle_gain"].mean()),
        "kendall_modele": recommend.kendall_by_country(t_rel, "rel_pred", cfg["recommendation"]["min_crops"]),
        "kendall_constant": recommend.kendall_by_country(
            t_rel, "const_score", cfg["recommendation"]["min_crops"]
        ),
        "repartition_recommandations": groups["recommended"].value_counts().to_dict(),
        "repartition_constant": groups["recommended_const"].value_counts().to_dict(),
        "taux_top1_modele_normaliseur_lignes": float(groups_rows["top1_ok"].mean()),
        "taux_top1_constant_normaliseur_lignes": float(groups_rows["top1_ok_const"].mean()),
        "diff_normaliseur_lignes_ic95": _boot(groups_rows, _diff_vs_constant, cfg),
        "pays_ou_modele_et_constant_different": int(
            groups.assign(diff=groups["recommended"] != groups["recommended_const"])
            .groupby("country")["diff"]
            .any()
            .sum()
        ),
        "part_groupes_meme_recommandation": float(
            (groups["recommended"] == groups["recommended_const"]).mean()
        ),
        **filtered_eval(train, t_rel, cfg),
    }

    # Analyse complémentaire (ajoutée après la sélection, déclarée dans le README) :
    # (a) optimisme de la validation aléatoire pour chaque famille de modèle ;
    # (b) un modèle NON additif (arbres optimisés) recommanderait-il mieux que le classement constant ?
    others = {}
    for other, other_params in [
        ("random_forest", cfg["models"]["random_forest"]),
        ("hist_gb", cfg["models"]["hist_gb"]),
        *[(k, v["params"]) for k, v in selection["search"].items()],
    ]:
        label = f"{other}_{'optimise' if other_params == selection['search'][other]['params'] else 'depart'}"
        rnd = -cross_val_score(
            modeling.build_model(other, other_params, features, seed),
            full,
            full["yield_t_ha"],
            cv=KFold(cfg["split"]["cv_folds"], shuffle=True, random_state=seed),
            scoring=RMSE_LOG,
            n_jobs=-1,
        )
        entry = {"cv_aleatoire_rmse_log": float(rnd.mean())}
        if label.endswith("optimise"):
            entry["cv_par_pays_rmse_log"] = float(np.mean(selection["search"][other]["folds"]))
            if other != "ridge":
                m = modeling.build_model(other, other_params, features, seed).fit(train, train["yield_t_ha"])
                p = m.predict(test)
                _, go, _ = recommendation_eval(train, test, p, cfg)
                entry |= {
                    "test_rmse_log": metrics.rmse_log(test["yield_t_ha"], p),
                    "taux_top1": float(go["top1_ok"].mean()),
                    "diff_moins_constant": float(go["top1_ok"].mean() - go["top1_ok_const"].mean()),
                    "diff_moins_constant_ic95": _boot(go, _diff_vs_constant, cfg),
                    "repartition_recommandations": go["recommended"].value_counts().to_dict(),
                }
        else:
            entry["cv_par_pays_rmse_log"] = float(np.mean(selection["comparison_folds"][other]))
        others[label] = entry

    # 3. Sensibilité au tirage des pays (même configuration, sans nouveau réglage)
    sens = []
    for s in range(cfg["split"]["sensitivity_splits"]):
        tr, te = split.group_test_split(full, cfg["split"]["test_size"], s)
        m = modeling.build_model(name, params, features, seed).fit(tr, tr["yield_t_ha"])
        p = m.predict(te)
        _, gs, _ = recommendation_eval(tr, te, p, cfg)
        sens.append(
            {
                "graine": s,
                "rmse_log": metrics.rmse_log(te["yield_t_ha"], p),
                "top1_modele": gs["top1_ok"].mean(),
                "top1_constant": gs["top1_ok_const"].mean(),
                "bias_t_ha": metrics.bias(te["yield_t_ha"], p),
            }
        )
    sens = pd.DataFrame(sens)
    sens.to_csv(processed / "sensibilite_decoupage.csv", index=False)

    # 4. Modèle servi : même configuration, réentraînée sur tous les pays
    served = modeling.build_model(name, params, features, seed).fit(full, full["yield_t_ha"])
    bundle = Bundle(
        model=served,
        reference={str(k): float(v) for k, v in recommend.reference_yields(full).items()},
        crops=[str(c) for c in sorted(full["crop"].unique())],
        domain=fit_domain(full),
        metadata={
            "modele": name,
            "params": params,
            "features": features,
            "n_lignes": len(full),
            "periode": [int(full["year"].min()), int(full["year"].max())],
        },
    )
    save_bundle(bundle, cfg["paths"]["models"] / "model.joblib")

    results = {
        "modele": name,
        "params": params,
        "donnees": {
            "lignes": len(full),
            "pays": int(full["country"].nunique()),
            "cultures": int(full["crop"].nunique()),
            "annees": [int(full["year"].min()), int(full["year"].max())],
            "pays_entrainement": selection["n_train_countries"],
            "pays_test": selection["n_test_countries"],
            "lignes_test": len(test),
            "cultures_test": int(test["crop"].nunique()),
        },
        "cv": {
            k: {"moyenne": float(np.mean(v)), "ecart_type": float(np.std(v, ddof=1))}
            for k, v in selection["candidate_folds"].items()
        },
        "cv_variantes": {
            k: {"moyenne": float(np.mean(v)), "ecart_type": float(np.std(v, ddof=1))}
            for k, v in selection["variant_folds"].items()
        },
        "test": {
            **test_m,
            "rmse_log_ic95": boot_rmse,
            **metrics.country_weighted(t),
            "train_rmse_log": metrics.rmse_log(train["yield_t_ha"], pred_train),
            "rmse_log_culture_seule": crop_only_rmse,
            # Lecture concrète de l'erreur : facteur typique (médiane de |écart en log|) et part des cas
            # où la prédiction reste à moins d'un facteur exp(RMSE-log) de la réalité
            "facteur_typique": float(np.exp(np.median(np.abs(np.log(pred) - np.log(test["yield_t_ha"]))))),
            "facteur_exp_rmse": float(np.exp(test_m["rmse_log"])),
            "part_dans_facteur_exp_rmse": float(
                np.mean(np.abs(np.log(pred) - np.log(test["yield_t_ha"])) <= test_m["rmse_log"])
            ),
            "reference_mediane": baseline_m,
        },
        "cv_aleatoire_rmse_log": {
            "moyenne": float(random_cv.mean()),
            "ecart_type": float(random_cv.std(ddof=1)),
        },
        "importance": importance.set_index("variable")["mean"].to_dict(),
        "recommandation": reco,
        "sensibilite": {
            c: {"min": float(sens[c].min()), "mediane": float(sens[c].median()), "max": float(sens[c].max())}
            for c in ["rmse_log", "top1_modele", "top1_constant"]
        }
        | {
            "modele_bat_constant": int((sens["top1_modele"] > sens["top1_constant"]).sum()),
            "egalites": int((sens["top1_modele"] == sens["top1_constant"]).sum()),
            "modele_battu": int((sens["top1_modele"] < sens["top1_constant"]).sum()),
            "biais_t_ha": {
                "min": float(sens["bias_t_ha"].min()),
                "mediane": float(sens["bias_t_ha"].median()),
                "max": float(sens["bias_t_ha"].max()),
                "negatif": int((sens["bias_t_ha"] < 0).sum()),
            },
            "n_decoupages": len(sens),
        },
        "reference_t_ha": {k: round(v, 3) for k, v in bundle.reference.items()},
        "analyse_complementaire": others,
    }
    (processed / "resultats.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    _experiment("p12-04-modele-final", cfg["paths"]["mlruns"])
    with mlflow.start_run(run_name=f"{name}-test-final"):
        mlflow.set_tags(
            {
                "etape": "test final",
                "modele": name,
                "mlflow.note.content": "Évalué une fois sur les pays de test, puis réentraîné sur tous",
            }
        )
        mlflow.log_params({"modele": name, "features": ",".join(features), "seed": seed, **params})
        mlflow.log_metrics({f"test_{k}": v for k, v in test_m.items()})
        mlflow.log_metrics(
            {
                "test_taux_top1": reco["taux_top1_modele"],
                "test_taux_top1_constant": reco["taux_top1_constant"],
            }
        )
        mlflow.log_artifact(str(processed / "resultats.json"))
        mlflow.sklearn.log_model(served, name="modele", input_example=full[features].head(3))
    return results


def run_prepare(cfg: dict) -> pd.DataFrame:
    """Étape « prepare » : téléchargement vérifié, fusion, CSV consolidé + journal."""
    from agrireco import io

    _, fao_dir = io.download()
    table, log = prepare.build_fao_table(*prepare.load_fao_raw(fao_dir))
    out = cfg["paths"]["processed"]
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "dataset_consolide.csv", index=False)
    log.to_csv(out / "journal_fusion.csv", index=False)
    return table
