"""Nettoyage spécifique à EdStats."""

import pandas as pd

# Codes alpha-2 réservés par la Banque mondiale aux agrégats (régions, groupes de revenus, monde…)
AGGREGATE_ALPHA2_PREFIXES = ("X", "Z")
AGGREGATE_ALPHA2_CODES = {"EU", "OE"}


def _is_aggregate_alpha2(code: str) -> bool:
    return (
        any(ch.isdigit() for ch in code)
        or code.startswith(AGGREGATE_ALPHA2_PREFIXES)
        or code in AGGREGATE_ALPHA2_CODES
    )


def find_aggregates(country: pd.DataFrame) -> list[str]:
    """Codes pays qui sont en réalité des agrégats (« faux pays »).

    Deux conditions pour éviter les faux positifs : pas de région, ET un code alpha-2 d'agrégat.
    Gibraltar (GI) et Nauru (NR) n'ont pas de région mais sont de vrais territoires.
    """
    no_region = country["Region"].isna()
    aggregate_code = country["2-alpha code"].fillna("").map(_is_aggregate_alpha2)
    return sorted(country.loc[no_region & aggregate_code, "Country Code"])
