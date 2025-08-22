# modules/lottery_config.py — Config de loterías (saneado)
from __future__ import annotations
from pathlib import Path

# Carpeta de assets (opcional). Si no tienes imágenes, dejamos los logos en None.
ASSETS = Path(__file__).resolve().parent.parent / "ASSETS"

def _has_logo(name: str) -> str | None:
    """Devuelve la ruta del logo si existe; si no, None."""
    p = ASSETS / name
    return str(p) if p.exists() else None

# Estructura esperada por vision_app.py:
# LOTTERIES[key] = {
#   "name": str,
#   "logo": str|None (ruta a imagen o None),
#   "days": list[str],                 # días del sorteo
#   "draw_time_local": str,            # hora local tipo "23:00 ET"
#   "tz": str,                         # zona horaria IANA
#   "site": str,                       # URL oficial
#   "structure": str,                  # descripción del formato
# }

LOTTERIES = {
    "megamillions": {
        "name": "Mega Millions",
        "logo": _has_logo("megamillions.png"),
        "days": ["Tuesday", "Friday"],
        "draw_time_local": "23:00",
        "tz": "America/New_York",
        "site": "https://www.megamillions.com/",
        "structure": "5 números (1-70) + Mega Ball (1-25)",
    },
    "powerball": {
        "name": "Powerball",
        "logo": _has_logo("powerball.png"),
        "days": ["Monday", "Wednesday", "Saturday"],
        "draw_time_local": "22:59",
        "tz": "America/New_York",
        "site": "https://www.powerball.com/",
        "structure": "5 números (1-69) + Powerball (1-26)",
    },
    "cash5_nj": {
        "name": "Cash5 Jersey",
        "logo": _has_logo("cash5_nj.png"),
        "days": ["Daily"],
        "draw_time_local": "22:57",
        "tz": "America/New_York",
        "site": "https://www.njlottery.com/",
        "structure": "5 números (1-45)",
    },
    # Puedes añadir más entradas siguiendo el mismo patrón:
    # "california_superlotto": {
    #     "name": "CA SuperLotto Plus",
    #     "logo": _has_logo("ca_superlotto.png"),
    #     "days": ["Wednesday", "Saturday"],
    #     "draw_time_local": "19:57",
    #     "tz": "America/Los_Angeles",
    #     "site": "https://www.calottery.com/",
    #     "structure": "5/47 + 1/27",
    # },
}

# Clave predeterminada (debe existir en LOTTERIES)
DEFAULT_LOTTERY = "megamillions"
