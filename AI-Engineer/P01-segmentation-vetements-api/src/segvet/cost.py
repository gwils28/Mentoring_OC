"""Chiffrage : du temps mesuré par image à un budget mensuel, selon deux façons de payer."""

SECONDS_PER_DAY = 24 * 3600


def required_rate_per_minute(n_images: int, days: int) -> float:
    """Débit moyen nécessaire pour traiter `n_images` en `days` jours, en images par minute."""
    return n_images / (days * 24 * 60)


def serverless_cost(n_images: int, seconds_per_image: float, price_per_second: float) -> float:
    """Paiement à l'usage : on paie le temps de calcul de chaque requête (hf-inference)."""
    return n_images * seconds_per_image * price_per_second


def dedicated_cost(hours: float, price_per_hour: float) -> float:
    """Machine réservée : on paie chaque heure allumée, qu'elle travaille ou non."""
    return hours * price_per_hour


def batch_hours(n_images: int, seconds_per_image: float, parallel: int = 1) -> float:
    """Heures de machine nécessaires si on traite les images par lots puis qu'on éteint la machine."""
    return n_images * seconds_per_image / parallel / 3600
