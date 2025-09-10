# === MÓDULO SUBLIMINAL v1.2 (Pick 3 Florida / extensible a otros juegos) ===
# - Genera "pistas poéticas" + "temas de noticias" a partir del sorteo anterior.
# - Pensado para 2 sorteos diarios (AM/PM) de Pick 3 Florida.
# - Extensible a MegaMillions/Powerball mediante mapeos y hooks.
# - Integrable con tu Paso 5 (semejantes gemátricos).
# Autor: App.Vision

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# -----------------------------------------------------------------------------
# 1) CONFIGURACIÓN DE JUEGOS Y RANGOS
# -----------------------------------------------------------------------------
@dataclass
class GameConfig:
    name: str
    white_min: int
    white_max: int
    # Opcionalmente para juegos con bola especial (no aplica Pick3):
    special_min: Optional[int] = None
    special_max: Optional[int] = None

PICK3_FL = GameConfig(name="Pick3_FL", white_min=0, white_max=9)
MEGA = GameConfig(name="MegaMillions", white_min=1, white_max=70, special_min=1, special_max=25)
POWER = GameConfig(name="Powerball", white_min=1, white_max=69, special_min=1, special_max=26)

# -----------------------------------------------------------------------------
# 2) DICCIONARIOS GEMÁTRICOS Y SIMBÓLICOS (núcleo mínimo; puedes ampliar)
# -----------------------------------------------------------------------------
# Valores gemátricos hebreos clásicos y asociaciones simbólicas. En Pick3 (0–9)
# usamos equivalentes compactos (0→"vacío/portal", 1→Alef, etc.).
GEMATRIA_CORE: Dict[int, Dict[str, List[str] | str]] = {
    # 0–9 para Pick3
    0: {"hebrew": "-", "symbols": ["vacío", "portal", "cero", "origen"]},
    1: {"hebrew": "א (Alef)", "symbols": ["comienzo", "aliento", "unidad", "toro"]},
    2: {"hebrew": "ב (Bet)", "symbols": ["casa", "contenedor", "dualidad"]},
    3: {"hebrew": "ג (Guímel)", "symbols": ["camello", "tránsito", "provisión"]},
    4: {"hebrew": "ד (Dálet)", "symbols": ["puerta", "umbral", "acceso"]},
    5: {"hebrew": "ה (He)", "symbols": ["soplo", "revelación", "ventana"]},
    6: {"hebrew": "ו (Vav)", "symbols": ["clavo", "conexión", "unión"]},
    7: {"hebrew": "ז (Zayin)", "symbols": ["arma", "corte", "decisión"]},
    8: {"hebrew": "ח (Jet)", "symbols": ["valla", "vida", "ciclo"]},
    9: {"hebrew": "ט (Tet)", "symbols": ["serpiente", "oculto", "giro"]},

    # Núcleo 10–70 (útiles cuando conectes con Mega/Power/Paso 5)
    10: {"hebrew": "י (Yod)", "symbols": ["semilla", "mano", "destello"]},
    20: {"hebrew": "כ (Kaf)", "symbols": ["palma", "dominio", "forma"]},
    30: {"hebrew": "ל (Lámed)", "symbols": ["aguijón", "aprendizaje", "guía"]},
    40: {"hebrew": "מ (Mem)", "symbols": ["agua", "flujo", "gestación"]},
    50: {"hebrew": "נ (Nun)", "symbols": ["pez", "continuidad", "linaje"]},
    60: {"hebrew": "ס (Sámej)", "symbols": ["soporte", "anillo", "protección"]},
    70: {"hebrew": "ע (Ayin)", "symbols": ["ojo", "visión", "fuente"]},
}

