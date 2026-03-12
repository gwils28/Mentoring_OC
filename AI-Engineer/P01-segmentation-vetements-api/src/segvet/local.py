"""Plan B et « aller plus loin » : faire tourner le même modèle sur sa machine (groupe uv « local »)."""

from pathlib import Path

import numpy as np
from PIL import Image

from segvet.api import MODEL_ID


def load_model(model_id: str = MODEL_ID):
    """Télécharge (une fois, cache Hugging Face) puis charge le modèle et son préprocesseur."""
    from transformers import AutoModelForSemanticSegmentation, SegformerImageProcessor

    processor = SegformerImageProcessor.from_pretrained(model_id)
    model = AutoModelForSemanticSegmentation.from_pretrained(model_id).eval()
    return processor, model


def predict(path: Path, processor, model) -> np.ndarray:
    """Carte de classes à la taille de l'image, comme dans l'exemple de la fiche du modèle."""
    import torch

    image = Image.open(path).convert("RGB")
    with torch.inference_mode():
        logits = model(**processor(images=image, return_tensors="pt")).logits
        upsampled = torch.nn.functional.interpolate(
            logits, size=image.size[::-1], mode="bilinear", align_corners=False
        )
    return upsampled.argmax(dim=1)[0].numpy().astype(np.uint8)
