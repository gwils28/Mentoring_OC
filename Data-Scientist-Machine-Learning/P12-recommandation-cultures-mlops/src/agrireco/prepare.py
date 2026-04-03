"""Étape « prepare » : fusion des fichiers FAO / Banque mondiale en une table (pays, culture, année).

On reconstruit la table depuis les fichiers bruts plutôt que d'utiliser `yield_df.csv` : ce dernier contient
des doublons (plusieurs stations de température par pays) et perd les pays dont le nom s'écrit différemment
d'un fichier à l'autre.
"""

from pathlib import Path

import numpy as np
import pandas as pd

KEY = ["country", "crop", "year"]

# Noms des fichiers pluie / température / pesticides → noms FAO du fichier de rendement.
# Construite en listant les pays présents d'un côté et absents de l'autre (anti-jointure).
COUNTRY_ALIASES = {
    "Bolivia": "Bolivia (Plurinational State of)",
    "Bosnia And Herzegovina": "Bosnia and Herzegovina",
    "Congo (Democratic Republic Of The)": "Democratic Republic of the Congo",
    "Congo, Dem. Rep.": "Democratic Republic of the Congo",
    "Congo, Rep.": "Congo",
    "Cote d'Ivoire": "Côte d'Ivoire",
    "Côte D'Ivoire": "Côte d'Ivoire",
    "Czech Republic": "Czechia",
    "Guinea Bissau": "Guinea-Bissau",
    "Hong Kong": "China, Hong Kong SAR",
    "Hong Kong SAR, China": "China, Hong Kong SAR",
    "Iran": "Iran (Islamic Republic of)",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Lao PDR": "Lao People's Democratic Republic",
    "Laos": "Lao People's Democratic Republic",
    "Macedonia": "The former Yugoslav Republic of Macedonia",
    "Moldova": "Republic of Moldova",
    "North Korea": "Democratic People's Republic of Korea",
    "Russia": "Russian Federation",
    "Slovak Republic": "Slovakia",
    "South Korea": "Republic of Korea",
    "Syria": "Syrian Arab Republic",
    "Taiwan": "China, Taiwan Province of",
    "Tanzania": "United Republic of Tanzania",
    "United States": "United States of America",
    "Venezuela": "Venezuela (Bolivarian Republic of)",
    "Venezuela, RB": "Venezuela (Bolivarian Republic of)",
    "Vietnam": "Viet Nam",
}
# « China » dans le fichier de rendement est un agrégat (continent + Taïwan + Hong Kong + Macao) ; les
# pesticides n'existent que pour « China, mainland ». La pluie et la température « China » décrivent le
# territoire continental : on les rattache à « China, mainland » et on retire l'agrégat.
CHINA_AGGREGATE = "China"
CHINA_MAINLAND = "China, mainland"


def harmonize(names: pd.Series) -> pd.Series:
    """Ramène les noms de pays aux noms FAO (espaces superflus retirés)."""
    return names.str.strip().replace(COUNTRY_ALIASES)


def check_unique_key(df: pd.DataFrame, key: list[str] = KEY) -> None:
    dup = df.duplicated(key, keep=False)
    if dup.any():
        raise ValueError(
            f"La clé {key} n'est pas unique : {int(dup.sum())} lignes en double, par ex.\n{df[dup].head()}"
        )


def build_fao_table(
    yield_raw: pd.DataFrame, rain_raw: pd.DataFrame, pest_raw: pd.DataFrame, temp_raw: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fusionne les 4 fichiers bruts. Renvoie (table, journal du nombre de lignes à chaque étape)."""
    log = []
    y = yield_raw.loc[yield_raw["Unit"] == "hg/ha", ["Area", "Item", "Year", "Value"]]
    y = y.rename(columns={"Area": "country", "Item": "crop", "Year": "year", "Value": "yield_hg_ha"})
    log.append(("rendements FAO (toutes années)", len(y)))
    y = y[y["country"] != CHINA_AGGREGATE]
    log.append(("sans l'agrégat « China »", len(y)))

    rain = rain_raw.rename(columns=lambda c: c.strip())
    rain = pd.DataFrame(
        {
            "country": harmonize(rain["Area"]).replace({CHINA_AGGREGATE: CHINA_MAINLAND}),
            "year": rain["Year"],
            "rainfall_mm": pd.to_numeric(rain["average_rain_fall_mm_per_year"], errors="coerce").astype(
                float
            ),
        }
    ).dropna()

    pest = pd.DataFrame(
        {"country": harmonize(pest_raw["Area"]), "year": pest_raw["Year"], "pesticides_t": pest_raw["Value"]}
    )

    temp = pd.DataFrame(
        {
            "country": harmonize(temp_raw["country"]).replace({CHINA_AGGREGATE: CHINA_MAINLAND}),
            "year": temp_raw["year"],
            "avg_temp": temp_raw["avg_temp"],
        }
    ).dropna()
    # Plusieurs stations pour un même pays et une même année : une seule valeur, la moyenne
    temp = temp.groupby(["country", "year"], as_index=False)["avg_temp"].mean()

    out = y
    for name, table in [("pluie", rain), ("pesticides", pest), ("température", temp)]:
        check_unique_key(table, ["country", "year"])
        out = out.merge(table, on=["country", "year"], how="inner")
        log.append((f"après jointure {name}", len(out)))

    out = out.assign(yield_t_ha=out["yield_hg_ha"] / 10_000).drop(columns="yield_hg_ha")
    out = out[KEY + ["yield_t_ha", "rainfall_mm", "pesticides_t", "avg_temp"]]
    out = out.sort_values(KEY).reset_index(drop=True)
    check_unique_key(out)
    return out, pd.DataFrame(log, columns=["etape", "lignes"])


def load_fao_raw(fao_dir: Path) -> tuple[pd.DataFrame, ...]:
    return tuple(
        pd.read_csv(fao_dir / f) for f in ("yield.csv", "rainfall.csv", "pesticides.csv", "temp.csv")
    )


# Correspondance des cultures communes aux deux jeux (synthétique → FAO)
AGRI_TO_FAO_CROP = {"Maize": "Maize", "Rice": "Rice, paddy", "Wheat": "Wheat", "Soybean": "Soybeans"}


def join_on_crop(fao: pd.DataFrame, agri: pd.DataFrame) -> pd.DataFrame:
    """Seule fusion possible avec le jeu synthétique (ni pays ni année) : par culture, après agrégation.

    Sert à démontrer que les colonnes ajoutées sont quasi constantes ; elle n'alimente pas le modèle.
    """
    per_crop = (
        agri.assign(crop=agri["Crop"].map(AGRI_TO_FAO_CROP))
        .dropna(subset=["crop"])
        .groupby("crop")
        .agg(
            agri_fertilizer_rate=("Fertilizer_Used", "mean"),
            agri_irrigation_rate=("Irrigation_Used", "mean"),
            agri_mean_yield_t_ha=("Yield_tons_per_hectare", "mean"),
        )
        .reset_index()
    )
    return fao.merge(per_crop, on="crop", how="inner")


def add_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Variables dérivées utilisées par le modèle."""
    return df.assign(log10_pesticides_t=np.log10(df["pesticides_t"].clip(lower=0) + 1))
