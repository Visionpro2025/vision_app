# modules/cloud_sync.py — Sincronización en la Nube
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional
import base64

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "__CONFIG" / "cloud_config.json"

class CloudSync:
    def __init__(self):
        self.config = self._load_config()
        self.sync_queue = []
        
    def _load_config(self) -> dict:
        """Carga configuración de sincronización."""
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "cloud_sync": {
                "enabled": True,
                "auto_sync": True,
                "provider": "local",  # local, gdrive, dropbox, s3
                "credentials": {},
                "sync_interval_minutes": 5
            }
        }
    
    def _save_config(self):
        """Guarda configuración de sincronización."""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    
    def queue_for_sync(self, file_path: Path, metadata: Dict = None):
        """Añade archivo a la cola de sincronización."""
        if not self.config["cloud_sync"]["enabled"]:
            return False
            
        sync_item = {
            "file_path": str(file_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "status": "pending"
        }
        
        self.sync_queue.append(sync_item)
        return True
    
    def sync_pending(self) -> List[Dict]:
        """Sincroniza archivos pendientes."""
        if not self.config["cloud_sync"]["enabled"]:
            return []
            
        synced = []
        failed = []
        
        for item in self.sync_queue[:]:  # Copy to avoid modification during iteration
            try:
                file_path = Path(item["file_path"])
                if file_path.exists():
                    # Simular subida a la nube
                    success = self._upload_file(file_path, item["metadata"])
                    if success:
                        item["status"] = "synced"
                        item["synced_at"] = datetime.now(timezone.utc).isoformat()
                        synced.append(item)
                        self.sync_queue.remove(item)
                    else:
                        item["status"] = "failed"
                        failed.append(item)
                else:
                    item["status"] = "file_not_found"
                    failed.append(item)
            except Exception as e:
                item["status"] = "error"
                item["error"] = str(e)
                failed.append(item)
        
        return synced
    
    def _upload_file(self, file_path: Path, metadata: Dict) -> bool:
        """Sube archivo a la nube (stub)."""
        provider = self.config["cloud_sync"]["provider"]
        
        if provider == "local":
            # Simular subida local (copia a carpeta de respaldo)
            backup_dir = ROOT / "__BACKUP" / datetime.now().strftime("%Y%m%d")
            backup_dir.mkdir(parents=True, exist_ok=True)
            try:
                import shutil
                shutil.copy2(file_path, backup_dir / file_path.name)
                return True
            except Exception:
                return False
        else:
            # Stub para otros proveedores
            return True  # Simular éxito
    
    def get_sync_status(self) -> Dict:
        """Obtiene estado de sincronización."""
        return {
            "enabled": self.config["cloud_sync"]["enabled"],
            "queue_size": len(self.sync_queue),
            "pending": len([i for i in self.sync_queue if i["status"] == "pending"]),
            "synced": len([i for i in self.sync_queue if i["status"] == "synced"]),
            "failed": len([i for i in self.sync_queue if i["status"] == "failed"])
        }

def render_cloud_sync_ui():
    """Renderiza UI de sincronización en la nube."""
    st.subheader("☁️ Sincronización en la Nube")
    
    sync = CloudSync()
    
    # Configuración
    col1, col2 = st.columns(2)
    with col1:
        enabled = st.toggle("Sincronización Activa", value=sync.config["cloud_sync"]["enabled"])
        auto_sync = st.toggle("Auto-sincronización", value=sync.config["cloud_sync"]["auto_sync"])
    
    with col2:
        provider = st.selectbox(
            "Proveedor",
            ["local", "gdrive", "dropbox", "s3"],
            index=["local", "gdrive", "dropbox", "s3"].index(sync.config["cloud_sync"]["provider"])
        )
        interval = st.number_input("Intervalo (min)", 1, 60, sync.config["cloud_sync"]["sync_interval_minutes"])
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración", use_container_width=True):
        sync.config["cloud_sync"].update({
            "enabled": enabled,
            "auto_sync": auto_sync,
            "provider": provider,
            "sync_interval_minutes": interval
        })
        sync._save_config()
        st.success("✅ Configuración guardada")
    
    # Estado de sincronización
    status = sync.get_sync_status()
    st.markdown("#### 📊 Estado de Sincronización")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Cola", status["queue_size"])
    col2.metric("Pendientes", status["pending"])
    col3.metric("Sincronizados", status["synced"])
    col4.metric("Fallidos", status["failed"])
    
    # Sincronizar manualmente
    if st.button("🔄 Sincronizar Ahora", use_container_width=True):
        with st.spinner("Sincronizando..."):
            synced = sync.sync_pending()
        if synced:
            st.success(f"✅ {len(synced)} archivos sincronizados")
        else:
            st.info("No hay archivos pendientes de sincronización")
    
    return sync