# Sugerencias simbólicas complementarias por patrón/carácter
AUX_LEXICON: Dict[str, List[str]] = {
    "apertura": ["apertura", "inauguración", "lanzamiento", "umbral", "portal"],
    "corte": ["corte", "arma", "veredicto", "decisión", "cirugía"],
    "flujo": ["lluvia", "agua", "río", "mareas", "derrame"],
    "cielo": ["eclipse", "cometa", "constelación", "tormenta solar", "satélite"],
    "serpiente": ["serpiente", "veneno", "reptil", "antídoto", "molting"],
    "casa": ["hogar", "vivienda", "propiedad", "inmueble", "refugio"],
    "migración": ["tránsito", "movilidad", "frontera", "caravana", "puente"],
    "economía": ["mercado", "divisa", "inflación", "bonos", "crédito"],
}

# -----------------------------------------------------------------------------
# 3) UTILIDADES DE MAPEADO Y ENSAMBLAJE
# -----------------------------------------------------------------------------
def num_to_symbols(n: int) -> Tuple[str, List[str]]:
    """
    Devuelve (hebrew_label, symbols[]) para un dígito 0–9 o un valor clave 10..70.
    Si no existe entrada, aproxima por decenas (e.g., 61→'60') o devuelve genérico.
    """
    if n in GEMATRIA_CORE:
        entry = GEMATRIA_CORE[n]
        return entry["hebrew"], list(entry["symbols"])  # copia defensiva

    # Aproximación por decena para ≥10
    if n >= 10:
        base = (n // 10) * 10
        if base in GEMATRIA_CORE:
            entry = GEMATRIA_CORE[base]
            # añadimos matiz por unidad
            delta = n - base
            extra = []
            if delta in (1, 2, 3):
                extra = ["crecimiento", "extensión", "eco"]
            return entry["hebrew"], list(entry["symbols"]) + extra

    # fallback genérico
    return "-", ["señal", "eco", "rastro"]

def merge_keywords(symbols_list: List[List[str]]) -> List[str]:
    """Une y depura palabras clave manteniendo orden aproximado y unicidad."""
    seen, out = set(), []
    for group in symbols_list:
        for w in group:
            if w not in seen:
                seen.add(w)
                out.append(w)
    return out

def enrich_topics(base_keywords: List[str], max_topics: int = 6) -> List[str]:
    """
    Expande palabras clave con AUX_LEXICON y devuelve temas de noticia buscables.
    """
    topics = set()
    for w in base_keywords:
        # Mapea por familias
        if w in ("puerta", "umbral", "acceso", "portal"):
            topics.update(AUX_LEXICON["apertura"])
        if w in ("arma", "corte", "decisión"):
            topics.update(AUX_LEXICON["corte"])
        if w in ("agua", "flujo", "gestación", "lluvia", "río"):
            topics.update(AUX_LEXICON["flujo"])
        if w in ("cielo", "visión", "destello", "ojo"):
            topics.update(AUX_LEXICON["cielo"])
        if w in ("serpiente", "veneno", "oculto"):
            topics.update(AUX_LEXICON["serpiente"])
        if w in ("casa", "contenedor", "refugio"):
            topics.update(AUX_LEXICON["casa"])
        if w in ("tránsito", "camello", "puente", "conexión"):
            topics.update(AUX_LEXICON["migración"])
        if w in ("dominio", "mercado", "forma", "mano"):
            topics.update(AUX_LEXICON["economía"])

    # Selección determinista y acotada
    topics = list(topics)[:max_topics]
    return topics

# -----------------------------------------------------------------------------
# 4) MOTOR DE POESÍA SUBLIMINAL
# -----------------------------------------------------------------------------
def compose_poem(digits: List[int],
                 hebrews: List[str],
                 keywords: List[str],
                 draw_label: str,
                 date_str: Optional[str] = None) -> str:
    """
    Ensambla un poema corto, sugestivo y direccionado a la búsqueda de señales.
    """
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    hline = " · ".join([h for h in hebrews if h != "-"]) or "—"
    kline = ", ".join(keywords[:5])

    # Plantilla poética; minimalista y operacional
    poem = (
f"({draw_label} · {date_str})\n"
f"{hline}\n"
f"Abre la señal y escucha el tránsito del día:\n"
f"{kline}.\n"
f"Donde el umbral se encuentre con la decisión,\n"
f"allí la noticia revelará su cifra."
    )
    return poem

# -----------------------------------------------------------------------------
# 5) INTERFAZ PÚBLICA: PICK3 (AM/PM) + EXTENSIONES
# -----------------------------------------------------------------------------
@dataclass
class SubliminalOutput:
    game: str
    draw_label: str
    input_draw: Tuple[int, int, int]
    hebrew_labels: List[str]
    base_keywords: List[str]
    news_topics: List[str]
    poem: str
    # Hook futuro: candidatos Paso 5 (semejantes) o "indicados"
    hinted_numbers: List[int] = field(default_factory=list)

def subliminal_from_pick3(prev_draw: Tuple[int, int, int],
                          draw_label: str,
                          hinted_numbers: Optional[List[int]] = None) -> SubliminalOutput:
    """
    Genera el paquete subliminal para Pick3 a partir del sorteo anterior (d1,d2,d3).
    - draw_label: "AM" o "PM".
    - hinted_numbers: opcional, números "indicados" por tu pipeline (Paso 5, etc.)
    """
    d1, d2, d3 = prev_draw
    heb1, sym1 = num_to_symbols(d1)
    heb2, sym2 = num_to_symbols(d2)
    heb3, sym3 = num_to_symbols(d3)

    hebs = [heb1, heb2, heb3]
    keywords = merge_keywords([sym1, sym2, sym3])

    topics = enrich_topics(keywords, max_topics=6)
    poem = compose_poem([d1, d2, d3], hebs, keywords, draw_label=draw_label)

    return SubliminalOutput(
        game="Pick3_FL",
        draw_label=draw_label,
        input_draw=(d1, d2, d3),
        hebrew_labels=hebs,
        base_keywords=keywords,
        news_topics=topics,
        poem=poem,
        hinted_numbers=list(hinted_numbers or [])
    )

# -----------------------------------------------------------------------------
# 6) PUNTOS DE INTEGRACIÓN CON PASO 5 (Mega/Power) - OPCIONALES
# -----------------------------------------------------------------------------
def subliminal_from_candidates(candidates: List[int],
                               game_cfg: GameConfig,
                               draw_label: str,
                               keep_top_k: int = 5) -> SubliminalOutput:
    """
    Versión genérica: toma candidatos (p.ej., 'semejantes gemátricos' del Paso 5)
    y produce la misma salida subliminal (poema + topics) para juegos 1..70/69.
    """
    picked = candidates[:keep_top_k] if candidates else []
    hebs, sym_groups = [], []
    for v in picked:
        heb, syms = num_to_symbols(v)
        hebs.append(heb)
        sym_groups.append(syms)

    keywords = merge_keywords(sym_groups)
    topics = enrich_topics(keywords, max_topics=6)
    poem = compose_poem(picked, hebs, keywords, draw_label=draw_label)

    return SubliminalOutput(
        game=game_cfg.name,
        draw_label=draw_label,
        input_draw=tuple(picked[:3] + [None]*(3-len(picked[:3]))),  # compat mínima
        hebrew_labels=hebs,
        base_keywords=keywords,
        news_topics=topics,
        poem=poem,
        hinted_numbers=picked
    )

# -----------------------------------------------------------------------------
# 7) EJEMPLO RÁPIDO (puedes comentar en producción)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Ejemplo: último Pick3 fue 4-7-9, y queremos pista para el siguiente (AM o PM)
    out_am = subliminal_from_pick3((4,7,9), draw_label="AM")
    print("=== SUBLIMINAL (AM) ===")
    print("Hewbrew:", out_am.hebrew_labels)
    print("Keywords:", out_am.base_keywords)
    print("News Topics:", out_am.news_topics)
    print(out_am.poem)

    # Ejemplo con candidatos (p.ej. MegaMillions Paso 5) → pista genérica
    out_mega = subliminal_from_candidates([26, 52, 61, 34], game_cfg=MEGA, draw_label="NOCHE")
    print("\n=== SUBLIMINAL (Mega) ===")
    print("Hewbrew:", out_mega.hebrew_labels)
    print("Keywords:", out_mega.base_keywords)
    print("News Topics:", out_mega.news_topics)
    print(out_mega.poem)






