"""Préparation des 4 tables de la base (region, commune, bien, vente) à partir des 3 fichiers sources.

Toutes les sources sont lues en texte (io.load_sources) : chaque conversion est faite ici, explicitement.
La colonne « Nom de l'acquereur » n'est jamais reprise (RGPD : aucune requête n'en a besoin).
"""

import re

import pandas as pd

REGION_COLUMNS = ["id_region", "nom_region", "nom_regroupement"]
COMMUNE_COLUMNS = [
    "id_codedep_codecommune",
    "id_region",
    "code_departement",
    "code_commune",
    "nom_commune",
    "population",
]
BIEN_COLUMNS = [
    "id_bien",
    "id_codedep_codecommune",
    "no_voie",
    "btq",
    "type_voie",
    "voie",
    "code_postal",
    "type_local",
    "total_pieces",
    "surface_carrez",
    "surface_reelle_bati",
]
VENTE_COLUMNS = ["id_vente", "id_bien", "date_vente", "valeur_fonciere", "nombre_lots"]

# Colonne DVF -> colonne de la base (seules les colonnes listées ici sont reprises)
DVF_BIEN = {
    "No voie": "no_voie",
    "B/T/Q": "btq",
    "Type de voie": "type_voie",
    "Voie": "voie",
    "Type local": "type_local",
}
POPULATION = "PMUN"  # population municipale : PTOT compte deux fois les personnes « comptées à part »

# --- Encodage ---------------------------------------------------------------------------------------------

# Un texte UTF-8 relu en Windows-1252 transforme chaque lettre accentuée en 2 ou 3 caractères :
# un « octet de tête » (Ã, Å, â…) suivi d'« octets de suite » (codes 0x80 à 0xBF en Windows-1252).
# On repère ces groupes et on les décode un par un, ce qui laisse intacts les accents sains du même nom
# (« Prévessin-MoÃ«ns » : seul « Ã« » est réparé).
_SUITE = "".join(bytes([b]).decode("cp1252", errors="ignore") for b in range(0x80, 0xC0))
_MOJIBAKE = re.compile(f"[Â-ô][{re.escape(_SUITE)}]{{1,3}}")


def _decode_group(match: re.Match) -> str:
    groupe = match.group()
    try:
        return groupe.encode("cp1252").decode("utf-8")
    except UnicodeDecodeError:
        return groupe  # ce n'était pas une lettre abîmée (ex. « Âge » suivi d'un symbole) : on n'y touche pas


def repair_mojibake(texte):
    """Répare un nom UTF-8 relu en Windows-1252 (« SchÅ“lcher » -> « Schœlcher »). NaN/None inchangés."""
    if not isinstance(texte, str):
        return texte
    return _MOJIBAKE.sub(_decode_group, texte)


def repair_names(noms: pd.Series) -> tuple[pd.Series, int]:
    """Répare une colonne de noms ; renvoie aussi le nombre de noms modifiés (journal de préparation)."""
    repares = noms.map(repair_mojibake)
    nb_repares = int((repares != noms)[noms.notna()].sum())
    return repares, nb_repares


# --- Codes ------------------------------------------------------------------------------------------------


def code_postal(x) -> str | None:
    """Code postal sur 5 caractères : Excel a perdu le zéro initial (1170 -> « 01170 »). None si absent."""
    if x is None or pd.isna(x) or str(x).strip() == "":
        return None
    code = str(x).strip()
    if not code.isdigit() or len(code) > 5:
        raise ValueError(f"Code postal invalide : {code!r} (attendu : 1 à 5 chiffres)")
    return code.zfill(5)


def commune_key(dep, com):
    """Clé commune = code département + code commune sur 3 chiffres.

    Exemples : « 01 »+« 103 » -> « 01103 », « 972 »+« 226 » -> « 972226 », « 2A »+« 004 » -> « 2A004 ».

    Accepte deux textes ou deux colonnes (Series) : la même règle sert pour les 3 fichiers.
    Le code postal ne convient pas comme clé : 05100 désigne 3 communes.
    """
    if isinstance(com, pd.Series):
        return dep.str.strip() + com.str.strip().str.zfill(3)
    return dep.strip() + com.strip().zfill(3)


def _check_unique(df: pd.DataFrame, key: str, source: str) -> None:
    doublons = df.loc[df[key].duplicated(keep=False), key]
    if not doublons.empty:
        raise ValueError(
            f"{source} : {doublons.nunique()} clé(s) {key} en double, ex. {sorted(doublons.unique())[:5]}"
        )


# --- Tables -----------------------------------------------------------------------------------------------


