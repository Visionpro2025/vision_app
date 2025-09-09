# modules/sefirot/sefirot_analyzer.py
"""
Sefirot Analyzer - Análisis de Sorteos de Lotería con Kabbalah Numérica
Módulo para App.Vision que aplica el modelo de Sefirot para analizar patrones en sorteos
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SefirotAnalyzer:
    """
    Analizador de sorteos de lotería basado en el modelo de Sefirot de la Kabbalah.
    
    Mapea números de lotería a las 10 Sefirot del Árbol de la Vida y calcula
    métricas de frecuencia, ausencia y energía sefirotica para identificar patrones.
    """
    
    def __init__(self, data_source: Union[str, Path, pd.DataFrame]):
        """
        Inicializa el analizador de Sefirot.
        
        Args:
            data_source: Ruta al archivo CSV, DataFrame o conexión a base de datos
        """
        self.data_source = data_source
        self.sorteos_data = None
        self.analysis_results = None
        
        # Definición de las 10 Sefirot del Árbol de la Vida
        self.sefirot_mapping = {
            1: {
                'name': 'Keter',
                'meaning': 'Corona',
                'energy': 'Divina',
                'position': 'Superior',
                'weight': 10
            },
            2: {
                'name': 'Chokmah',
                'meaning': 'Sabiduría',
                'energy': 'Masculina',
                'position': 'Superior',
                'weight': 9
            },
            3: {
                'name': 'Binah',
                'meaning': 'Entendimiento',
                'energy': 'Femenina',
                'position': 'Superior',
                'weight': 8
            },
            4: {
                'name': 'Chesed',
                'meaning': 'Misericordia',
                'energy': 'Expansiva',
                'position': 'Medio',
                'weight': 7
            },
            5: {
                'name': 'Gevurah',
                'meaning': 'Fuerza',
                'energy': 'Restrictiva',
                'position': 'Medio',
                'weight': 6
            },
            6: {
                'name': 'Tiferet',
                'meaning': 'Belleza',
                'energy': 'Equilibrada',
                'position': 'Medio',
                'weight': 5
            },
            7: {
                'name': 'Netzach',
                'meaning': 'Victoria',
                'energy': 'Activa',
                'position': 'Inferior',
                'weight': 4
            },
            8: {
                'name': 'Hod',
                'meaning': 'Gloria',
                'energy': 'Receptiva',
                'position': 'Inferior',
                'weight': 3
            },
            9: {
                'name': 'Yesod',
                'meaning': 'Fundación',
                'energy': 'Estabilizadora',
                'position': 'Inferior',
                'weight': 2
            },
            10: {
                'name': 'Malkuth',
                'meaning': 'Reino',
                'energy': 'Manifestada',
                'position': 'Inferior',
                'weight': 1
            }
        }
        
        # Cargar datos
        self._load_data()
        
        logger.info("🔮 SefirotAnalyzer inicializado correctamente")
    
    def _load_data(self):
        """Carga los datos de sorteos desde la fuente especificada."""
        try:
            if isinstance(self.data_source, pd.DataFrame):
                self.sorteos_data = self.data_source.copy()
            elif isinstance(self.data_source, (str, Path)):
                # Intentar cargar como CSV
                self.sorteos_data = pd.read_csv(self.data_source)
            else:
                raise ValueError("Fuente de datos no soportada")
            
            # Validar estructura de datos
            required_columns = ['fecha', 'numeros']
            if not all(col in self.sorteos_data.columns for col in required_columns):
                # Si no tiene la estructura esperada, crear datos de ejemplo
                self._create_sample_data()
            
            logger.info(f"✅ Datos cargados: {len(self.sorteos_data)} sorteos")
            
        except Exception as e:
            logger.warning(f"⚠️ Error cargando datos: {e}. Creando datos de ejemplo.")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Crea datos de ejemplo para demostración."""
        np.random.seed(42)  # Para reproducibilidad
        
        # Generar 20 sorteos de ejemplo
        fechas = pd.date_range(start='2024-01-01', periods=20, freq='3D')
        sorteos = []
        
        for i, fecha in enumerate(fechas):
            # Generar 5 números aleatorios entre 1 y 100
            numeros = sorted(np.random.choice(range(1, 101), size=5, replace=False))
            sorteos.append({
                'fecha': fecha,
                'numeros': numeros,
                'sorteo_id': i + 1
            })
        
        self.sorteos_data = pd.DataFrame(sorteos)
        logger.info("📊 Datos de ejemplo creados")
    
    def map_to_sefira(self, number: int) -> Dict:
        """
        Mapea un número a su Sefirá correspondiente.
        
        Args:
            number: Número a mapear (1-100)
            
        Returns:
            Diccionario con información de la Sefirá
        """
        # Mapeo circular: número % 10 + 1 para obtener Sefirá (1-10)
        sefira_number = ((number - 1) % 10) + 1
        sefira_info = self.sefirot_mapping[sefira_number].copy()
        sefira_info['sefira_number'] = sefira_number
        sefira_info['original_number'] = number
        
        return sefira_info
    
    def analyze(self, last_n: int = 5) -> Dict:
        """
        Aplica el análisis completo de Sefirot sobre los últimos N sorteos.
        
        Args:
            last_n: Número de sorteos recientes a analizar
            
        Returns:
            Diccionario con resultados del análisis
        """
        try:
            logger.info(f"🔍 Iniciando análisis de últimos {last_n} sorteos")
            
            # Obtener últimos N sorteos
            recent_sorteos = self.sorteos_data.tail(last_n).copy()
            
            # Extraer todos los números únicos
            all_numbers = set()
            for numeros in recent_sorteos['numeros']:
                all_numbers.update(numeros)
            
            all_numbers = sorted(list(all_numbers))
            
            # Calcular métricas para cada número
            analysis_results = []
            
            for numero in all_numbers:
                # Mapear a Sefirá
                sefira_info = self.map_to_sefira(numero)
                
                # Calcular frecuencia absoluta
                freq_abs = self._calculate_frequency(numero, recent_sorteos)
                
                # Calcular ausencia (sorteos sin aparición)
                ausencia = self._calculate_absence(numero, recent_sorteos)
                
                # Calcular score ponderado
                score = self._calculate_weighted_score(
                    freq_abs, ausencia, sefira_info['weight']
                )
                
                analysis_results.append({
                    'numero': numero,
                    'sefira_number': sefira_info['sefira_number'],
                    'sefira_name': sefira_info['name'],
                    'sefira_meaning': sefira_info['meaning'],
                    'sefira_energy': sefira_info['energy'],
                    'sefira_position': sefira_info['position'],
                    'sefira_weight': sefira_info['weight'],
                    'freq_abs': freq_abs,
                    'ausencia': ausencia,
                    'score': score
                })
            
            # Crear DataFrame con resultados
            self.analysis_results = pd.DataFrame(analysis_results)
            
            # Identificar números críticos
            critical_numbers = self._identify_critical_numbers()
            
            # Generar ranking
            ranking = self.get_ranking()
            
            results = {
                'analysis_date': datetime.now().isoformat(),
                'sorteos_analyzed': len(recent_sorteos),
                'numbers_analyzed': len(all_numbers),
                'critical_numbers': critical_numbers,
                'ranking': ranking.to_dict('records'),
                'summary_stats': self._generate_summary_stats()
            }
            
            logger.info(f"✅ Análisis completado: {len(all_numbers)} números analizados")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}")
            return {'error': str(e)}
    
    def _calculate_frequency(self, number: int, sorteos: pd.DataFrame) -> int:
        """Calcula la frecuencia absoluta de un número en los sorteos."""
        count = 0
        for numeros in sorteos['numeros']:
            if number in numeros:
                count += 1
        return count
    
    def _calculate_absence(self, number: int, sorteos: pd.DataFrame) -> int:
        """Calcula cuántos sorteos pasaron sin que aparezca el número."""
        absence_count = 0
        for i, numeros in enumerate(sorteos['numeros']):
            if number not in numeros:
                absence_count += 1
            else:
                break  # Reset al encontrar el número
        return absence_count
    
    def _calculate_weighted_score(self, freq: int, absence: int, sefira_weight: int) -> float:
        """
        Calcula el score ponderado basado en frecuencia, ausencia y peso sefirotico.
        
        Fórmula: (freq * 0.4) + (absence * 0.3) + (sefira_weight * 0.3)
        """
        return (freq * 0.4) + (absence * 0.3) + (sefira_weight * 0.3)
    
    def _identify_critical_numbers(self) -> List[Dict]:
        """Identifica números críticos con alta ausencia pero alta energía sefirotica."""
        if self.analysis_results is None:
            return []
        
        # Filtrar números con alta ausencia (>= 3) y alta energía sefirotica (weight >= 7)
        critical = self.analysis_results[
            (self.analysis_results['ausencia'] >= 3) & 
            (self.analysis_results['sefira_weight'] >= 7)
        ].copy()
        
        # Ordenar por score descendente
        critical = critical.sort_values('score', ascending=False)
        
        return critical.to_dict('records')
    
    def get_ranking(self) -> pd.DataFrame:
        """
        Devuelve un DataFrame con el ranking de números por score.
        
        Returns:
            DataFrame con columnas [numero, sefira, freq_abs, ausencia, score]
        """
        if self.analysis_results is None:
            return pd.DataFrame()
        
        ranking = self.analysis_results.copy()
        ranking = ranking.sort_values('score', ascending=False)
        ranking = ranking.reset_index(drop=True)
        ranking['rank'] = range(1, len(ranking) + 1)
        
        return ranking[['rank', 'numero', 'sefira_name', 'freq_abs', 'ausencia', 'score']]
    
    def _generate_summary_stats(self) -> Dict:
        """Genera estadísticas resumen del análisis."""
        if self.analysis_results is None:
            return {}
        
        return {
            'total_numbers': len(self.analysis_results),
            'avg_frequency': self.analysis_results['freq_abs'].mean(),
            'max_frequency': self.analysis_results['freq_abs'].max(),
            'avg_absence': self.analysis_results['ausencia'].mean(),
            'max_absence': self.analysis_results['ausencia'].max(),
            'avg_score': self.analysis_results['score'].mean(),
            'max_score': self.analysis_results['score'].max(),
            'sefirot_distribution': self.analysis_results['sefira_name'].value_counts().to_dict()
        }
    
    def export_json(self, path: str) -> bool:
        """
        Exporta los resultados del análisis en formato JSON.
        
        Args:
            path: Ruta donde guardar el archivo JSON
            
        Returns:
            True si la exportación fue exitosa, False en caso contrario
        """
        try:
            if self.analysis_results is None:
                logger.warning("⚠️ No hay resultados para exportar")
                return False
            
            export_data = {
                'analysis_results': self.analysis_results.to_dict('records'),
                'ranking': self.get_ranking().to_dict('records'),
                'critical_numbers': self._identify_critical_numbers(),
                'summary_stats': self._generate_summary_stats(),
                'export_date': datetime.now().isoformat()
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Resultados exportados a: {path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exportando JSON: {e}")
            return False
    
    def get_sefirot_info(self, sefira_number: int) -> Dict:
        """
        Obtiene información detallada de una Sefirá específica.
        
        Args:
            sefira_number: Número de la Sefirá (1-10)
            
        Returns:
            Diccionario con información de la Sefirá
        """
        if sefira_number not in self.sefirot_mapping:
            raise ValueError(f"Sefirá {sefira_number} no existe. Debe estar entre 1-10")
        
        return self.sefirot_mapping[sefira_number].copy()
    
    def get_numbers_by_sefira(self, sefira_number: int) -> List[int]:
        """
        Obtiene todos los números que pertenecen a una Sefirá específica.
        
        Args:
            sefira_number: Número de la Sefirá (1-10)
            
        Returns:
            Lista de números que pertenecen a esa Sefirá
        """
        numbers = []
        for num in range(1, 101):
            if self.map_to_sefira(num)['sefira_number'] == sefira_number:
                numbers.append(num)
        return numbers


# =================== EJEMPLOS DE USO ===================

def ejemplo_uso_basico():
    """Ejemplo básico de uso del SefirotAnalyzer."""
    print("🔮 Ejemplo de uso básico del SefirotAnalyzer")
    print("=" * 50)
    
    # Crear instancia con datos de ejemplo
    analyzer = SefirotAnalyzer("datos_ejemplo.csv")
    
    # Realizar análisis de últimos 5 sorteos
    resultados = analyzer.analyze(last_n=5)
    
    # Mostrar ranking
    ranking = analyzer.get_ranking()
    print("\n📊 TOP 10 NÚMEROS POR SCORE:")
    print(ranking.head(10).to_string(index=False))
    
    # Mostrar números críticos
    print(f"\n⚠️ NÚMEROS CRÍTICOS: {len(resultados['critical_numbers'])}")
    for num in resultados['critical_numbers'][:5]:
        print(f"  - Número {num['numero']} ({num['sefira_name']}): Score {num['score']:.2f}")
    
    # Exportar resultados
    analyzer.export_json("resultados_sefirot.json")
    print("\n✅ Resultados exportados a resultados_sefirot.json")

def ejemplo_analisis_avanzado():
    """Ejemplo avanzado con análisis personalizado."""
    print("\n🔮 Ejemplo de análisis avanzado")
    print("=" * 50)
    
    # Crear DataFrame personalizado
    datos_personalizados = pd.DataFrame({
        'fecha': pd.date_range('2024-01-01', periods=10, freq='7D'),
        'numeros': [
            [7, 14, 21, 28, 35],
            [3, 12, 23, 34, 45],
            [1, 11, 22, 33, 44],
            [5, 15, 25, 35, 45],
            [2, 13, 24, 35, 46],
            [8, 18, 28, 38, 48],
            [4, 14, 24, 34, 44],
            [6, 16, 26, 36, 46],
            [9, 19, 29, 39, 49],
            [10, 20, 30, 40, 50]
        ]
    })
    
    # Crear analizador con datos personalizados
    analyzer = SefirotAnalyzer(datos_personalizados)
    
    # Análisis completo
    resultados = analyzer.analyze(last_n=10)
    
    # Información de Sefirot específica
    print(f"\n🔮 INFORMACIÓN SEFIROT:")
    for i in range(1, 11):
        info = analyzer.get_sefirot_info(i)
        print(f"  {i}. {info['name']} ({info['meaning']}) - {info['energy']}")
    
    # Números por Sefirá
    print(f"\n📊 DISTRIBUCIÓN POR SEFIROT:")
    for i in range(1, 11):
        numeros = analyzer.get_numbers_by_sefira(i)
        print(f"  Sefirá {i}: {len(numeros)} números ({min(numeros)}-{max(numeros)})")

if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_uso_basico()
    ejemplo_analisis_avanzado()





