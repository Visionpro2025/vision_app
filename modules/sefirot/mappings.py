# modules/sefirot/mappings.py
"""
Mapeos y conversiones para el sistema Sefirot Suite
Funciones para mapear números a Sefirot y conversiones gematría
"""

from typing import Union, List, Dict, Optional
import logging
from .constants import SEFIROT, HEBREW_MAP, HEBREW_VALUES

logger = logging.getLogger(__name__)

def map_to_sefira(number: int) -> int:
    """
    Mapea un número (1-100) a su Sefirá correspondente (1-10).
    
    Usa mapeo circular: (número - 1) % 10 + 1
    Esto asegura distribución uniforme de números en las 10 Sefirot.
    
    Args:
        number: Número a mapear (1-100)
        
    Returns:
        Número de Sefirá (1-10)
        
    Raises:
        ValueError: Si el número está fuera del rango válido
    """
    if not isinstance(number, int):
        raise ValueError(f"El número debe ser entero, recibido: {type(number)}")
    
    if number < 1 or number > 100:
        raise ValueError(f"Número fuera de rango válido (1-100): {number}")
    
    sefira_number = ((number - 1) % 10) + 1
    logger.debug(f"Mapeo {number} → Sefirá {sefira_number}")
    return sefira_number

def number_to_hebrew(number: int) -> str:
    """
    Convierte un número a su representación hebrea.
    
    Para números > 100, usa descomposición en centenas, decenas y unidades.
    
    Args:
        number: Número a convertir (1-1000)
        
    Returns:
        Representación hebrea del número
        
    Raises:
        ValueError: Si el número está fuera del rango válido
    """
    if not isinstance(number, int):
        raise ValueError(f"El número debe ser entero, recibido: {type(number)}")
    
    if number < 1 or number > 1000:
        raise ValueError(f"Número fuera de rango válido (1-1000): {number}")
    
    if number in HEBREW_MAP:
        return HEBREW_MAP[number]
    
    # Descomposición para números compuestos
    result = ""
    
    # Centenas
    if number >= 100:
        centenas = (number // 100) * 100
        if centenas in HEBREW_MAP:
            result += HEBREW_MAP[centenas]
        number = number % 100
    
    # Decenas
    if number >= 10:
        decenas = (number // 10) * 10
        if decenas in HEBREW_MAP:
            result += HEBREW_MAP[decenas]
        number = number % 10
    
    # Unidades
    if number > 0 and number in HEBREW_MAP:
        result += HEBREW_MAP[number]
    
    return result if result else "?"

def hebrew_value(token: str) -> int:
    """
    Calcula el valor gematría de un token hebreo.
    
    Suma los valores de todas las letras hebreas en el token.
    
    Args:
        token: Token hebreo a evaluar
        
    Returns:
        Valor gematría total
        
    Raises:
        ValueError: Si el token contiene caracteres no hebreos válidos
    """
    if not isinstance(token, str):
        raise ValueError(f"El token debe ser string, recibido: {type(token)}")
    
    if not token:
        return 0
    
    total_value = 0
    invalid_chars = []
    
    for char in token:
        if char in HEBREW_VALUES:
            total_value += HEBREW_VALUES[char]
        else:
            invalid_chars.append(char)
    
    if invalid_chars:
        logger.warning(f"Caracteres no hebreos encontrados: {invalid_chars}")
    
    return total_value

def get_sefira_info(number: int) -> Dict[str, Union[str, int, float]]:
    """
    Obtiene información completa de la Sefirá correspondiente a un número.
    
    Args:
        number: Número a mapear (1-100)
        
    Returns:
        Diccionario con información completa de la Sefirá
    """
    sefira_number = map_to_sefira(number)
    sefira_data = SEFIROT[sefira_number]
    
    return {
        "numero_original": number,
        "sefira_number": sefira_number,
        "nombre": sefira_data.nombre,
        "pilar": sefira_data.pilar,
        "peso_base": sefira_data.peso_base,
        "ciclo_sugerido": sefira_data.ciclo_sugerido,
        "coordenadas": sefira_data.coordenadas,
        "color": sefira_data.color,
        "energia": sefira_data.energia,
        "descripcion": sefira_data.descripcion,
        "hebrew_representation": number_to_hebrew(number),
        "hebrew_value": hebrew_value(number_to_hebrew(number))
    }

def map_numbers_to_sefirot(numbers: List[int]) -> Dict[int, Dict[str, Union[str, int, float]]]:
    """
    Mapea una lista de números a sus Sefirot correspondientes.
    
    Args:
        numbers: Lista de números a mapear
        
    Returns:
        Diccionario con mapeo número → información sefirá
    """
    result = {}
    
    for number in numbers:
        try:
            result[number] = get_sefira_info(number)
        except ValueError as e:
            logger.error(f"Error mapeando número {number}: {e}")
            continue
    
    return result

def get_pilar_for_number(number: int) -> str:
    """
    Obtiene el pilar al que pertenece un número.
    
    Args:
        number: Número a evaluar (1-100)
        
    Returns:
        Nombre del pilar (Derecha, Izquierda, Centro)
    """
    sefira_number = map_to_sefira(number)
    return SEFIROT[sefira_number].pilar

def get_energy_for_number(number: int) -> str:
    """
    Obtiene el tipo de energía de un número.
    
    Args:
        number: Número a evaluar (1-100)
        
    Returns:
        Tipo de energía sefirotica
    """
    sefira_number = map_to_sefira(number)
    return SEFIROT[sefira_number].energia

def validate_number_range(number: int, min_val: int = 1, max_val: int = 100) -> bool:
    """
    Valida que un número esté en el rango especificado.
    
    Args:
        number: Número a validar
        min_val: Valor mínimo (inclusive)
        max_val: Valor máximo (inclusive)
        
    Returns:
        True si está en rango, False en caso contrario
    """
    return isinstance(number, int) and min_val <= number <= max_val

def normalize_number_list(numbers: Union[List[int], str, str]) -> List[int]:
    """
    Normaliza una lista de números desde diferentes formatos de entrada.
    
    Args:
        numbers: Lista de enteros, string separado por comas/espacios, o string individual
        
    Returns:
        Lista normalizada de enteros
        
    Raises:
        ValueError: Si no se pueden convertir los números
    """
    if isinstance(numbers, list):
        # Ya es una lista, validar que todos sean enteros
        try:
            return [int(x) for x in numbers if str(x).strip()]
        except ValueError as e:
            raise ValueError(f"Error convirtiendo lista a enteros: {e}")
    
    elif isinstance(numbers, str):
        # String, intentar separar por comas o espacios
        if not numbers.strip():
            return []
        
        # Intentar separar por comas primero, luego por espacios
        separators = [',', ' ', ';', '|']
        parts = [numbers]
        
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = new_parts
        
        # Limpiar y convertir
        try:
            return [int(x.strip()) for x in parts if x.strip()]
        except ValueError as e:
            raise ValueError(f"Error convirtiendo string '{numbers}' a enteros: {e}")
    
    else:
        raise ValueError(f"Tipo de entrada no soportado: {type(numbers)}")

def get_sefira_distribution(numbers: List[int]) -> Dict[int, int]:
    """
    Calcula la distribución de números por Sefirá.
    
    Args:
        numbers: Lista de números a analizar
        
    Returns:
        Diccionario con conteo por Sefirá (1-10)
    """
    distribution = {i: 0 for i in range(1, 11)}
    
    for number in numbers:
        try:
            sefira = map_to_sefira(number)
            distribution[sefira] += 1
        except ValueError:
            continue
    
    return distribution

def get_pilar_distribution(numbers: List[int]) -> Dict[str, int]:
    """
    Calcula la distribución de números por pilar.
    
    Args:
        numbers: Lista de números a analizar
        
    Returns:
        Diccionario con conteo por pilar
    """
    from .constants import PILARES
    
    distribution = {pilar: 0 for pilar in PILARES.keys()}
    
    for number in numbers:
        try:
            pilar = get_pilar_for_number(number)
            distribution[pilar] += 1
        except ValueError:
            continue
    
    return distribution







