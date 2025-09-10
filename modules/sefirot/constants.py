# modules/sefirot/constants.py
"""
Constantes y mapeos para el sistema Sefirot Suite
Definiciones del Árbol de la Vida, pilares, senderos y configuraciones
"""

from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class SefiraInfo:
    """Información completa de una Sefirá"""
    nombre: str
    pilar: str
    peso_base: float
    ciclo_sugerido: int
    coordenadas: Tuple[float, float]
    color: str
    energia: str
    descripcion: str

# Mapeo completo de las 10 Sefirot del Árbol de la Vida
SEFIROT: Dict[int, SefiraInfo] = {
    1: SefiraInfo(
        nombre="Keter",
        pilar="Centro",
        peso_base=10.0,
        ciclo_sugerido=7,
        coordenadas=(0.5, 0.9),
        color="#FFD700",  # Dorado
        energia="Divina",
        descripcion="Corona - Voluntad Divina"
    ),
    2: SefiraInfo(
        nombre="Chokmah",
        pilar="Centro",
        peso_base=9.0,
        ciclo_sugerido=6,
        coordenadas=(0.3, 0.7),
        color="#87CEEB",  # Azul cielo
        energia="Masculina",
        descripcion="Sabiduría - Energía Creativa"
    ),
    3: SefiraInfo(
        nombre="Binah",
        pilar="Izquierda",
        peso_base=8.0,
        ciclo_sugerido=5,
        coordenadas=(0.1, 0.7),
        color="#9370DB",  # Púrpura
        energia="Femenina",
        descripcion="Entendimiento - Forma y Estructura"
    ),
    4: SefiraInfo(
        nombre="Chesed",
        pilar="Derecha",
        peso_base=7.0,
        ciclo_sugerido=4,
        coordenadas=(0.7, 0.7),
        color="#32CD32",  # Verde
        energia="Expansiva",
        descripcion="Misericordia - Amor y Compasión"
    ),
    5: SefiraInfo(
        nombre="Gevurah",
        pilar="Izquierda",
        peso_base=6.0,
        ciclo_sugerido=3,
        coordenadas=(0.1, 0.5),
        color="#FF4500",  # Rojo naranja
        energia="Restrictiva",
        descripcion="Fuerza - Justicia y Disciplina"
    ),
    6: SefiraInfo(
        nombre="Tiferet",
        pilar="Centro",
        peso_base=5.0,
        ciclo_sugerido=2,
        coordenadas=(0.5, 0.5),
        color="#FFD700",  # Dorado
        energia="Equilibrada",
        descripcion="Belleza - Armonía y Balance"
    ),
    7: SefiraInfo(
        nombre="Netzach",
        pilar="Derecha",
        peso_base=4.0,
        ciclo_sugerido=1,
        coordenadas=(0.7, 0.3),
        color="#FF69B4",  # Rosa
        energia="Activa",
        descripcion="Victoria - Persistencia y Resistencia"
    ),
    8: SefiraInfo(
        nombre="Hod",
        pilar="Izquierda",
        peso_base=3.0,
        ciclo_sugerido=1,
        coordenadas=(0.1, 0.3),
        color="#FFA500",  # Naranja
        energia="Receptiva",
        descripcion="Gloria - Esplendor y Forma"
    ),
    9: SefiraInfo(
        nombre="Yesod",
        pilar="Centro",
        peso_base=2.0,
        ciclo_sugerido=1,
        coordenadas=(0.5, 0.1),
        color="#00CED1",  # Turquesa
        energia="Estabilizadora",
        descripcion="Fundación - Subconsciente"
    ),
    10: SefiraInfo(
        nombre="Malkuth",
        pilar="Derecha",
        peso_base=1.0,
        ciclo_sugerido=1,
        coordenadas=(0.7, 0.1),
        color="#8B4513",  # Marrón
        energia="Manifestada",
        descripcion="Reino - Mundo Físico"
    )
}

# Definición de pilares
PILARES: Dict[str, List[int]] = {
    "Derecha": [4, 7, 10],    # Chesed, Netzach, Malkuth
    "Izquierda": [3, 5, 8],   # Binah, Gevurah, Hod
    "Centro": [1, 2, 6, 9]    # Keter, Chokmah, Tiferet, Yesod
}

