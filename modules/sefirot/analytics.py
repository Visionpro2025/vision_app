# modules/sefirot/analytics.py
"""
Análisis de frecuencias, ausencias y scores para el sistema Sefirot Suite
Métricas base para el análisis predictivo de sorteos
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging
from .constants import SEFIROT, DEFAULT_WEIGHTS
from .mappings import map_to_sefira, get_sefira_info

logger = logging.getLogger(__name__)

def compute_frequency_absence(df: pd.DataFrame, last_n: int) -> pd.DataFrame:
    """
    Calcula frecuencia absoluta y ausencia para todos los números en los últimos N sorteos.
    
    Args:
        df: DataFrame con columnas ["sorteo_id", "numeros"] (numeros = lista/str)
        last_n: Número de sorteos recientes a analizar
        
    Returns:
        DataFrame con columnas [numero, freq_abs, ausencia, sefira, pilar, energia]
    """
    if df.empty:
        logger.warning("DataFrame vacío proporcionado")
        return pd.DataFrame(columns=['numero', 'freq_abs', 'ausencia', 'sefira', 'pilar', 'energia'])
    
    # Validar columnas requeridas
    required_columns = ['sorteo_id', 'numeros']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Columnas faltantes: {missing_columns}")
    
    # Obtener últimos N sorteos
    recent_draws = df.tail(last_n).copy()
    
    # Normalizar números a listas de enteros
    recent_draws['numeros_list'] = recent_draws['numeros'].apply(_normalize_numbers)
    
    # Obtener todos los números únicos
    all_numbers = set()
    for numeros_list in recent_draws['numeros_list']:
        all_numbers.update(numeros_list)
    
    all_numbers = sorted(list(all_numbers))
    
    # Calcular métricas para cada número
    results = []
    
    for numero in all_numbers:
        # Calcular frecuencia absoluta
        freq_abs = _calculate_frequency(numero, recent_draws['numeros_list'])
        
        # Calcular ausencia (sorteos consecutivos sin aparición)
        ausencia = _calculate_absence(numero, recent_draws['numeros_list'])
        
        # Obtener información sefirotica
        try:
            sefira_info = get_sefira_info(numero)
            sefira = sefira_info['sefira_number']
            pilar = sefira_info['pilar']
            energia = sefira_info['energia']
        except Exception as e:
            logger.warning(f"Error obteniendo info sefirotica para {numero}: {e}")
            sefira = map_to_sefira(numero)
            pilar = SEFIROT[sefira].pilar
            energia = SEFIROT[sefira].energia
        
        results.append({
            'numero': numero,
            'freq_abs': freq_abs,
            'ausencia': ausencia,
            'sefira': sefira,
            'pilar': pilar,
            'energia': energia
        })
    
    return pd.DataFrame(results)

def _normalize_numbers(numbers: Union[List[int], str, Any]) -> List[int]:
    """Normaliza números desde diferentes formatos."""
    if isinstance(numbers, list):
        return [int(x) for x in numbers if str(x).strip()]
    elif isinstance(numbers, str):
        if not numbers.strip():
            return []
        # Intentar separar por comas, espacios, etc.
        parts = numbers.replace(',', ' ').replace(';', ' ').split()
        return [int(x.strip()) for x in parts if x.strip()]
    else:
        return []

def _calculate_frequency(number: int, numeros_lists: pd.Series) -> int:
    """Calcula frecuencia absoluta de un número."""
    count = 0
    for numeros_list in numeros_lists:
        if number in numeros_list:
            count += 1
    return count

def _calculate_absence(number: int, numeros_lists: pd.Series) -> int:
    """Calcula ausencia (sorteos consecutivos sin aparición)."""
    absence_count = 0
    for numeros_list in numeros_lists:
        if number not in numeros_list:
            absence_count += 1
        else:
            break  # Reset al encontrar el número
    return absence_count

def score_number(row: pd.Series, weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calcula el score ponderado de un número basado en frecuencia, ausencia y peso sefirotico.
    
    Args:
        row: Fila del DataFrame con columnas freq_abs, ausencia, sefira
        weights: Pesos para el cálculo (frecuencia, ausencia, peso_sefira)
        
    Returns:
        Score ponderado
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Obtener peso sefirotico
    sefira = row['sefira']
    peso_sefira = SEFIROT[sefira].peso_base
    
    # Calcular score
    score = (
        row['freq_abs'] * weights['frecuencia'] +
        row['ausencia'] * weights['ausencia'] +
        peso_sefira * weights['peso_sefira']
    )
    
    return round(score, 4)

def rank_numbers(freq_df: pd.DataFrame, weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """
    Crea ranking de números ordenado por score descendente.
    
    Args:
        freq_df: DataFrame con métricas de frecuencia/ausencia
        weights: Pesos para el cálculo de score
        
    Returns:
        DataFrame con columnas [numero, sefira, freq_abs, ausencia, score] ordenado desc
    """
    if freq_df.empty:
        return pd.DataFrame(columns=['numero', 'sefira', 'freq_abs', 'ausencia', 'score'])
    
    # Calcular scores
    freq_df = freq_df.copy()
    freq_df['score'] = freq_df.apply(lambda row: score_number(row, weights), axis=1)
    
    # Ordenar por score descendente
    ranked_df = freq_df.sort_values('score', ascending=False).reset_index(drop=True)
    ranked_df['rank'] = range(1, len(ranked_df) + 1)
    
    # Seleccionar columnas de salida
    output_columns = ['rank', 'numero', 'sefira', 'freq_abs', 'ausencia', 'score']
    return ranked_df[output_columns]

def calculate_sefira_aggregates(freq_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas agregadas por Sefirá.
    
    Args:
        freq_df: DataFrame con métricas por número
        
    Returns:
        DataFrame con métricas agregadas por Sefirá
    """
    if freq_df.empty:
        return pd.DataFrame()
    
    # Agregar información sefirotica si no está presente
    if 'sefira' not in freq_df.columns:
        freq_df = freq_df.copy()
        freq_df['sefira'] = freq_df['numero'].apply(map_to_sefira)
    
    # Agregar por Sefirá
    aggregates = freq_df.groupby('sefira').agg({
        'numero': 'count',
        'freq_abs': ['sum', 'mean', 'max'],
        'ausencia': ['sum', 'mean', 'max'],
        'score': ['sum', 'mean', 'max']
    }).round(4)
    
    # Aplanar columnas multi-nivel
    aggregates.columns = ['_'.join(col).strip() for col in aggregates.columns]
    aggregates = aggregates.reset_index()
    
    # Agregar información de Sefirot
    aggregates['nombre'] = aggregates['sefira'].apply(lambda x: SEFIROT[x].nombre)
    aggregates['pilar'] = aggregates['sefira'].apply(lambda x: SEFIROT[x].pilar)
    aggregates['energia'] = aggregates['sefira'].apply(lambda x: SEFIROT[x].energia)
    
    return aggregates

