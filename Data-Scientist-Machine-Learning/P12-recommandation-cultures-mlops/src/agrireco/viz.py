"""Style graphique commun (notebooks, fiches, présentation, rapport) et petites aides d'affichage."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

# Palette catégorielle validée daltonisme (validateur du skill dataviz), dans son ordre fixe.
# Orange et jaune ont un contraste < 3:1 sur le fond : toujours accompagnés d'une étiquette directe.
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
TEXT, TEXT_2, MUTED = "#0b0b0b", "#52514e", "#898781"
SURFACE, GRID = "#fcfcfb", "#e1e0d9"

FIGURES_DIR = Path(__file__).resolve().parents[2] / "presentation" / "figures"

CROPS_FR = {
    "Cassava": "Manioc",
    "Maize": "Maïs",
    "Plantains and others": "Banane plantain",
    "Potatoes": "Pomme de terre",
    "Rice, paddy": "Riz",
    "Sorghum": "Sorgho",
    "Soybeans": "Soja",
    "Sweet potatoes": "Patate douce",
    "Wheat": "Blé",
    "Yams": "Igname",
}


def fr(x: float, decimals: int = 2) -> str:
    """Nombre à la française pour les textes : 0,61 et non 0.61 ; espace fine pour les milliers."""
    return f"{x:,.{decimals}f}".replace(",", " ").replace(".", ",")


def pct(x: float, decimals: int = 1) -> str:
    return fr(100 * x, decimals) + " %"


def apply_style() -> None:
    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "figure.dpi": 110,
            "savefig.dpi": 200,
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "axes.labelcolor": TEXT_2,
            "axes.edgecolor": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "xtick.color": TEXT_2,
            "ytick.color": TEXT_2,
            "legend.frameon": False,
            "axes.prop_cycle": mpl.cycler(color=[BLUE, ORANGE, AQUA, YELLOW]),
        }
    )


def save(fig: plt.Figure, name: str) -> Path:
    """Enregistre la figure dans presentation/figures/ (réutilisée par la présentation et le rapport)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    return path
