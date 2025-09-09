# modules/storage_config.py — Configuración del Sistema de Almacenamiento Organizado

from pathlib import Path
from datetime import datetime
import json
import pandas as pd

class NewsStorageConfig:
    """Configuración centralizada para el almacenamiento de noticias."""
    
    def __init__(self):
        # Directorios base
        self.ROOT = Path(__file__).resolve().parent.parent
        self.RUNS_DIR = self.ROOT / "__RUNS"
        self.NEWS_DIR = self.RUNS_DIR / "NEWS"
        self.ARCHIVE_DIR = self.RUNS_DIR / "ARCHIVE"
        self.TEMP_DIR = self.RUNS_DIR / "TEMP"
        
        # Crear directorios si no existen
        for directory in [self.RUNS_DIR, self.NEWS_DIR, self.ARCHIVE_DIR, self.TEMP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Estructura de almacenamiento
        self.STORAGE_STRUCTURE = {
            "raw_news": self.NEWS_DIR / "raw",
            "processed_news": self.NEWS_DIR / "processed", 
            "categorized_news": self.NEWS_DIR / "categorized",
            "t70_mapped": self.NEWS_DIR / "t70_mapped",
            "gem_results": self.NEWS_DIR / "gematria",
            "sub_results": self.NEWS_DIR / "subliminal",
            "protocol_logs": self.NEWS_DIR / "logs",
            "exports": self.NEWS_DIR / "exports"
        }
        
        # Crear estructura de directorios
        for dir_path in self.STORAGE_STRUCTURE.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def get_storage_path(self, storage_type: str) -> Path:
        """Obtiene la ruta de almacenamiento para un tipo específico."""
        return self.STORAGE_STRUCTURE.get(storage_type, self.TEMP_DIR)
    
    def save_news_data(self, data: pd.DataFrame, storage_type: str, filename: str = None) -> Path:
        """Guarda datos de noticias en el almacenamiento correspondiente."""
        if data.empty:
            return None
        
        storage_path = self.get_storage_path(storage_type)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{storage_type}_{timestamp}.csv"
        
        file_path = storage_path / filename
        
        try:
            data.to_csv(file_path, index=False, encoding="utf-8")
            return file_path
        except Exception as e:
            print(f"Error al guardar {storage_type}: {e}")
            return None
    
    def load_news_data(self, storage_type: str, filename: str = None) -> pd.DataFrame:
        """Carga datos de noticias desde el almacenamiento."""
        storage_path = self.get_storage_path(storage_type)
        
        if filename is None:
            # Buscar el archivo más reciente
            files = list(storage_path.glob(f"{storage_type}_*.csv"))
            if not files:
                return pd.DataFrame()
            filename = max(files, key=lambda x: x.stat().st_mtime).name
        
        file_path = storage_path / filename
        
        try:
            if file_path.exists():
                return pd.read_csv(file_path, encoding="utf-8")
            else:
                return pd.DataFrame()
        except Exception as e:
            print(f"Error al cargar {storage_type}: {e}")
            return pd.DataFrame()
    
    def archive_old_data(self, days_to_keep: int = 30):
        """Archiva datos antiguos para mantener el almacenamiento limpio."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        for storage_type, storage_path in self.STORAGE_STRUCTURE.items():
            if storage_path.exists():
                for file_path in storage_path.glob("*.csv"):
                    if file_path.stat().st_mtime < cutoff_date:
                        # Mover a archivo
                        archive_path = self.ARCHIVE_DIR / storage_type / file_path.name
                        archive_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.rename(archive_path)
    
    def get_storage_status(self) -> dict:
        """Obtiene el estado del almacenamiento."""
        status = {}
        
        for storage_type, storage_path in self.STORAGE_STRUCTURE.items():
            if storage_path.exists():
                files = list(storage_path.glob("*.csv"))
                status[storage_type] = {
                    "path": str(storage_path),
                    "file_count": len(files),
                    "total_size_mb": sum(f.stat().st_size for f in files) / (1024 * 1024),
                    "latest_file": max(files, key=lambda x: x.stat().st_mtime).name if files else None
                }
            else:
                status[storage_type] = {
                    "path": str(storage_path),
                    "file_count": 0,
                    "total_size_mb": 0,
                    "latest_file": None
                }
        
        return status
    
    def cleanup_temp_files(self):
        """Limpia archivos temporales."""
        temp_files = list(self.TEMP_DIR.glob("*"))
        for file_path in temp_files:
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Error al limpiar {file_path}: {e}")

# Instancia global
news_storage_config = NewsStorageConfig()