def detect_trends(freq_df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """
    Detecta tendencias en la aparición de números.
    
    Args:
        freq_df: DataFrame con métricas por número
        window: Ventana para análisis de tendencia
        
    Returns:
        DataFrame con información de tendencias
    """
    if freq_df.empty:
        return pd.DataFrame()
    
    trends = []
    
    for _, row in freq_df.iterrows():
        numero = row['numero']
        freq = row['freq_abs']
        ausencia = row['ausencia']
        
        # Clasificar tendencia
        if freq >= 3:
            trend = "Alta frecuencia"
        elif freq >= 2:
            trend = "Frecuencia media"
        elif ausencia >= 3:
            trend = "Alta ausencia"
        elif ausencia >= 2:
            trend = "Ausencia media"
        else:
            trend = "Estable"
        
        trends.append({
            'numero': numero,
            'sefira': row.get('sefira', map_to_sefira(numero)),
            'trend': trend,
            'freq_abs': freq,
            'ausencia': ausencia,
            'score': row.get('score', 0)
        })
    
    return pd.DataFrame(trends)

def calculate_correlation_matrix(freq_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula matriz de correlación entre Sefirot basada en apariciones.
    
    Args:
        freq_df: DataFrame con métricas por número
        
    Returns:
        Matriz de correlación entre Sefirot
    """
    if freq_df.empty:
        return pd.DataFrame()
    
    # Crear matriz de apariciones por Sefirá
    sefira_matrix = freq_df.groupby('sefira')['freq_abs'].sum().to_dict()
    
    # Inicializar matriz de correlación
    sefirot_numbers = list(SEFIROT.keys())
    correlation_matrix = pd.DataFrame(
        index=sefirot_numbers,
        columns=sefirot_numbers
    )
    
    # Calcular correlaciones (simplificado)
    for sefira_a in sefirot_numbers:
        for sefira_b in sefirot_numbers:
            if sefira_a == sefira_b:
                correlation_matrix.loc[sefira_a, sefira_b] = 1.0
            else:
                # Correlación basada en pesos sefiroticos
                peso_a = SEFIROT[sefira_a].peso_base
                peso_b = SEFIROT[sefira_b].peso_base
                correlation = min(peso_a, peso_b) / max(peso_a, peso_b)
                correlation_matrix.loc[sefira_a, sefira_b] = round(correlation, 4)
    
    return correlation_matrix

def generate_insights(freq_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera insights automáticos del análisis.
    
    Args:
        freq_df: DataFrame con métricas por número
        
    Returns:
        Diccionario con insights generados
    """
    if freq_df.empty:
        return {"error": "No hay datos para analizar"}
    
    insights = {}
    
    # Número más frecuente
    if 'freq_abs' in freq_df.columns:
        max_freq_idx = freq_df['freq_abs'].idxmax()
        insights['numero_mas_frecuente'] = {
            'numero': freq_df.loc[max_freq_idx, 'numero'],
            'frecuencia': freq_df.loc[max_freq_idx, 'freq_abs']
        }
    
    # Número con mayor ausencia
    if 'ausencia' in freq_df.columns:
        max_ausencia_idx = freq_df['ausencia'].idxmax()
        insights['numero_mas_ausente'] = {
            'numero': freq_df.loc[max_ausencia_idx, 'numero'],
            'ausencia': freq_df.loc[max_ausencia_idx, 'ausencia']
        }
    
    # Sefirá más activa
    if 'sefira' in freq_df.columns:
        sefira_counts = freq_df['sefira'].value_counts()
        insights['sefira_mas_activa'] = {
            'sefira': sefira_counts.index[0],
            'nombre': SEFIROT[sefira_counts.index[0]].nombre,
            'conteo': sefira_counts.iloc[0]
        }
    
    # Estadísticas generales
    insights['estadisticas'] = {
        'total_numeros': len(freq_df),
        'frecuencia_promedio': freq_df['freq_abs'].mean() if 'freq_abs' in freq_df.columns else 0,
        'ausencia_promedio': freq_df['ausencia'].mean() if 'ausencia' in freq_df.columns else 0,
        'score_promedio': freq_df['score'].mean() if 'score' in freq_df.columns else 0
    }
    
    return insights







