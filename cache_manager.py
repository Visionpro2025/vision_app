#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CACHE MANAGER - Sistema de caché inteligente para VISION PREMIUM
Maneja caché de análisis de IA, resultados de loterías y validaciones
"""

import os
import json
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import streamlit as st

class CacheManager:
    """Gestor de caché inteligente para VISION PREMIUM"""
    
    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.max_size_mb = max_size_mb
        self.cache_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorios
        (self.cache_dir / "ai_analysis").mkdir(exist_ok=True)
        (self.cache_dir / "lottery_results").mkdir(exist_ok=True)
        (self.cache_dir / "validation_results").mkdir(exist_ok=True)
        (self.cache_dir / "temp").mkdir(exist_ok=True)
        
        # Configuración de TTL (Time To Live)
        self.ttl_config = {
            "ai_analysis": timedelta(hours=24),      # Análisis de IA: 24 horas
            "lottery_results": timedelta(days=7),    # Resultados de lotería: 7 días
            "validation_results": timedelta(hours=6), # Validaciones: 6 horas
            "temp": timedelta(hours=1)               # Archivos temporales: 1 hora
        }
        
        # Limpiar caché expirado al inicializar
        self.cleanup_expired_cache()
    
    def _generate_cache_key(self, data: str, prefix: str = "") -> str:
        """Genera una clave única para el caché"""
        content_hash = hashlib.md5(data.encode()).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{content_hash}_{timestamp}"
    
    def _get_cache_file_path(self, cache_key: str, cache_type: str) -> Path:
        """Obtiene la ruta del archivo de caché"""
        return self.cache_dir / cache_type / f"{cache_key}.cache"
    
    def _get_cache_metadata_path(self, cache_key: str, cache_type: str) -> Path:
        """Obtiene la ruta del archivo de metadatos"""
        return self.cache_dir / cache_type / f"{cache_key}.meta"
    
    def _is_cache_valid(self, cache_key: str, cache_type: str) -> bool:
        """Verifica si el caché es válido (no expirado)"""
        meta_path = self._get_cache_metadata_path(cache_key, cache_type)
        
        if not meta_path.exists():
            return False
        
        try:
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            created_time = datetime.fromisoformat(metadata['created_at'])
            ttl = self.ttl_config.get(cache_type, timedelta(hours=1))
            
            return datetime.now() - created_time < ttl
            
        except Exception:
            return False
    
    def _get_cache_size_mb(self) -> float:
        """Obtiene el tamaño total del caché en MB"""
        total_size = 0
        for cache_type in self.ttl_config.keys():
            cache_type_dir = self.cache_dir / cache_type
            if cache_type_dir.exists():
                for file_path in cache_type_dir.glob("*.cache"):
                    total_size += file_path.stat().st_size
        
        return total_size / (1024 * 1024)  # Convertir a MB
    
    def _cleanup_oldest_cache(self, cache_type: str, target_size_mb: float):
        """Elimina el caché más antiguo hasta alcanzar el tamaño objetivo"""
        cache_type_dir = self.cache_dir / cache_type
        
        if not cache_type_dir.exists():
            return
        
        # Obtener todos los archivos de caché con sus metadatos
        cache_files = []
        for cache_file in cache_type_dir.glob("*.cache"):
            meta_file = cache_file.with_suffix('.meta')
            if meta_file.exists():
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    created_time = datetime.fromisoformat(metadata['created_at'])
                    cache_files.append((cache_file, meta_file, created_time))
                except Exception:
                    # Si no se puede leer metadata, eliminar archivo
                    cache_file.unlink(missing_ok=True)
                    meta_file.unlink(missing_ok=True)
        
        # Ordenar por fecha de creación (más antiguos primero)
        cache_files.sort(key=lambda x: x[2])
        
        # Eliminar archivos hasta alcanzar el tamaño objetivo
        current_size = self._get_cache_size_mb()
        for cache_file, meta_file, _ in cache_files:
            if current_size <= target_size_mb:
                break
            
            file_size_mb = cache_file.stat().st_size / (1024 * 1024)
            cache_file.unlink(missing_ok=True)
            meta_file.unlink(missing_ok=True)
            current_size -= file_size_mb
    
    def cleanup_expired_cache(self):
        """Limpia todo el caché expirado"""
        for cache_type in self.ttl_config.keys():
            cache_type_dir = self.cache_dir / cache_type
            
            if not cache_type_dir.exists():
                continue
            
            for cache_file in cache_type_dir.glob("*.cache"):
                cache_key = cache_file.stem
                if not self._is_cache_valid(cache_key, cache_type):
                    # Eliminar archivo de caché y metadatos
                    cache_file.unlink(missing_ok=True)
                    meta_file = self._get_cache_metadata_path(cache_key, cache_type)
                    meta_file.unlink(missing_ok=True)
        
        # Verificar tamaño total y limpiar si es necesario
        if self._get_cache_size_mb() > self.max_size_mb:
            self._cleanup_oldest_cache("ai_analysis", self.max_size_mb * 0.7)
            self._cleanup_oldest_cache("lottery_results", self.max_size_mb * 0.8)
            self._cleanup_oldest_cache("validation_results", self.max_size_mb * 0.9)
    
    def set_cache(self, data: Any, cache_type: str, custom_key: str = None) -> str:
        """Guarda datos en el caché"""
        try:
            # Generar clave de caché
            if custom_key:
                cache_key = custom_key
            else:
                data_str = json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
                cache_key = self._generate_cache_key(data_str, cache_type)
            
            # Verificar tamaño del caché
            if self._get_cache_size_mb() > self.max_size_mb:
                self.cleanup_expired_cache()
            
            # Guardar datos
            cache_file = self._get_cache_file_path(cache_key, cache_type)
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # Guardar metadatos
            metadata = {
                'created_at': datetime.now().isoformat(),
                'cache_type': cache_type,
                'size_bytes': cache_file.stat().st_size,
                'data_type': type(data).__name__
            }
            
            meta_file = self._get_cache_metadata_path(cache_key, cache_type)
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return cache_key
            
        except Exception as e:
            print(f"Error al guardar en caché: {e}")
            return None
    
    def get_cache(self, cache_key: str, cache_type: str) -> Optional[Any]:
        """Obtiene datos del caché si son válidos"""
        try:
            if not self._is_cache_valid(cache_key, cache_type):
                return None
            
            cache_file = self._get_cache_file_path(cache_key, cache_type)
            if not cache_file.exists():
                return None
            
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            print(f"Error al leer del caché: {e}")
            return None
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Obtiene información detallada del caché"""
        info = {
            'total_size_mb': round(self._get_cache_size_mb(), 2),
            'max_size_mb': self.max_size_mb,
            'cache_types': {}
        }
        
        for cache_type in self.ttl_config.keys():
            cache_type_dir = self.cache_dir / cache_type
            if cache_type_dir.exists():
                cache_files = list(cache_type_dir.glob("*.cache"))
                total_size = sum(f.stat().st_size for f in cache_files)
                
                info['cache_types'][cache_type] = {
                    'file_count': len(cache_files),
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'ttl_hours': self.ttl_config[cache_type].total_seconds() / 3600
                }
        
        return info
    
    def clear_cache(self, cache_type: str = None):
        """Limpia el caché especificado o todo el caché"""
        if cache_type:
            cache_type_dir = self.cache_dir / cache_type
            if cache_type_dir.exists():
                for file_path in cache_type_dir.glob("*"):
                    file_path.unlink(missing_ok=True)
        else:
            # Limpiar todo el caché
            for cache_type in self.ttl_config.keys():
                cache_type_dir = self.cache_dir / cache_type
                if cache_type_dir.exists():
                    for file_path in cache_type_dir.glob("*"):
                        file_path.unlink(missing_ok=True)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché para Streamlit"""
        info = self.get_cache_info()
        
        stats = {
            'total_size_mb': info['total_size_mb'],
            'max_size_mb': info['max_size_mb'],
            'usage_percentage': round((info['total_size_mb'] / info['max_size_mb']) * 100, 1),
            'cache_types': {}
        }
        
        for cache_type, type_info in info['cache_types'].items():
            stats['cache_types'][cache_type] = {
                'files': type_info['file_count'],
                'size_mb': type_info['size_mb'],
                'ttl_hours': type_info['ttl_hours']
            }
        
        return stats

# Instancia global del caché
cache_manager = CacheManager()

# Funciones de conveniencia para uso directo
def cache_ai_analysis(data: Any, custom_key: str = None) -> str:
    """Guarda análisis de IA en caché"""
    return cache_manager.set_cache(data, "ai_analysis", custom_key)

def get_cached_ai_analysis(cache_key: str) -> Optional[Any]:
    """Obtiene análisis de IA del caché"""
    return cache_manager.get_cache(cache_key, "ai_analysis")

def cache_lottery_result(data: Any, custom_key: str = None) -> str:
    """Guarda resultado de lotería en caché"""
    return cache_manager.set_cache(data, "lottery_results", custom_key)

def get_cached_lottery_result(cache_key: str) -> Optional[Any]:
    """Obtiene resultado de lotería del caché"""
    return cache_manager.get_cache(cache_key, "lottery_results")

def cache_validation_result(data: Any, custom_key: str = None) -> str:
    """Guarda resultado de validación en caché"""
    return cache_manager.set_cache(data, "validation_results", custom_key)

def get_cached_validation_result(cache_key: str) -> Optional[Any]:
    """Obtiene resultado de validación del caché"""
    return cache_manager.get_cache(cache_key, "validation_results")

def get_cache_stats() -> Dict[str, Any]:
    """Obtiene estadísticas del caché"""
    return cache_manager.get_cache_stats()

def clear_all_cache():
    """Limpia todo el caché"""
    cache_manager.clear_cache()

if __name__ == "__main__":
    # Prueba del sistema de caché
    print("🗄️ VISION PREMIUM - Sistema de Caché")
    print("=" * 40)
    
    # Probar guardado y lectura
    test_data = {"test": "data", "timestamp": datetime.now().isoformat()}
    
    # Guardar en caché
    cache_key = cache_ai_analysis(test_data, "test_key")
    print(f"✅ Datos guardados en caché con clave: {cache_key}")
    
    # Leer del caché
    cached_data = get_cached_ai_analysis("test_key")
    print(f"✅ Datos leídos del caché: {cached_data}")
    
    # Mostrar estadísticas
    stats = get_cache_stats()
    print(f"📊 Estadísticas del caché: {stats['total_size_mb']}MB / {stats['max_size_mb']}MB")
    
    print("\n🎯 Sistema de caché funcionando correctamente!")







