"""Mesures de qualité de données et traçabilité des filtres."""

from dataclasses import dataclass, field

import pandas as pd


def missing_rate(df: pd.DataFrame) -> pd.Series:
    """Pourcentage de valeurs manquantes par colonne, de la plus vide à la plus remplie."""
    return (df.isna().mean() * 100).round(2).sort_values(ascending=False)


def fill_rate(long: pd.DataFrame, by: str | list[str], value: str = "value") -> pd.Series:
    """Proportion de valeurs renseignées par groupe : count() ignore les NaN, size() non."""
    grouped = long.groupby(by)[value]
    return grouped.count() / grouped.size()


@dataclass
class FilterLog:
    """Journal des filtres : chaque étape garde le nombre de lignes avant et après."""

    steps: list[dict] = field(default_factory=list)

    def apply(self, df: pd.DataFrame, mask: pd.Series, label: str) -> pd.DataFrame:
        kept = df[mask]
        self.steps.append(
            {
                "etape": label,
                "lignes_avant": len(df),
                "lignes_apres": len(kept),
                "lignes_supprimees": len(df) - len(kept),
            }
        )
        return kept

    def record(self, label: str, before: int, after: int) -> None:
        """Pour les opérations qui ne sont pas des masques (jointure, pivot…)."""
        self.steps.append(
            {
                "etape": label,
                "lignes_avant": before,
                "lignes_apres": after,
                "lignes_supprimees": before - after,
            }
        )

    def to_frame(self) -> pd.DataFrame:
        return pd.DataFrame(self.steps)
