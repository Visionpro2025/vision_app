# modules/sefirot/sefirot_five.py
"""
Sefirot Five - Análisis de Últimos 5 Sorteos
Flujo optimizado para análisis sefirot usando siempre los últimos 5 sorteos
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import os

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar mapeos sefirot
from .mappings import map_to_sefira, get_sefira_info
from .constants import SEFIROT

def load_draws(source: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
    """
    Carga datos de sorteos desde CSV o DataFrame.
    
    Si el archivo no existe o faltan columnas, genera dataset sintético de 5 sorteos.
    
    Args:
        source: Ruta al CSV, Path o DataFrame existente
        
    Returns:
        DataFrame con columnas ["sorteo_id", "fecha", "numeros"]
    """
    try:
        if isinstance(source, pd.DataFrame):
            df = source.copy()
            logger.info("Usando DataFrame proporcionado")
        elif isinstance(source, (str, Path)):
            source_path = Path(source)
            if source_path.exists():
                df = pd.read_csv(source_path)
                logger.info(f"Datos cargados desde: {source_path}")
            else:
                logger.warning(f"Archivo no encontrado: {source_path}. Generando datos sintéticos.")
                df = _generate_synthetic_data()
        else:
            raise ValueError(f"Tipo de fuente no soportado: {type(source)}")
        
        # Validar columnas requeridas
        required_columns = ["sorteo_id", "fecha", "numeros"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Columnas faltantes: {missing_columns}. Generando datos sintéticos.")
            df = _generate_synthetic_data()
        
        # Validar que no esté vacío
        if df.empty:
            logger.warning("DataFrame vacío. Generando datos sintéticos.")
            df = _generate_synthetic_data()
        
        logger.info(f"Dataset cargado: {len(df)} sorteos")
        return df
        
    except Exception as e:
        logger.error(f"Error cargando datos: {e}. Generando datos sintéticos.")
        return _generate_synthetic_data()

def _generate_synthetic_data() -> pd.DataFrame:
    """
    Genera dataset sintético de 5 sorteos para pruebas.
    
    Returns:
        DataFrame con 5 sorteos sintéticos
    """
    np.random.seed(42)  # Para reproducibilidad
    
    sorteos = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(5):
        # Generar 5 números aleatorios entre 1 y 100
        numeros = sorted(np.random.choice(range(1, 101), size=5, replace=False))
        
        sorteos.append({
            'sorteo_id': i + 1,
            'fecha': (base_date + timedelta(days=i*7)).strftime('%Y-%m-%d'),
            'numeros': numeros
        })
    
    df = pd.DataFrame(sorteos)
    logger.info("Dataset sintético generado con 5 sorteos")
    return df

def normalize_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza columna numeros a List[int] y limpia duplicados por sorteo.
    
    Args:
        df: DataFrame con columna 'numeros'
        
    Returns:
        DataFrame con numeros normalizados
    """
    df = df.copy()
    
    def _normalize_single(numbers: Union[List[int], str, Any]) -> List[int]:
        """Normaliza una entrada individual de números."""
        if isinstance(numbers, list):
            # Ya es lista, validar que sean enteros
            try:
                return [int(x) for x in numbers if str(x).strip()]
            except ValueError:
                return []
        elif isinstance(numbers, str):
            if not numbers.strip():
                return []
            # Separar por comas, espacios, etc.
            parts = numbers.replace(',', ' ').replace(';', ' ').replace('|', ' ').split()
            try:
                return [int(x.strip()) for x in parts if x.strip()]
            except ValueError:
                return []
        else:
            return []
    
    # Normalizar columna numeros
    df['numeros'] = df['numeros'].apply(_normalize_single)
    
    # Limpiar duplicados por sorteo y ordenar
    df['numeros'] = df['numeros'].apply(lambda x: sorted(list(set(x))))
    
    # Filtrar sorteos sin números válidos
    df = df[df['numeros'].apply(len) > 0].copy()
    
    logger.info(f"Números normalizados. Sorteos válidos: {len(df)}")
    return df

