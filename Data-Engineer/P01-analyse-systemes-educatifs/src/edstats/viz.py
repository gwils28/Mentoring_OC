"""Style graphique commun : une palette, des axes discrets, des titres qui disent quelque chose."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Palette catégorielle validée daltonisme (ordre fixe : on ne la fait jamais « tourner »)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
TEXT, TEXT_2, MUTED = "#0b0b0b", "#52514e", "#a3a29c"
SURFACE, GRID = "#fcfcfb", "#e6e5e0"

# Divergente bleu ↔ rouge, milieu gris neutre : pour les corrélations (de -1 à +1)
DIVERGING = LinearSegmentedColormap.from_list(
    "bleu_gris_rouge", ["#104281", "#3987e5", "#f0efec", "#e66767", "#a32b2b"]
)

FIGURES_DIR = Path(__file__).resolve().parents[2] / "presentation" / "figures"


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
            "axes.prop_cycle": mpl.cycler(color=[BLUE, ORANGE, AQUA]),
        }
    )


def save(fig: plt.Figure, name: str) -> Path:
    """Enregistre la figure pour la présentation (PNG haute définition)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    return path
