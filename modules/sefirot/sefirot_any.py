# modules/sefirot/sefirot_any.py
"""
Sefirot Any - Análisis Sefirotico Universal para Cualquier Lotería
Módulo que aplica análisis sefirotico mediante perfiles de sorteo configurables
Soporte para Bolita Cubana con valor cero y múltiples pools
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
import logging
from datetime import datetime, timedelta

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================== DEFINICIONES SEFIROTICAS EMBEBIDAS ===================

def map_to_sefira(n: int) -> int:
    """
    Mapea un número a su Sefirá correspondiente.
    
    Regla:
    - Si n == 0: return 10 (Malkut)
    - Si n < 0: ValueError
    - Si n > 0: s = n % 10; return 10 si s==0; en otro caso s
    
    Args:
        n: Número a mapear
        
    Returns:
        Número de Sefirá (1-10)
        
    Raises:
        ValueError: Si n < 0
    """
    if n == 0:
        return 10  # Malkut
    elif n < 0:
        raise ValueError(f"Número negativo no válido: {n}")
    else:
        s = n % 10
        return 10 if s == 0 else s

# Pesos por Sefirá (prioriza Pilar Central)
SEFIROT_WEIGHTS = {
    1: 1.08,  # Keter (Pilar Central)
    2: 1.02,  # Chokmah (Central)
    3: 0.97,  # Binah (Izquierda)
    4: 1.01,  # Chesed (Derecha)
    5: 0.98,  # Gevurah (Izquierda)
    6: 1.06,  # Tiferet (Central)
    7: 1.02,  # Netzach (Derecha)
    8: 0.99,  # Hod (Izquierda)
    9: 1.07,  # Yesod (Central)
    10: 0.96  # Malkut (manifestación)
}

# Coeficientes globales del score
W_FREQ = 1.00
W_ABS = 0.60
W_SEF = 0.40

# =================== PERFILES EMBEBIDOS ===================

BUILTIN_PROFILES = {
    "powerball": {
        "id": "powerball",
        "name": "Powerball",
        "allow_zero": False,
        "pools": [
            {"key": "main", "label": "Blancos", "min": 1, "max": 69, "count": 5, "unique": True},
            {"key": "bonus", "label": "Powerball", "min": 1, "max": 26, "count": 1, "unique": True}
        ]
    },
    "florida_pick3": {
        "id": "florida_pick3",
        "name": "Florida Pick 3",
        "allow_zero": True,
        "pools": [
            {"key": "main", "label": "Números", "min": 0, "max": 9, "count": 3, "unique": False}
        ]
    },
    "mega_millions": {
        "id": "mega_millions",
        "name": "Mega Millions",
        "allow_zero": False,
        "pools": [
            {"key": "main", "label": "Blancos", "min": 1, "max": 70, "count": 5, "unique": True},
            {"key": "bonus", "label": "Mega Ball", "min": 1, "max": 25, "count": 1, "unique": True}
        ]
    },
    "euromillions": {
        "id": "euromillions",
        "name": "EuroMillions",
        "allow_zero": False,
        "pools": [
            {"key": "main", "label": "Blancos", "min": 1, "max": 50, "count": 5, "unique": True},
            {"key": "bonus", "label": "Estrellas", "min": 1, "max": 12, "count": 2, "unique": True}
        ]
    },
    "la_primitiva": {
        "id": "la_primitiva",
        "name": "La Primitiva",
        "allow_zero": False,
        "pools": [
            {"key": "main", "label": "Blancos", "min": 1, "max": 49, "count": 6, "unique": True},
            {"key": "bonus", "label": "Reintegro", "min": 0, "max": 9, "count": 1, "unique": True}
        ]
    },
    "bolita_cuba_2d": {
        "id": "bolita_cuba_2d",
        "name": "Bolita Cubana (2 dígitos)",
        "allow_zero": True,
        "pools": [
            {"key": "main", "label": "2D", "min": 0, "max": 99, "count": 1, "unique": True}
        ]
    },
    "bolita_cuba_3d": {
        "id": "bolita_cuba_3d",
        "name": "Bolita Cubana (3 dígitos)",
        "allow_zero": True,
        "pools": [
            {"key": "main", "label": "3D", "min": 0, "max": 999, "count": 1, "unique": True}
        ]
    }
}

# =================== CLASE PRINCIPAL ===================

class SefirotAny:
    """
    Analizador sefirotico universal para cualquier lotería mediante perfiles configurables.
    """
    
    def __init__(self, data_source: Union[str, Path, pd.DataFrame], 
                 profile: Union[Dict[str, Any], str], last_n: int = 5):
        """
        Inicializa el analizador sefirotico.
        
        Args:
            data_source: Ruta CSV, Path o DataFrame
            profile: Dict de perfil o string en BUILTIN_PROFILES
            last_n: Ventana de sorteos (default: 5)
        """
        self.data_source = data_source
        self.last_n = last_n
        
        # Resolver perfil
        if isinstance(profile, str):
            if profile in BUILTIN_PROFILES:
                self.profile = BUILTIN_PROFILES[profile]
            else:
                raise ValueError(f"Perfil '{profile}' no encontrado en BUILTIN_PROFILES")
        else:
            self.profile = profile
        
        self.allow_zero = self.profile.get("allow_zero", False)
        logger.info(f"Analizador inicializado - Perfil: {self.profile['name']}, Ventana: {last_n}")
    
    def load_draws(self) -> pd.DataFrame:
        """
        Carga y valida datos de sorteos.
        
        Returns:
            DataFrame con columnas normalizadas
        """
        try:
            if isinstance(self.data_source, pd.DataFrame):
                df = self.data_source.copy()
                logger.info("Usando DataFrame proporcionado")
            elif isinstance(self.data_source, (str, Path)):
                source_path = Path(self.data_source)
                if source_path.exists():
                    df = pd.read_csv(source_path)
                    logger.info(f"Datos cargados desde: {source_path}")
                else:
                    logger.warning(f"Archivo no encontrado: {source_path}. Generando datos sintéticos.")
                    df = self._generate_synthetic_data()
            else:
                raise ValueError(f"Tipo de fuente no soportado: {type(self.data_source)}")
            
            # Validar columnas requeridas
            required_columns = ["lottery_id", "sorteo_id", "fecha"]
            pool_columns = [f"nums_{pool['key']}" for pool in self.profile["pools"]]
            all_required = required_columns + pool_columns
            
            missing_columns = [col for col in all_required if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Columnas faltantes: {missing_columns}. Generando datos sintéticos.")
                df = self._generate_synthetic_data()
            
            # Normalizar pools
            df = self._normalize_pools(df)
            
            logger.info(f"Dataset cargado: {len(df)} sorteos")
            return df
            
        except Exception as e:
            logger.error(f"Error cargando datos: {e}. Generando datos sintéticos.")
            return self._generate_synthetic_data()
    
    def _generate_synthetic_data(self) -> pd.DataFrame:
        """Genera dataset sintético coherente con el perfil."""
        np.random.seed(42)
        
        sorteos = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(5):
            sorteo = {
                'lottery_id': self.profile['id'],
                'sorteo_id': i + 1,
                'fecha': (base_date + timedelta(days=i*7)).strftime('%Y-%m-%d')
            }
            
            # Generar números para cada pool
            for pool in self.profile["pools"]:
                key = pool["key"]
                min_val = pool["min"]
                max_val = pool["max"]
                count = pool["count"]
                unique = pool["unique"]
                
                if unique and count > 1:
                    # Múltiples números únicos
                    numbers = sorted(np.random.choice(range(min_val, max_val + 1), 
                                                    size=count, replace=False))
                else:
                    # Un solo número o no únicos
                    numbers = [np.random.randint(min_val, max_val + 1) for _ in range(count)]
                
                sorteo[f"nums_{key}"] = numbers
            
            sorteos.append(sorteo)
        
        df = pd.DataFrame(sorteos)
        logger.info(f"Dataset sintético generado para perfil: {self.profile['name']}")
        return df
    
    def _normalize_pools(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza todos los pools definidos en el perfil."""
        df = df.copy()
        
        for pool in self.profile["pools"]:
            key = pool["key"]
            column = f"nums_{key}"
            
            if column in df.columns:
                df[column] = df[column].apply(
                    lambda x: self._normalize_pool_numbers(x, pool)
                )
        
        return df
    
    def _normalize_pool_numbers(self, numbers: Any, pool: Dict[str, Any]) -> List[int]:
        """Normaliza números de un pool específico."""
        min_val = pool["min"]
        max_val = pool["max"]
        count = pool["count"]
        unique = pool["unique"]
        
        # Convertir a lista de enteros
        if isinstance(numbers, list):
            try:
                normalized = [int(x) for x in numbers if str(x).strip()]
            except ValueError:
                normalized = []
        elif isinstance(numbers, str):
            if not numbers.strip():
                normalized = []
            else:
                # Separar por comas, espacios, etc.
                parts = numbers.replace(',', ' ').replace(';', ' ').replace('|', ' ').split()
                try:
                    normalized = [int(x.strip()) for x in parts if x.strip()]
                except ValueError:
                    normalized = []
        else:
            normalized = []
        
        # Validar rango
        valid_numbers = []
        for num in normalized:
            if min_val <= num <= max_val:
                valid_numbers.append(num)
            else:
                logger.warning(f"Número {num} fuera de rango [{min_val}, {max_val}] - excluido")
        
        # Aplicar restricciones del pool
        if unique:
            valid_numbers = list(dict.fromkeys(valid_numbers))  # Mantener orden, eliminar duplicados
        
        # Recortar a count si es necesario
        if len(valid_numbers) > count:
            logger.warning(f"Pool {pool['key']}: {len(valid_numbers)} números, recortando a {count}")
            valid_numbers = valid_numbers[:count]
        
        return valid_numbers
    
    def select_last_n(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Selecciona los últimos N sorteos.
        
        Args:
            df: DataFrame con sorteos
            
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
        last_n = df_sorted.tail(self.last_n).copy()
        
        if len(last_n) < self.last_n:
            logger.info(f"INFO: solo {len(last_n)} sorteos disponibles (solicitados: {self.last_n})")
        
        logger.info(f"Seleccionados últimos {len(last_n)} sorteos")
        return last_n
    
    def compute_pool_metrics(self, df_n: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calcula métricas para cada pool.
        
        Args:
            df_n: DataFrame con últimos N sorteos
            
        Returns:
            Dict con métricas por pool
        """
        results = {}
        
        for pool in self.profile["pools"]:
            key = pool["key"]
            column = f"nums_{key}"
            
            if column not in df_n.columns:
                logger.warning(f"Columna {column} no encontrada - saltando pool {key}")
                continue
            
            # Obtener todos los números únicos del pool
            all_numbers = set()
            for numbers_list in df_n[column]:
                all_numbers.update(numbers_list)
            
            all_numbers = sorted(list(all_numbers))
            
            # Calcular métricas para cada número
            pool_results = []
            
            for numero in all_numbers:
                # Frecuencia absoluta
                freq_abs = sum(1 for numbers_list in df_n[column] if numero in numbers_list)
                
                # Ausencia
                ausencia = self.last_n - freq_abs
                
                # Mapear a Sefirá
                sefira = map_to_sefira(numero)
                peso_sefira = SEFIROT_WEIGHTS[sefira]
                
                # Calcular score
                score = W_FREQ * freq_abs - W_ABS * ausencia + W_SEF * peso_sefira
                
                pool_results.append({
                    'numero': numero,
                    'sefira': sefira,
                    'freq_abs': freq_abs,
                    'ausencia': ausencia,
                    'peso_sefira': peso_sefira,
                    'score': round(score, 4)
                })
            
            results[key] = pd.DataFrame(pool_results)
            logger.info(f"Métricas calculadas para pool {key}: {len(pool_results)} números")
        
        return results
    
    def rank_pool(self, pool_df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea ranking de un pool ordenado por score descendente.
        
        Args:
            pool_df: DataFrame con métricas del pool
            
        Returns:
            DataFrame con ranking ordenado
        """
        if pool_df.empty:
            return pd.DataFrame(columns=['rank', 'numero', 'sefira', 'freq_abs', 'ausencia', 'score'])
        
        # Ordenar por score descendente
        ranked_df = pool_df.sort_values('score', ascending=False).reset_index(drop=True)
        ranked_df['rank'] = range(1, len(ranked_df) + 1)
        
        # Seleccionar columnas de salida
        output_columns = ['rank', 'numero', 'sefira', 'freq_abs', 'ausencia', 'score']
        return ranked_df[output_columns]
    
    def combine_rankings(self, pool_results: Dict[str, pd.DataFrame], 
                        weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
        """
        Combina rankings de pools en un ranking global.
        
        Args:
            pool_results: Dict con rankings por pool
            weights: Pesos por pool (default: main=1.0, bonus=0.6, otros=0.8)
            
        Returns:
            DataFrame con ranking global combinado
        """
        if not pool_results:
            return pd.DataFrame()
        
        # Pesos por defecto
        if weights is None:
            weights = {}
            for pool in self.profile["pools"]:
                key = pool["key"]
                if key == "main":
                    weights[key] = 1.0
                elif key == "bonus":
                    weights[key] = 0.6
                else:
                    weights[key] = 0.8
        
        # Normalizar scores por pool y combinar
        combined_data = []
        
        for pool_key, pool_df in pool_results.items():
            if pool_df.empty:
                continue
            
            # Normalizar score a [0,1] usando min-max
            min_score = pool_df['score'].min()
            max_score = pool_df['score'].max()
            
            if max_score > min_score:
                pool_df['score_norm'] = (pool_df['score'] - min_score) / (max_score - min_score)
            else:
                pool_df['score_norm'] = 0.5  # Score constante
            
            # Aplicar peso del pool
            pool_weight = weights.get(pool_key, 0.8)
            pool_df['score_global'] = pool_df['score_norm'] * pool_weight
            pool_df['pool'] = pool_key
            pool_df['rank_pool'] = pool_df['rank']
            
            # Seleccionar columnas para combinación
            combined_data.append(pool_df[['numero', 'pool', 'score_norm', 'rank_pool', 'score_global']])
        
        if not combined_data:
            return pd.DataFrame()
        
        # Combinar todos los pools
        combined_df = pd.concat(combined_data, ignore_index=True)
        
        # Ordenar por score global descendente
        combined_df = combined_df.sort_values('score_global', ascending=False).reset_index(drop=True)
        combined_df['rank_global'] = range(1, len(combined_df) + 1)
        
        return combined_df
    
    def top_numbers(self, combined_df: pd.DataFrame, k: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna top-k números globales.
        
        Args:
            combined_df: DataFrame con ranking global
            k: Número de top números
            
        Returns:
            Lista con top-k números y sus métricas
        """
        if combined_df.empty:
            return []
        
        top_df = combined_df.head(k)
        
        return [
            {
                'numero': row['numero'],
                'pool': row['pool'],
                'score_global': row['score_global'],
                'rank_pool': row['rank_pool'],
                'rank_global': row['rank_global']
            }
            for _, row in top_df.iterrows()
        ]
    
    def export_csvs(self, per_pool: Dict[str, pd.DataFrame], 
                   combined: pd.DataFrame) -> None:
        """
        Exporta resultados a archivos CSV.
        
        Args:
            per_pool: Dict con rankings por pool
            combined: DataFrame con ranking global
        """
        try:
            # Crear directorio artifacts
            artifacts_dir = Path("artifacts")
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            
            profile_id = self.profile['id']
            last_n = self.last_n
            
            # Exportar por pool
            for pool_key, pool_df in per_pool.items():
                if not pool_df.empty:
                    # Métricas del pool
                    metrics_path = artifacts_dir / f"metrics_{profile_id}_last{last_n}_{pool_key}.csv"
                    pool_df.to_csv(metrics_path, index=False)
                    logger.info(f"Métricas {pool_key} guardadas en: {metrics_path}")
                    
                    # Ranking del pool
                    ranking_path = artifacts_dir / f"ranking_{profile_id}_last{last_n}_{pool_key}.csv"
                    pool_df.to_csv(ranking_path, index=False)
                    logger.info(f"Ranking {pool_key} guardado en: {ranking_path}")
            
            # Exportar ranking global
            if not combined.empty:
                combined_path = artifacts_dir / f"combined_{profile_id}_last{last_n}.csv"
                combined.to_csv(combined_path, index=False)
                logger.info(f"Ranking global guardado en: {combined_path}")
            
        except Exception as e:
            logger.error(f"Error exportando CSV: {e}")

# =================== BLOQUE EJECUTABLE ===================

if __name__ == "__main__":
    print("🔮 SEFIROT ANY - Análisis Sefirotico Universal")
    print("=" * 60)
    
    # Lista de perfiles para demostrar
    profiles_to_test = [
        "powerball",
        "mega_millions", 
        "euromillions",
        "bolita_cuba_2d",
        "bolita_cuba_3d"
    ]
    
    for profile_id in profiles_to_test:
        print(f"\n🎯 PERFIL: {profile_id}")
        print("-" * 40)
        
        try:
            # Crear analizador
            analyzer = SefirotAny("data/sorteos.csv", profile=profile_id, last_n=5)
            
            # Ejecutar pipeline completo
            df = analyzer.load_draws()
            df5 = analyzer.select_last_n(df)
            per_pool = analyzer.compute_pool_metrics(df5)
            ranked = {k: analyzer.rank_pool(v) for k, v in per_pool.items()}
            combined = analyzer.combine_rankings(ranked)
            
            # Exportar resultados
            analyzer.export_csvs(per_pool=ranked, combined=combined)
            
            # Mostrar resumen
            stats = {
                'sorteos_analizados': len(df5),
                'pools_activos': len(per_pool),
                'numeros_totales': sum(len(pool_df) for pool_df in per_pool.values())
            }
            
            print(f"📊 Ventana analizada: últimos {stats['sorteos_analizados']} sorteos")
            print(f"🔢 Pools activos: {stats['pools_activos']}")
            print(f"📈 Números totales analizados: {stats['numeros_totales']}")
            
            # Top 10 global
            if not combined.empty:
                print(f"\n🏆 TOP 10 GLOBAL:")
                print("Rank | Número | Pool | Score Global | Rank Pool")
                print("-" * 50)
                
                top_10 = combined.head(10)
                for _, row in top_10.iterrows():
                    print(f"{row['rank_global']:4d} | {row['numero']:6d} | {row['pool']:8s} | {row['score_global']:11.4f} | {row['rank_pool']:9d}")
            
            # Top 5 por pool
            for pool_key, pool_df in ranked.items():
                if not pool_df.empty:
                    print(f"\n📊 TOP 5 - {pool_key.upper()}:")
                    print("Rank | Número | Sefirá | Score | Frec | Ausencia")
                    print("-" * 50)
                    
                    top_5 = pool_df.head(5)
                    for _, row in top_5.iterrows():
                        sefira_name = f"Sefirá {row['sefira']}"
                        print(f"{row['rank']:4d} | {row['numero']:6d} | {sefira_name:8s} | {row['score']:5.2f} | {row['freq_abs']:4d} | {row['ausencia']:8d}")
            
        except Exception as e:
            print(f"❌ Error procesando perfil {profile_id}: {e}")
            continue
    
    print(f"\n✅ Análisis completado para {len(profiles_to_test)} perfiles")
    print("💾 Resultados guardados en directorio 'artifacts/'")