def select_last_n(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """
    Selecciona los últimos N sorteos ordenados por fecha o sorteo_id.
    
    Args:
        df: DataFrame con sorteos
        n: Número de sorteos a seleccionar (default: 5)
        
    Returns:
        DataFrame con últimos N sorteos
    """
    if df.empty:
        logger.warning("DataFrame vacío para selección")
        return df
    
    # Ordenar por fecha si existe, sino por sorteo_id
    if 'fecha' in df.columns:
        try:
            df['fecha_parsed'] = pd.to_datetime(df['fecha'])
            df_sorted = df.sort_values('fecha_parsed').copy()
        except:
            df_sorted = df.sort_values('sorteo_id').copy()
    else:
        df_sorted = df.sort_values('sorteo_id').copy()
    
    # Seleccionar últimos N
    last_n = df_sorted.tail(n).copy()
    
    if len(last_n) < n:
        logger.info(f"INFO: solo {len(last_n)} sorteos disponibles (solicitados: {n})")
    
    logger.info(f"Seleccionados últimos {len(last_n)} sorteos")
    return last_n

def compute_metrics(df5: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula métricas para los últimos 5 sorteos.
    
    Args:
        df5: DataFrame con últimos 5 sorteos
        
    Returns:
        DataFrame con columnas [numero, freq_abs, ausencia, sefira, score]
    """
    if df5.empty:
        logger.warning("No hay datos para calcular métricas")
        return pd.DataFrame(columns=['numero', 'freq_abs', 'ausencia', 'sefira', 'score'])
    
    # Obtener todos los números únicos
    all_numbers = set()
    for numeros_list in df5['numeros']:
        all_numbers.update(numeros_list)
    
    all_numbers = sorted(list(all_numbers))
    
    # Calcular métricas para cada número
    results = []
    
    for numero in all_numbers:
        # Frecuencia absoluta (apariciones en los 5 sorteos)
        freq_abs = sum(1 for numeros_list in df5['numeros'] if numero in numeros_list)
        
        # Ausencia (sorteos consecutivos sin aparición desde el final)
        ausencia = 0
        for numeros_list in reversed(df5['numeros']):
            if numero not in numeros_list:
                ausencia += 1
            else:
                break
        
        # Mapear a Sefirá
        sefira = map_to_sefira(numero)
        
        # Obtener peso sefirotico
        peso_sefirotico = SEFIROT[sefira].peso_base
        
        # Calcular score: w1*freq_abs - w2*ausencia + w3*peso_sefirotico
        w1, w2, w3 = 1.0, 0.6, 0.4
        score = w1 * freq_abs - w2 * ausencia + w3 * peso_sefirotico
        
        results.append({
            'numero': numero,
            'freq_abs': freq_abs,
            'ausencia': ausencia,
            'sefira': sefira,
            'peso_sefirotico': peso_sefirotico,
            'score': round(score, 4)
        })
    
    metrics_df = pd.DataFrame(results)
    logger.info(f"Métricas calculadas para {len(metrics_df)} números")
    return metrics_df

def rank_numbers(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea ranking de números ordenado por score descendente.
    
    Args:
        metrics_df: DataFrame con métricas
        
    Returns:
        DataFrame con ranking ordenado
    """
    if metrics_df.empty:
        return pd.DataFrame(columns=['rank', 'numero', 'sefira', 'freq_abs', 'ausencia', 'score'])
    
    # Ordenar por score descendente
    ranked_df = metrics_df.sort_values('score', ascending=False).reset_index(drop=True)
    ranked_df['rank'] = range(1, len(ranked_df) + 1)
    
    # Seleccionar columnas de salida
    output_columns = ['rank', 'numero', 'sefira', 'freq_abs', 'ausencia', 'score']
    return ranked_df[output_columns]

def top_numbers(metrics_df: pd.DataFrame, k: int = 10) -> List[int]:
    """
    Retorna top-k números por score.
    
    Args:
        metrics_df: DataFrame con métricas
        k: Número de top números a retornar
        
    Returns:
        Lista de top-k números
    """
    if metrics_df.empty:
        return []
    
    # Ordenar por score descendente y tomar top-k
    top_df = metrics_df.sort_values('score', ascending=False).head(k)
    return top_df['numero'].tolist()

def analyze_last_five(source: Union[str, Path, pd.DataFrame]) -> Dict[str, Any]:
    """
    Función principal que ejecuta el análisis completo de últimos 5 sorteos.
    
    Args:
        source: Fuente de datos (CSV, Path o DataFrame)
        
    Returns:
        Diccionario con resultados del análisis
    """
    try:
        # Cargar datos
        df = load_draws(source)
        
        # Normalizar números
        df_normalized = normalize_numbers(df)
        
        # Seleccionar últimos 5
        df_last5 = select_last_n(df_normalized, n=5)
        
        # Calcular métricas
        metrics = compute_metrics(df_last5)
        
        # Crear ranking
        ranking = rank_numbers(metrics)
        
        # Top números
        top_10 = top_numbers(metrics, k=10)
        
        # Estadísticas resumen
        stats = {
            'sorteos_analizados': len(df_last5),
            'numeros_unicos': len(metrics),
            'frecuencia_promedio': metrics['freq_abs'].mean(),
            'ausencia_promedio': metrics['ausencia'].mean(),
            'score_promedio': metrics['score'].mean(),
            'fecha_inicio': df_last5['fecha'].min() if 'fecha' in df_last5.columns else 'N/A',
            'fecha_fin': df_last5['fecha'].max() if 'fecha' in df_last5.columns else 'N/A'
        }
        
        return {
            'sorteos_data': df_last5,
            'metrics': metrics,
            'ranking': ranking,
            'top_10': top_10,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Error en análisis: {e}")
        return {'error': str(e)}

def save_results(results: Dict[str, Any], output_dir: str = "artifacts") -> None:
    """
    Guarda resultados en archivos CSV.
    
    Args:
        results: Resultados del análisis
        output_dir: Directorio de salida
    """
    try:
        # Crear directorio si no existe
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Guardar métricas
        if 'metrics' in results and not results['metrics'].empty:
            metrics_path = Path(output_dir) / "metrics_last5.csv"
            results['metrics'].to_csv(metrics_path, index=False)
            logger.info(f"Métricas guardadas en: {metrics_path}")
        
        # Guardar ranking
        if 'ranking' in results and not results['ranking'].empty:
            ranking_path = Path(output_dir) / "ranking_last5.csv"
            results['ranking'].to_csv(ranking_path, index=False)
            logger.info(f"Ranking guardado en: {ranking_path}")
        
        # Guardar datos de sorteos
        if 'sorteos_data' in results and not results['sorteos_data'].empty:
            sorteos_path = Path(output_dir) / "sorteos_last5.csv"
            results['sorteos_data'].to_csv(sorteos_path, index=False)
            logger.info(f"Datos de sorteos guardados en: {sorteos_path}")
            
    except Exception as e:
        logger.error(f"Error guardando resultados: {e}")

# =================== PRUEBAS RÁPIDAS ===================

def test_basic_functionality():
    """Prueba básica con 5 sorteos sintéticos."""
    print("🧪 Prueba básica con 5 sorteos sintéticos")
    
    # Crear datos de prueba
    test_data = pd.DataFrame({
        'sorteo_id': [1, 2, 3, 4, 5],
        'fecha': ['2024-01-01', '2024-01-08', '2024-01-15', '2024-01-22', '2024-01-29'],
        'numeros': [
            [7, 14, 21, 28, 35],
            [3, 12, 23, 34, 45],
            [1, 11, 22, 33, 44],
            [5, 15, 25, 35, 45],
            [2, 13, 24, 35, 46]
        ]
    })
    
    # Ejecutar análisis
    results = analyze_last_five(test_data)
    
    if 'error' not in results:
        print(f"✅ Análisis exitoso: {results['stats']['sorteos_analizados']} sorteos")
        print(f"📊 Números únicos: {results['stats']['numeros_unicos']}")
        print(f"🏆 Top 5: {results['top_10'][:5]}")
    else:
        print(f"❌ Error: {results['error']}")

def test_string_numbers():
    """Prueba con números en formato string."""
    print("\n🧪 Prueba con números en string")
    
    test_data = pd.DataFrame({
        'sorteo_id': [1, 2, 3],
        'fecha': ['2024-01-01', '2024-01-08', '2024-01-15'],
        'numeros': [
            "7, 14, 21, 28, 35",
            "3; 12; 23; 34; 45",
            "1 11 22 33 44"
        ]
    })
    
    results = analyze_last_five(test_data)
    
    if 'error' not in results:
        print(f"✅ Análisis exitoso: {results['stats']['sorteos_analizados']} sorteos")
        print(f"📊 Números únicos: {results['stats']['numeros_unicos']}")
    else:
        print(f"❌ Error: {results['error']}")

def test_less_than_five():
    """Prueba con menos de 5 sorteos."""
    print("\n🧪 Prueba con menos de 5 sorteos")
    
    test_data = pd.DataFrame({
        'sorteo_id': [1, 2],
        'fecha': ['2024-01-01', '2024-01-08'],
        'numeros': [
            [7, 14, 21, 28, 35],
            [3, 12, 23, 34, 45]
        ]
    })
    
    results = analyze_last_five(test_data)
    
    if 'error' not in results:
        print(f"✅ Análisis exitoso: {results['stats']['sorteos_analizados']} sorteos")
        print(f"📊 Números únicos: {results['stats']['numeros_unicos']}")
    else:
        print(f"❌ Error: {results['error']}")

# =================== EJECUCIÓN PRINCIPAL ===================

if __name__ == "__main__":
    print("🔮 SEFIROT FIVE - Análisis de Últimos 5 Sorteos")
    print("=" * 60)
    
    # Ejecutar pruebas
    test_basic_functionality()
    test_string_numbers()
    test_less_than_five()
    
    print("\n" + "=" * 60)
    print("🚀 Análisis principal con datos reales/sintéticos")
    
    # Intentar cargar datos reales
    data_source = "data/sorteos.csv"
    
    if not Path(data_source).exists():
        print(f"📁 Archivo {data_source} no encontrado. Generando datos sintéticos.")
        data_source = None  # Esto activará la generación sintética
    
    # Ejecutar análisis principal
    results = analyze_last_five(data_source)
    
    if 'error' not in results:
        stats = results['stats']
        print(f"\n📊 VENTANA ANALIZADA: últimos {stats['sorteos_analizados']} sorteos")
        print(f"📅 Período: {stats['fecha_inicio']} a {stats['fecha_fin']}")
        print(f"🔢 Números únicos analizados: {stats['numeros_unicos']}")
        
        # Mostrar top 10
        print(f"\n🏆 TOP 10 NÚMEROS:")
        print("Rank | Número | Sefirá | Score | Frec | Ausencia")
        print("-" * 50)
        
        top_10_df = results['ranking'].head(10)
        for _, row in top_10_df.iterrows():
            sefira_name = SEFIROT[row['sefira']].nombre
            print(f"{row['rank']:4d} | {row['numero']:6d} | {sefira_name:8s} | {row['score']:5.2f} | {row['freq_abs']:4d} | {row['ausencia']:8d}")
        
        # Guardar resultados
        save_results(results)
        print(f"\n💾 Resultados guardados en directorio 'artifacts/'")
        
    else:
        print(f"❌ Error en análisis: {results['error']}")
    
    print("\n✅ Análisis completado")






