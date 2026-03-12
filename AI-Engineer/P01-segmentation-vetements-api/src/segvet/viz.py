"""Style graphique commun et code couleur des masques (notebook, fiches et présentation)."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from PIL import Image, ImageFilter

from segvet.labels import CLASS_TO_ID, N_CLASSES

# Palette catégorielle validée daltonisme, dans son ordre fixe (8 teintes au maximum)
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#6250d6", "#e34948"
TEXT, TEXT_2, MUTED = "#0b0b0b", "#52514e", "#898781"
SURFACE, GRID, SKIN = "#fcfcfb", "#e1e0d9", "#c3c2b7"
LIGHT_BLUE = "#86b6ef"  # même teinte que BLUE, plus claire : vêtement hors métrique principale

FIGURES_DIR = Path(__file__).resolve().parents[2] / "presentation" / "figures"

# 18 classes, c'est trop de couleurs pour un œil : on affiche 8 familles de vêtements en couleur, le corps
# en gris (cheveux foncés, peau claire) et le fond sans couleur. Les calculs, eux, gardent les 18 classes.
DISPLAY_GROUPS = [
    ("Haut", ["Upper-clothes"], BLUE),
    ("Pantalon", ["Pants"], ORANGE),
    ("Jupe", ["Skirt"], AQUA),
    ("Robe", ["Dress"], YELLOW),
    ("Sac", ["Bag"], MAGENTA),
    ("Chaussures", ["Left-shoe", "Right-shoe"], GREEN),
    ("Chapeau, lunettes", ["Hat", "Sunglasses"], VIOLET),
    ("Ceinture, écharpe", ["Belt", "Scarf"], RED),
    ("Cheveux", ["Hair"], TEXT_2),
    ("Peau", ["Face", "Left-arm", "Right-arm", "Left-leg", "Right-leg"], SKIN),
]


def _class_colors() -> np.ndarray:
    colors = np.zeros((N_CLASSES, 3), dtype=np.uint8)
    colors[0] = [255 * c for c in mpl.colors.to_rgb(SURFACE)]
    for _, classes, color in DISPLAY_GROUPS:
        for name in classes:
            colors[CLASS_TO_ID[name]] = [round(255 * c) for c in mpl.colors.to_rgb(color)]
    return colors


CLASS_COLORS = _class_colors()


def fr(x: float, decimals: int = 2) -> str:
    """Nombre à la française pour les textes des figures : 0,79 et non 0.79."""
    return f"{x:.{decimals}f}".replace(".", ",")


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


def colorize(label_map: np.ndarray) -> np.ndarray:
    """Carte de classes (H, W) → image couleur (H, W, 3) avec le code couleur commun."""
    return CLASS_COLORS[label_map]


def blur_faces(image: np.ndarray, truth: np.ndarray, radius: int = 12) -> np.ndarray:
    """Floute le visage (classe Face de l'annotation) : les figures publiées montrent de vraies personnes."""
    face = truth == CLASS_TO_ID["Face"]
    if not face.any():
        return image
    # On élargit un peu la zone pour couvrir le contour du visage
    zone = np.array(Image.fromarray(face.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(15))) > 0
    blurred = np.array(Image.fromarray(image).filter(ImageFilter.GaussianBlur(radius)))
    out = image.copy()
    out[zone] = blurred[zone]
    return out


def legend_handles(*label_maps: np.ndarray) -> list[Patch]:
    """Légende limitée aux familles présentes dans les cartes affichées."""
    present = set(np.unique(np.concatenate([m.ravel() for m in label_maps])).tolist())
    return [
        Patch(facecolor=color, label=name)
        for name, classes, color in DISPLAY_GROUPS
        if present & {CLASS_TO_ID[c] for c in classes}
    ]


def show_triptych(image: np.ndarray, truth: np.ndarray, pred: np.ndarray, title: str = "", axes=None):
    """Photo (visage flouté) | annotation | prédiction, côte à côte, avec une légende commune."""
    if axes is None:
        _, axes = plt.subplots(1, 3, figsize=(9, 4.6))
    panels = [
        (blur_faces(image, truth), "Photo"),
        (colorize(truth), "Annotation"),
        (colorize(pred), "Modèle"),
    ]
    for ax, (picture, name) in zip(axes, panels, strict=True):
        ax.imshow(picture)
        ax.set_title(name, fontsize=10, fontweight="normal", color=TEXT_2)
        ax.axis("off")
    if title:
        axes[0].figure.suptitle(title, x=0.01, ha="left", fontweight="bold")
    axes[-1].legend(handles=legend_handles(truth, pred), loc="center left", bbox_to_anchor=(1.02, 0.5))
    return axes


def save(fig: plt.Figure, name: str) -> Path:
    """Enregistre la figure pour la présentation (PNG haute définition)."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    return path
