from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass(frozen=True)
class GameConfig:
    name: str
    draw_len: int
    min_val: int
    max_val: int
    special_len: int = 0
    special_min: Optional[int] = None
    special_max: Optional[int] = None
    digits_mode: bool = False

REGISTRY: Dict[str, GameConfig] = {
    "Pick3_FL":  GameConfig("Pick3_FL", 3, 0, 9, 0, None, None, True),
    "Pick4_FL":  GameConfig("Pick4_FL", 4, 0, 9, 0, None, None, True),
    "Pick5_FL":  GameConfig("Pick5_FL", 5, 0, 9, 0, None, None, True),

    "MegaMillions": GameConfig("MegaMillions", 5, 1, 70, 1, 1, 25, False),
    "Powerball":    GameConfig("Powerball",    5, 1, 69, 1, 1, 26, False),
}

def get_game_cfg(name: str) -> GameConfig:
    if name not in REGISTRY:
        raise ValueError(f"Juego no registrado: {name}")
    return REGISTRY[name]





