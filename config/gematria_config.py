# config/gematria_config.py — Configuración de Gematría Hebrea y Arquetipos

"""
CONFIGURACIÓN DE GEMATRÍA HEBREA Y ARQUETIPOS JUNGIANOS

Este archivo contiene la configuración para el sistema de gematría
que convierte números de lotería en firmas simbólicas arquetipales.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Tuple

# =================== CONFIGURACIÓN DE LETRAS HEBREAS ===================

# Mapeo de números a letras hebreas (gematría tradicional)
HEBREW_LETTERS_CONFIG = {
    1: {"letter": "א", "name": "Alef", "meaning": "Unidad, principio, divinidad"},
    2: {"letter": "ב", "name": "Bet", "meaning": "Casa, bendición, dualidad"},
    3: {"letter": "ג", "name": "Gimel", "meaning": "Camello, generosidad, movimiento"},
    4: {"letter": "ד", "name": "Dalet", "meaning": "Puerta, pobreza, humildad"},
    5: {"letter": "ה", "name": "He", "meaning": "Ventana, respiración, revelación"},
    6: {"letter": "ו", "name": "Vav", "meaning": "Gancho, conexión, unión"},
    7: {"letter": "ז", "name": "Zayin", "meaning": "Espada, alimento, victoria"},
    8: {"letter": "ח", "name": "Chet", "meaning": "Vida, gracia, temor"},
    9: {"letter": "ט", "name": "Tet", "meaning": "Serpiente, bondad, verdad"},
    10: {"letter": "י", "name": "Yud", "meaning": "Mano, trabajo, humildad"},
    20: {"letter": "כ", "name": "Kaf", "meaning": "Palma, corona, bendición"},
    30: {"letter": "ל", "name": "Lamed", "meaning": "Aguijón, enseñanza, aprendizaje"},
    40: {"letter": "מ", "name": "Mem", "meaning": "Agua, maternidad, sabiduría"},
    50: {"letter": "נ", "name": "Nun", "meaning": "Pez, fidelidad, humildad"},
    60: {"letter": "ס", "name": "Samech", "meaning": "Soporte, protección, confianza"},
    70: {"letter": "ע", "name": "Ayin", "meaning": "Ojo, visión, revelación"},
    80: {"letter": "פ", "name": "Pe", "meaning": "Boca, habla, expresión"},
    90: {"letter": "צ", "name": "Tzadi", "meaning": "Justicia, rectitud, pescador"},
    100: {"letter": "ק", "name": "Kuf", "meaning": "Mono, santidad, elevación"},
    200: {"letter": "ר", "name": "Reish", "meaning": "Cabeza, pobreza, liderazgo"},
    300: {"letter": "ש", "name": "Shin", "meaning": "Diente, fuego, cambio"},
    400: {"letter": "ת", "name": "Tav", "meaning": "Marca, verdad, perfección"}
}

# =================== CONFIGURACIÓN DE RAÍCES HEBREAS ===================

# Raíces hebreas de 2-3 letras con significados arquetipales
HEBREW_ROOTS_CONFIG = {
    # Raíces de 2 letras
    "לב": {
        "value": 32,
        "archetype": "Madre/Corazón",
        "meaning": "Amor, compasión, centro emocional",
        "jungian_type": "Anima/Animus",
        "description": "Representa el centro emocional y la capacidad de amar"
    },
    "חי": {
        "value": 18,
        "archetype": "Héroe/Renacimiento",
        "meaning": "Vida, vitalidad, transformación",
        "jungian_type": "Hero",
        "description": "Simboliza la fuerza vital y la capacidad de transformación"
    },
    "לא": {
        "value": 31,
        "archetype": "Sombra/Conflicto",
        "meaning": "Negación, oposición, desafío",
        "jungian_type": "Shadow",
        "description": "Representa la oposición y los desafíos para el crecimiento"
    },
    "יה": {
        "value": 26,
        "archetype": "Sabio/Luz",
        "meaning": "Divinidad, sabiduría, iluminación",
        "jungian_type": "Wise Old Man",
        "description": "Simboliza la sabiduría divina y la iluminación espiritual"
    },
    "עם": {
        "value": 110,
        "archetype": "Comunidad/Pueblo",
        "meaning": "Colectividad, unidad, sociedad",
        "jungian_type": "Collective Unconscious",
        "description": "Representa la unidad colectiva y la identidad grupal"
    },
    "דם": {
        "value": 44,
        "archetype": "Sangre/Pasiones",
        "meaning": "Vitalidad, emociones intensas",
        "jungian_type": "Anima",
        "description": "Simboliza las pasiones y emociones intensas de la vida"
    },
    "שם": {
        "value": 340,
        "archetype": "Nombre/Identidad",
        "meaning": "Esencia, reputación, destino",
        "jungian_type": "Self",
        "description": "Representa la identidad esencial y el destino personal"
    },
    "אור": {
        "value": 207,
        "archetype": "Luz/Revelación",
        "meaning": "Conocimiento, verdad, claridad",
        "jungian_type": "Wise Old Man",
        "description": "Simboliza la revelación de la verdad y el conocimiento"
    },
    "מים": {
        "value": 90,
        "archetype": "Agua/Emociones",
        "meaning": "Fluidez, adaptabilidad, purificación",
        "jungian_type": "Anima",
        "description": "Representa la fluidez emocional y la purificación"
    },
    "אש": {
        "value": 301,
        "archetype": "Fuego/Transformación",
        "meaning": "Pasión, destrucción, renovación",
        "jungian_type": "Trickster",
        "description": "Simboliza la transformación a través del fuego purificador"
    },
    
    # Raíces de 3 letras
    "אדם": {
        "value": 45,
        "archetype": "Humanidad/Consciencia",
        "meaning": "Ser humano, consciencia, potencial",
        "jungian_type": "Self",
        "description": "Representa la consciencia humana y el potencial divino"
    },
    "שלום": {
        "value": 376,
        "archetype": "Paz/Equilibrio",
        "meaning": "Armonía, reconciliación, plenitud",
        "jungian_type": "Self",
        "description": "Simboliza la armonía interior y la reconciliación"
    },
    "אמת": {
        "value": 441,
        "archetype": "Verdad/Integridad",
        "meaning": "Autenticidad, honestidad, realidad",
        "jungian_type": "Wise Old Man",
        "description": "Representa la verdad absoluta y la integridad moral"
    },
    "חסד": {
        "value": 72,
        "archetype": "Gracia/Bondad",
        "meaning": "Misericordia, generosidad, amor incondicional",
        "jungian_type": "Anima",
        "description": "Simboliza la gracia divina y la bondad incondicional"
    },
    "דין": {
        "value": 64,
        "archetype": "Justicia/Juicio",
        "meaning": "Ley, orden, evaluación",
        "jungian_type": "Wise Old Man",
        "description": "Representa la justicia divina y el juicio moral"
    },
    "תפילה": {
        "value": 515,
        "archetype": "Oración/Conectividad",
        "meaning": "Comunicación divina, intención",
        "jungian_type": "Self",
        "description": "Simboliza la conexión con lo divino a través de la oración"
    },
    "תשובה": {
        "value": 713,
        "archetype": "Retorno/Arrepentimiento",
        "meaning": "Transformación, cambio de dirección",
        "jungian_type": "Hero",
        "description": "Representa el retorno espiritual y la transformación"
    },
    "גאולה": {
        "value": 45,
        "archetype": "Redención/Liberación",
        "meaning": "Salvación, liberación, nueva oportunidad",
        "jungian_type": "Self",
        "description": "Simboliza la redención y la liberación espiritual"
    }
}

# =================== CONFIGURACIÓN DE ARQUETIPOS JUNGIANOS ===================

# Arquetipos jungianos asociados a emociones y temas
ARCHETYPE_MAPPING_CONFIG = {
    # Arquetipos por emoción
    "ira": {
        "archetypes": ["Guerrero", "Sombra", "Destructor"],
        "description": "Emociones de enojo y frustración",
        "jungian_type": "Shadow/Animus",
        "positive_aspects": ["Protección", "Justicia", "Transformación"],
        "negative_aspects": ["Violencia", "Destrucción", "Odio"]
    },
    "miedo": {
        "archetypes": ["Huérfano", "Víctima", "Sombra"],
        "description": "Emociones de temor y ansiedad",
        "jungian_type": "Shadow",
        "positive_aspects": ["Prudencia", "Protección", "Crecimiento"],
        "negative_aspects": ["Parálisis", "Pánico", "Fuga"]
    },
    "esperanza": {
        "archetypes": ["Héroe", "Sabio", "Creador"],
        "description": "Emociones de optimismo y confianza",
        "jungian_type": "Hero/Wise Old Man",
        "positive_aspects": ["Inspiración", "Fe", "Transformación"],
        "negative_aspects": ["Ilusión", "Desconexión", "Escape"]
    },
    "tristeza": {
        "archetypes": ["Huérfano", "Mártir", "Sombra"],
        "description": "Emociones de pena y desesperación",
        "jungian_type": "Shadow/Anima",
        "positive_aspects": ["Reflexión", "Compasión", "Curación"],
        "negative_aspects": ["Depresión", "Auto-compasión", "Estancamiento"]
    },
    "orgullo": {
        "archetypes": ["Héroe", "Rey", "Creador"],
        "description": "Emociones de dignidad y logro",
        "jungian_type": "Hero/King",
        "positive_aspects": ["Confianza", "Logro", "Liderazgo"],
        "negative_aspects": ["Arrogancia", "Narcisismo", "Separación"]
    },
    
    # Arquetipos por tema
    "economia_dinero": {
        "archetypes": ["Mercader", "Rey", "Mago"],
        "description": "Temas económicos y financieros",
        "jungian_type": "Trickster/King",
        "positive_aspects": ["Prosperidad", "Sabiduría", "Transformación"],
        "negative_aspects": ["Codicia", "Explotación", "Materialismo"]
    },
    "politica_justicia": {
        "archetypes": ["Guerrero", "Juez", "Líder"],
        "description": "Temas políticos y de justicia social",
        "jungian_type": "Hero/Wise Old Man",
        "positive_aspects": ["Justicia", "Liderazgo", "Protección"],
        "negative_aspects": ["Autoritarismo", "Corrupción", "Opresión"]
    },
    "seguridad_social": {
        "archetypes": ["Guardián", "Guerrero", "Sanador"],
        "description": "Temas de seguridad y orden social",
        "jungian_type": "Hero/Anima",
        "positive_aspects": ["Protección", "Curación", "Orden"],
        "negative_aspects": ["Represión", "Violencia", "Control"]
    }
}

# =================== VALORES NUMÉRICOS ESPECIALES ===================

# Valores numéricos especiales (números compuestos)
SPECIAL_VALUES_CONFIG = {
    26: {
        "hebrew": "יה",
        "meaning": "Nombre divino",
        "archetype": "Sabio/Luz",
        "description": "Representa la presencia divina y la sabiduría"
    },
    18: {
        "hebrew": "חי",
        "meaning": "Vida",
        "archetype": "Héroe/Renacimiento",
        "description": "Simboliza la bendición de la vida"
    },
    32: {
        "hebrew": "לב",
        "meaning": "Corazón",
        "archetype": "Madre/Corazón",
        "description": "Representa el centro emocional y la sabiduría"
    },
    45: {
        "hebrew": "מה",
        "meaning": "¿Qué? (pregunta existencial)",
        "archetype": "Sabio/Luz",
        "description": "Simboliza la búsqueda de significado"
    },
    70: {
        "hebrew": "ע",
        "meaning": "Ojo (visión)",
        "archetype": "Sabio/Luz",
        "description": "Representa la visión espiritual y la revelación"
    },
    91: {
        "hebrew": "אמן",
        "meaning": "Amén (confirmación)",
        "archetype": "Sabio/Luz",
        "description": "Simboliza la confirmación divina"
    },
    111: {
        "hebrew": "אלא",
        "meaning": "Pero (contradicción)",
        "archetype": "Sombra/Conflicto",
        "description": "Representa la contradicción y el desafío"
    },
    365: {
        "hebrew": "שנה",
        "meaning": "Año (ciclo completo)",
        "archetype": "Héroe/Renacimiento",
        "description": "Simboliza el ciclo completo de la vida"
    },
    613: {
        "hebrew": "תרי״ג",
        "meaning": "Mitzvot (mandamientos)",
        "archetype": "Sabio/Luz",
        "description": "Representa la sabiduría de la ley divina"
    }
}

# =================== FUNCIONES DE UTILIDAD ===================

def get_hebrew_letter_info(number: int) -> Dict:
    """Obtiene información completa de una letra hebrea por número."""
    if number in HEBREW_LETTERS_CONFIG:
        return HEBREW_LETTERS_CONFIG[number]
    return None

def get_hebrew_root_info(root: str) -> Dict:
    """Obtiene información completa de una raíz hebrea."""
    if root in HEBREW_ROOTS_CONFIG:
        return HEBREW_ROOTS_CONFIG[root]
    return None

def get_archetype_info(emotion: str, theme: str = None) -> Dict:
    """Obtiene información de arquetipos por emoción y tema."""
    result = {}
    
    if emotion in ARCHETYPE_MAPPING_CONFIG:
        result["emotion"] = ARCHETYPE_MAPPING_CONFIG[emotion]
    
    if theme and theme in ARCHETYPE_MAPPING_CONFIG:
        result["theme"] = ARCHETYPE_MAPPING_CONFIG[theme]
    
    return result

def get_special_value_info(value: int) -> Dict:
    """Obtiene información de un valor numérico especial."""
    if value in SPECIAL_VALUES_CONFIG:
        return SPECIAL_VALUES_CONFIG[value]
    return None

def get_all_archetypes() -> List[str]:
    """Obtiene lista de todos los arquetipos disponibles."""
    archetypes = set()
    
    # Arquetipos de emociones
    for emotion_config in ARCHETYPE_MAPPING_CONFIG.values():
        if "archetypes" in emotion_config:
            archetypes.update(emotion_config["archetypes"])
    
    # Arquetipos de raíces hebreas
    for root_config in HEBREW_ROOTS_CONFIG.values():
        if "archetype" in root_config:
            archetypes.add(root_config["archetype"])
    
    return sorted(list(archetypes))

# =================== EJEMPLO DE USO ===================

if __name__ == "__main__":
    print("🔮 CONFIGURACIÓN DE GEMATRÍA HEBREA Y ARQUETIPOS")
    print("=" * 60)
    
    # Mostrar información de letras hebreas
    print("📜 LETRAS HEBREAS:")
    for number, info in list(HEBREW_LETTERS_CONFIG.items())[:5]:
        print(f"   {number}: {info['letter']} ({info['name']}) - {info['meaning']}")
    
    # Mostrar información de raíces hebreas
    print(f"\n🌱 RAÍCES HEBREAS:")
    for root, info in list(HEBREW_ROOTS_CONFIG.items())[:5]:
        print(f"   {root}: {info['archetype']} - {info['meaning']}")
    
    # Mostrar información de arquetipos
    print(f"\n👥 ARQUETIPOS JUNGIANOS:")
    for emotion, info in ARCHETYPE_MAPPING_CONFIG.items():
        if "archetypes" in info:
            print(f"   {emotion}: {', '.join(info['archetypes'])}")
    
    # Mostrar valores especiales
    print(f"\n⭐ VALORES ESPECIALES:")
    for value, info in SPECIAL_VALUES_CONFIG.items():
        print(f"   {value}: {info['hebrew']} - {info['meaning']}")
    
    # Mostrar todos los arquetipos disponibles
    print(f"\n🎯 TOTAL ARQUETIPOS DISPONIBLES:")
    all_archetypes = get_all_archetypes()
    print(f"   {len(all_archetypes)} arquetipos: {', '.join(all_archetypes[:10])}...")
    
    print(f"\n✅ Configuración de gematría cargada correctamente")
