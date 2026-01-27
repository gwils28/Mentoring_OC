"""Chaque requête SQL des 12 besoins est recoupée par un calcul pandas indépendant, fait sur les CSV.

Deux chemins de calcul différents qui donnent le même résultat : c'est la preuve qu'on n'a pas seulement écrit
une requête qui « tourne », mais une requête qui répond juste.
"""

import sqlite3
from pathlib import Path

import pandas as pd
import pytest

PROJET = Path(__file__).resolve().parents[1]
BASE = PROJET / "data" / "processed" / "dataimmo.sqlite"
REQUETES = PROJET / "sql" / "requetes"

pytestmark = pytest.mark.skipif(
    not BASE.exists(), reason="base non construite : uv run python -m dataimmo.build"
)


def requete(numero: int) -> pd.DataFrame:
    fichier = next(REQUETES.glob(f"{numero:02d}_*.sql"))
    with sqlite3.connect(f"file:{BASE}?mode=ro", uri=True) as connexion:
        return pd.read_sql(fichier.read_text(encoding="utf-8"), connexion)


@pytest.fixture(scope="module")
def ventes() -> pd.DataFrame:
    """Une ligne par vente, avec bien, commune et région : la « table plate » reconstruite en pandas."""
    codes_texte = {
        "id_region": str,
        "id_codedep_codecommune": str,
        "code_departement": str,
        "code_commune": str,
    }

    def lire(nom: str) -> pd.DataFrame:
        return pd.read_csv(PROJET / "data" / "processed" / f"{nom}.csv", dtype=codes_texte)

    plate = (
        lire("vente")
        .merge(lire("bien"), on="id_bien", validate="one_to_one")
        .merge(lire("commune"), on="id_codedep_codecommune", validate="many_to_one")
        .merge(lire("region"), on="id_region", validate="many_to_one")
    )
    plate["prix_m2"] = plate["valeur_fonciere"] / plate["surface_carrez"]
    return plate


def test_toutes_les_requetes_existent():
    assert len(list(REQUETES.glob("*.sql"))) == 12


def test_01_appartements_vendus(ventes):
    attendu = (ventes["type_local"] == "Appartement").sum()
    assert requete(1).iloc[0, 0] == attendu == 31378


def test_02_par_region(ventes):
    attendu = ventes[ventes["type_local"] == "Appartement"].groupby("nom_region").size()
    obtenu = requete(2).set_index("nom_region")["nb_ventes_appartements"]
    pd.testing.assert_series_equal(obtenu.sort_index(), attendu.sort_index(), check_names=False)
    assert len(obtenu) == 17


def test_03_proportions(ventes):
    appart = ventes[ventes["type_local"] == "Appartement"]
    attendu = (appart["total_pieces"].value_counts(normalize=True) * 100).round(2).sort_index()
    obtenu = requete(3).set_index("nb_pieces")["proportion_pct"]
    pd.testing.assert_series_equal(obtenu, attendu, check_names=False, check_index_type=False)


def test_04_top10_departements(ventes):
    attendu = ventes.groupby("code_departement")["prix_m2"].mean().round(0).nlargest(10)
    obtenu = requete(4)
    assert obtenu["code_departement"].tolist() == attendu.index.tolist()
    assert obtenu["prix_m2_moyen"].tolist() == attendu.tolist()


def test_05_maisons_idf(ventes):
    idf = ventes[(ventes["type_local"] == "Maison") & (ventes["id_region"] == "11")]
    assert requete(5).iloc[0, 0] == round(idf["prix_m2"].mean()) == 3745


def test_06_top10_appartements(ventes):
    attendu = ventes[ventes["type_local"] == "Appartement"].nlargest(10, "valeur_fonciere")["valeur_fonciere"]
    assert requete(6)["valeur_fonciere"].tolist() == attendu.tolist()


def test_07_evolution(ventes):
    t1 = ventes["date_vente"].between("2020-01-01", "2020-03-31").sum()
    t2 = ventes["date_vente"].between("2020-04-01", "2020-06-30").sum()
    ligne = requete(7).iloc[0]
    assert (ligne["nb_t1"], ligne["nb_t2"]) == (t1, t2) == (16776, 17393)
    assert ligne["evolution_pct"] == round((t2 - t1) / t1 * 100, 2) == 3.68


def test_08_regions_plus_de_4_pieces(ventes):
    grands = ventes[(ventes["type_local"] == "Appartement") & (ventes["total_pieces"] > 4)]
    attendu = grands.groupby("nom_region")["prix_m2"].mean().round(0).sort_values(ascending=False)
    obtenu = requete(8)
    assert obtenu["nom_region"].tolist() == attendu.index.tolist()
    assert obtenu["nb_ventes"].sum() == grands["prix_m2"].notna().sum()


def test_09_communes_50_ventes_t1(ventes):
    t1 = ventes[ventes["date_vente"].between("2020-01-01", "2020-03-31")]
    attendu = t1.groupby("id_codedep_codecommune").size()
    assert len(requete(9)) == (attendu >= 50).sum() == 48


def test_10_ecart_2_3_pieces(ventes):
    appart = ventes[ventes["type_local"] == "Appartement"]
    p2 = appart.loc[appart["total_pieces"] == 2, "prix_m2"].mean()
    p3 = appart.loc[appart["total_pieces"] == 3, "prix_m2"].mean()
    assert requete(10).iloc[0]["ecart_pct"] == round((p3 - p2) / p2 * 100, 2) == -12.4


def test_11_top3_par_departement(ventes):
    cinq = ventes[ventes["code_departement"].isin(["06", "13", "33", "59", "69"])]
    moyennes = cinq.groupby(["code_departement", "id_codedep_codecommune"])["valeur_fonciere"].mean().round(0)
    attendu = moyennes.groupby(level=0).nlargest(3).droplevel(0)
    obtenu = requete(11)
    assert len(obtenu) == 15
    assert obtenu["valeur_moyenne"].tolist() == attendu.tolist()


def test_12_ventes_pour_1000_habitants(ventes):
    grandes = ventes[ventes["population"] > 10000]
    par_commune = grandes.groupby("id_codedep_codecommune").agg(
        n=("id_vente", "size"), pop=("population", "first")
    )
    attendu = (par_commune["n"] * 1000 / par_commune["pop"]).round(2).nlargest(20)
    obtenu = requete(12)
    assert obtenu["ventes_pour_1000_hab"].tolist() == attendu.tolist()
    assert (
        obtenu.iloc[0]["nom_commune"].startswith("Paris") and obtenu.iloc[0]["ventes_pour_1000_hab"] == 5.88
    )