def build_region(ref: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par région du référentiel ; id_region = code INSEE en texte (« 02 » = Martinique).

    Les noms sont gardés tels que la source les écrit (« Ile-de-France », sans accent).
    """
    region = (
        ref[["reg_code", "reg_nom", "regrgp_nom"]]
        .drop_duplicates()
        .rename(columns={"reg_code": "id_region", "reg_nom": "nom_region", "regrgp_nom": "nom_regroupement"})
        .sort_values("id_region")
        .reset_index(drop=True)
    )
    # Si un même code porte deux noms, drop_duplicates garde deux lignes : la clé ne serait plus unique.
    _check_unique(region, "id_region", "Référentiel géographique")
    return region[REGION_COLUMNS]


def build_commune(dvf: pd.DataFrame, pop: pd.DataFrame, ref: pd.DataFrame) -> pd.DataFrame:
    """Communes présentes dans DVF, avec leur région (référentiel) et leur population municipale (INSEE)."""
    commune = (
        dvf[["Code departement", "Code commune"]]
        .drop_duplicates()
        .rename(columns={"Code departement": "code_departement", "Code commune": "code_commune"})
    )
    commune["id_codedep_codecommune"] = commune_key(commune["code_departement"], commune["code_commune"])

    geo = ref[["com_code", "reg_code", "com_nom"]].rename(
        columns={"com_code": "id_codedep_codecommune", "reg_code": "id_region", "com_nom": "nom_commune"}
    )
    geo["nom_commune"], _ = repair_names(geo["nom_commune"])
    # espaces doubles de la source (« Paris  7e ») et espaces en fin de nom
    geo["nom_commune"] = geo["nom_commune"].str.split().str.join(" ")
    _check_unique(geo, "id_codedep_codecommune", "Référentiel géographique")

    population = pd.DataFrame(
        {
            "id_codedep_codecommune": commune_key(pop["CODDEP"], pop["CODCOM"]),
            "population": pop[POPULATION],
        }
    )
    _check_unique(population, "id_codedep_codecommune", "Population INSEE")

    # validate="one_to_one" : une jointure ne doit ni dupliquer ni fusionner de communes.
    commune = commune.merge(geo, on="id_codedep_codecommune", how="left", validate="one_to_one")
    commune = commune.merge(population, on="id_codedep_codecommune", how="left", validate="one_to_one")

    for colonne, source in [("id_region", "le référentiel géographique"), ("population", "le fichier INSEE")]:
        absentes = commune.loc[commune[colonne].isna(), "id_codedep_codecommune"]
        if not absentes.empty:
            raise ValueError(
                f"{len(absentes)} commune(s) de DVF introuvable(s) dans {source} : {sorted(absentes)[:10]}"
            )

    commune["population"] = commune["population"].astype("int64")
    return commune.sort_values("id_codedep_codecommune").reset_index(drop=True)[COMMUNE_COLUMNS]


def build_bien_vente(dvf: pd.DataFrame, communes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Une ligne DVF = une vente d'un bien : on crée 1 bien et 1 vente par ligne, numérotés à partir de 1.

    Les valeurs absentes restent manquantes (NaN/None) : elles deviendront NULL en base et des champs vides
    dans les CSV, jamais des chaînes « nan ».
    """
    ids = pd.RangeIndex(1, len(dvf) + 1)
    dvf = dvf.reset_index(drop=True)

    bien = dvf[list(DVF_BIEN)].rename(columns=DVF_BIEN)
    bien.insert(0, "id_bien", ids)
    bien.insert(1, "id_codedep_codecommune", commune_key(dvf["Code departement"], dvf["Code commune"]))
    bien["no_voie"] = pd.to_numeric(dvf["No voie"]).astype("Int64")  # Int64 : entier qui accepte le manquant
    bien["code_postal"] = dvf["Code postal"].map(code_postal)
    bien["total_pieces"] = pd.to_numeric(dvf["Nombre pieces principales"]).astype("Int64")
    bien["surface_carrez"] = pd.to_numeric(dvf["Surface Carrez du 1er lot"])
    bien["surface_reelle_bati"] = pd.to_numeric(dvf["Surface reelle bati"]).astype("Int64")

    inconnues = bien.loc[~bien["id_codedep_codecommune"].isin(communes["id_codedep_codecommune"])]
    if not inconnues.empty:
        raise ValueError(
            f"{len(inconnues)} bien(s) dans une commune absente de la table commune : "
            f"{sorted(inconnues['id_codedep_codecommune'].unique())[:10]}"
        )

    dates = pd.to_datetime(dvf["Date mutation"], format="%Y-%m-%d %H:%M:%S")
    vente = pd.DataFrame(
        {
            "id_vente": ids,
            "id_bien": ids,
            "date_vente": dates.dt.strftime("%Y-%m-%d"),  # format ISO : se trie et se compare comme du texte
            "valeur_fonciere": pd.to_numeric(dvf["Valeur fonciere"]).astype("float64"),
            "nombre_lots": pd.to_numeric(dvf["Nombre de lots"]).astype("Int64"),
        }
    )
    return bien[BIEN_COLUMNS], vente[VENTE_COLUMNS]


def prepare_tables(sources: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Les 4 tables, dans l'ordre de chargement imposé par les clés étrangères (region -> ... -> vente)."""
    dvf, pop, ref = sources["dvf"], sources["population"], sources["referentiel"]
    region = build_region(ref)
    commune = build_commune(dvf, pop, ref)
    bien, vente = build_bien_vente(dvf, commune)
    return {"region": region, "commune": commune, "bien": bien, "vente": vente}