# Senderos del Árbol de la Vida (conexiones entre Sefirot)
SENDEROS: List[Tuple[int, int]] = [
    # Senderos verticales
    (1, 2), (1, 3),  # Keter → Chokmah, Binah
    (2, 4), (2, 6),  # Chokmah → Chesed, Tiferet
    (3, 5), (3, 6),  # Binah → Gevurah, Tiferet
    (4, 7), (4, 6),  # Chesed → Netzach, Tiferet
    (5, 8), (5, 6),  # Gevurah → Hod, Tiferet
    (6, 9), (6, 7), (6, 8),  # Tiferet → Yesod, Netzach, Hod
    (7, 10), (8, 9), (9, 10),  # Netzach → Malkuth, Hod → Yesod, Yesod → Malkuth
    
    # Senderos horizontales
    (2, 3),  # Chokmah ↔ Binah
    (4, 5),  # Chesed ↔ Gevurah
    (7, 8),  # Netzach ↔ Hod
]

# Mapeo hebreo para gematría (números 1-100)
HEBREW_MAP: Dict[int, str] = {
    # Unidades (1-9)
    1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה", 6: "ו", 7: "ז", 8: "ח", 9: "ט",
    # Decenas (10-90)
    10: "י", 20: "כ", 30: "ל", 40: "מ", 50: "נ", 60: "ס", 70: "ע", 80: "פ", 90: "צ",
    # Centenas (100)
    100: "ק"
}

# Valores gematría de letras hebreas
HEBREW_VALUES: Dict[str, int] = {
    "א": 1, "ב": 2, "ג": 3, "ד": 4, "ה": 5, "ו": 6, "ז": 7, "ח": 8, "ט": 9,
    "י": 10, "כ": 20, "ל": 30, "מ": 40, "נ": 50, "ס": 60, "ע": 70, "פ": 80, "צ": 90,
    "ק": 100
}

# Patrones de armonía predefinidos
HARMONY_PATTERNS: Dict[str, List[int]] = {
    "vertical": [1, 6, 9],  # Keter → Tiferet → Yesod
    "triangulo_superior": [3, 4, 5],  # Binah → Chesed → Gevurah
    "netzach_hod_yesod": [7, 8, 9],  # Netzach → Hod → Yesod
    "pilar_derecho": [4, 7, 10],  # Chesed → Netzach → Malkuth
    "pilar_izquierdo": [3, 5, 8],  # Binah → Gevurah → Hod
    "pilar_central": [1, 2, 6, 9],  # Keter → Chokmah → Tiferet → Yesod
}

# Pesos para cálculo de scores
DEFAULT_WEIGHTS: Dict[str, float] = {
    "frecuencia": 0.4,
    "ausencia": 0.3,
    "peso_sefira": 0.3
}

# Configuración de visualización
VISUAL_CONFIG: Dict[str, Any] = {
    "node_size_range": (10, 50),
    "edge_width_range": (1, 5),
    "color_scale": "Viridis",
    "hover_template": "<b>%{text}</b><br>Score: %{customdata[0]:.2f}<br>Números: %{customdata[1]}",
    "layout": {
        "title": "Árbol de la Vida - Activación Sefirot",
        "showlegend": True,
        "hovermode": "closest"
    }
}

# Configuración de análisis
ANALYSIS_CONFIG: Dict[str, Any] = {
    "min_absence_for_hidden": 3,
    "min_energy_for_hidden": 7.0,
    "cycle_readiness_threshold": 0.7,
    "harmony_score_threshold": 0.6,
    "top_k_default": 10
}

# Mensajes de interpretación
INTERPRETATION_MESSAGES: Dict[str, str] = {
    "balance_perfecto": "El Árbol está en perfecto equilibrio. Todas las energías fluyen armoniosamente.",
    "desbalance_derecha": "Exceso de energía expansiva. Necesitas más estructura y disciplina.",
    "desbalance_izquierda": "Exceso de energía restrictiva. Necesitas más compasión y flexibilidad.",
    "desbalance_centro": "Falta de conexión espiritual. Necesitas más equilibrio entre acción y contemplación.",
    "ciclo_activo": "Este número está en un ciclo activo y tiene alta probabilidad de aparecer.",
    "ciclo_latente": "Este número está en un ciclo latente pero puede activarse pronto.",
    "numero_oculto": "Número con alta energía sefirotica pero alta ausencia - potencial de reaparición.",
    "armonia_detectada": "Se detectó un patrón de armonía que puede repetirse en próximos sorteos."
}







