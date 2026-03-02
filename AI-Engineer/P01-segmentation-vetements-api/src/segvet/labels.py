"""Les 18 classes du modèle segformer_b3_clothes (jeu ATR) et leur regroupement métier."""

# Ordre = identifiant de classe dans les masques annotés comme dans le modèle (config.json, id2label)
CLASSES = [
    "Background",
    "Hat",
    "Hair",
    "Sunglasses",
    "Upper-clothes",
    "Skirt",
    "Pants",
    "Dress",
    "Belt",
    "Left-shoe",
    "Right-shoe",
    "Face",
    "Left-leg",
    "Right-leg",
    "Left-arm",
    "Right-arm",
    "Bag",
    "Scarf",
]
CLASS_TO_ID = {name: i for i, name in enumerate(CLASSES)}
N_CLASSES = len(CLASSES)

FRENCH = {
    "Background": "Fond",
    "Hat": "Chapeau",
    "Hair": "Cheveux",
    "Sunglasses": "Lunettes de soleil",
    "Upper-clothes": "Haut",
    "Skirt": "Jupe",
    "Pants": "Pantalon",
    "Dress": "Robe",
    "Belt": "Ceinture",
    "Left-shoe": "Chaussure gauche",
    "Right-shoe": "Chaussure droite",
    "Face": "Visage",
    "Left-leg": "Jambe gauche",
    "Right-leg": "Jambe droite",
    "Left-arm": "Bras gauche",
    "Right-arm": "Bras droit",
    "Bag": "Sac",
    "Scarf": "Écharpe",
}

# Ce qui intéresse ModeTrends : les vêtements et accessoires, pas le corps ni le fond
CLOTHING = [
    "Hat",
    "Sunglasses",
    "Upper-clothes",
    "Skirt",
    "Pants",
    "Dress",
    "Belt",
    "Left-shoe",
    "Right-shoe",
    "Bag",
    "Scarf",
]
BODY = ["Hair", "Face", "Left-leg", "Right-leg", "Left-arm", "Right-arm"]
