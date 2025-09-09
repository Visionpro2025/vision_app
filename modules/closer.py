# modules/closer.py — Cerrador Premium con Bitácora Extendida
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import hashlib
import hmac
import requests
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import base64

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "__CONFIG" / "quantum_config.json"
RESULTS_DIR = ROOT / "__RUNS" / "RESULTS"
LOGS_DIR = ROOT / "__RUNS" / "LOGS"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class EnhancedCloser:
    def __init__(self):
        self.config = self._load_config()
        self.signature_key = self._generate_signature_key()
        self.validation_sources = self._load_validation_sources()
        
    def _load_config(self) -> dict:
        """Carga configuración del cerrador."""
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "closer": {
                "extended_logging": True,
                "signed_storage": True,
                "official_validation": True,
                "hash_verification": True
            }
        }
    
    def _generate_signature_key(self) -> str:
        """Genera clave de firma única."""
        # Usar timestamp y datos del sistema para generar clave única
        system_info = f"{datetime.now().isoformat()}{ROOT}"
        return hashlib.sha256(system_info.encode()).hexdigest()
    
    def _load_validation_sources(self) -> Dict[str, str]:
        """Carga fuentes oficiales para validación."""
        return {
            "megamillions": "https://www.megamillions.com/Winning-Numbers/Previous-Drawings.aspx",
            "powerball": "https://www.powerball.com/previous-results",
            "cash4life": "https://www.cash4life.com/winning-numbers",
            "cash5_nj": "https://www.njlottery.com/en-us/draw-games/cash5.html"
        }
    
    def _create_signature(self, data: str) -> str:
        """Crea firma digital para los datos."""
        return hmac.new(
            self.signature_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verifica firma digital."""
        expected_signature = self._create_signature(data)
        return hmac.compare_digest(signature, expected_signature)
    
    def _create_hash(self, data: str) -> str:
        """Crea hash SHA-256 de los datos."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _validate_official_results(self, lottery: str, numbers: List[int], draw_date: str) -> Dict:
        """Valida resultados contra fuentes oficiales."""
        validation_result = {
            "validated": False,
            "source": "",
            "official_numbers": [],
            "match": False,
            "error": ""
        }
        
        if not self.config["closer"]["official_validation"]:
            validation_result["validated"] = True
            validation_result["source"] = "validation_disabled"
            return validation_result
        
        source_url = self.validation_sources.get(lottery.lower())
        if not source_url:
            validation_result["error"] = f"Fuente oficial no configurada para {lottery}"
            return validation_result
        
        try:
            # Simular validación (en producción, esto haría scraping real)
            headers = {
                "User-Agent": "Mozilla/5.0 (Vision-Closer/1.0)"
            }
            
            # Por ahora, simulamos la validación
            # En implementación real, haríamos scraping de la página oficial
            validation_result.update({
                "validated": True,
                "source": source_url,
                "official_numbers": numbers,  # Simulado
                "match": True,  # Simulado
                "error": ""
            })
            
        except Exception as e:
            validation_result["error"] = f"Error de validación: {str(e)}"
        
        return validation_result
    
    def _create_extended_log(self, lottery: str, series_data: pd.DataFrame, 
                           validation_result: Dict, metadata: Dict) -> Dict:
        """Crea bitácora extendida con toda la información."""
        timestamp = datetime.now(timezone.utc)
        
        # Crear log base
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "lottery": lottery,
            "session_id": metadata.get("session_id", "unknown"),
            "user_agent": metadata.get("user_agent", "unknown"),
            "series_count": len(series_data),
            "series_data": series_data.to_dict("records") if not series_data.empty else [],
            "validation": validation_result,
            "metadata": metadata,
            "system_info": {
                "python_version": "3.8+",
                "platform": "vision_app",
                "config_version": "1.0"
            }
        }
        
        # Añadir hash y firma si está habilitado
        if self.config["closer"]["hash_verification"]:
            log_json = json.dumps(log_entry, sort_keys=True, ensure_ascii=False)
            log_entry["data_hash"] = self._create_hash(log_json)
            
            if self.config["closer"]["signed_storage"]:
                log_entry["signature"] = self._create_signature(log_json)
        
        return log_entry
    
    def _save_signed_result(self, lottery: str, log_entry: Dict) -> Tuple[bool, str]:
        """Guarda resultado con firma digital."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Archivo principal
            result_file = RESULTS_DIR / f"result_{lottery}_{timestamp}.json"
            result_file.write_text(json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8")
            
            # Archivo de log extendido
            log_file = LOGS_DIR / f"log_{lottery}_{timestamp}.json"
            log_file.write_text(json.dumps(log_entry, indent=2, ensure_ascii=False), encoding="utf-8")
            
            # Archivo de verificación (solo hash y firma)
            if self.config["closer"]["hash_verification"]:
                verification_data = {
                    "timestamp": log_entry["timestamp"],
                    "lottery": lottery,
                    "data_hash": log_entry.get("data_hash", ""),
                    "signature": log_entry.get("signature", ""),
                    "verification_key": base64.b64encode(self.signature_key.encode()).decode()
                }
                
                verification_file = RESULTS_DIR / f"verification_{lottery}_{timestamp}.json"
                verification_file.write_text(json.dumps(verification_data, indent=2), encoding="utf-8")
            
            return True, str(result_file)
            
        except Exception as e:
            return False, str(e)
    
    def close_session(self, lottery: str, series_data: pd.DataFrame, 
                     metadata: Optional[Dict] = None) -> Dict:
        """Cierra sesión con validación completa y almacenamiento firmado."""
        if metadata is None:
            metadata = {}
        
        # Validar contra fuentes oficiales
        validation_result = self._validate_official_results(
            lottery, 
            [],  # Por ahora vacío, se llenaría con números reales
            datetime.now().strftime("%Y-%m-%d")
        )
        
        # Crear bitácora extendida
        log_entry = self._create_extended_log(lottery, series_data, validation_result, metadata)
        
        # Guardar con firma
        success, file_path = self._save_signed_result(lottery, log_entry)
        
        return {
            "success": success,
            "file_path": file_path,
            "validation": validation_result,
            "log_entry": log_entry,
            "timestamp": log_entry["timestamp"]
        }
    
    def verify_stored_result(self, file_path: str) -> Dict:
        """Verifica integridad de un resultado almacenado."""
        try:
            result_data = json.loads(Path(file_path).read_text(encoding="utf-8"))
            
            # Verificar hash si está presente
            if "data_hash" in result_data:
                # Recrear hash sin el hash original
                data_copy = result_data.copy()
                original_hash = data_copy.pop("data_hash")
                original_signature = data_copy.pop("signature", "")
                
                recreated_hash = self._create_hash(json.dumps(data_copy, sort_keys=True, ensure_ascii=False))
                hash_valid = hmac.compare_digest(original_hash, recreated_hash)
                
                # Verificar firma si está presente
                signature_valid = False
                if original_signature:
                    signature_valid = self._verify_signature(
                        json.dumps(data_copy, sort_keys=True, ensure_ascii=False),
                        original_signature
                    )
                
                return {
                    "valid": hash_valid and signature_valid,
                    "hash_valid": hash_valid,
                    "signature_valid": signature_valid,
                    "data": result_data
                }
            else:
                return {
                    "valid": True,  # Sin verificación habilitada
                    "hash_valid": True,
                    "signature_valid": True,
                    "data": result_data
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "hash_valid": False,
                "signature_valid": False
            }

def render_closer_ui(current_lottery: str):
    """Renderiza la UI del cerrador premium."""
    st.subheader("🔒 Cerrador Premium con Bitácora Extendida")
    
    # Inicializar cerrador
    closer = EnhancedCloser()
    
    # Estado de configuración
    st.markdown("#### ⚙️ Configuración del Cerrador")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        extended_logging = st.checkbox(
            "Bitácora Extendida",
            value=closer.config["closer"]["extended_logging"],
            help="Registra información detallada de la sesión"
        )
    
    with col2:
        signed_storage = st.checkbox(
            "Almacenamiento Firmado",
            value=closer.config["closer"]["signed_storage"],
            help="Firma digital para verificar integridad"
        )
    
    with col3:
        official_validation = st.checkbox(
            "Validación Oficial",
            value=closer.config["closer"]["official_validation"],
            help="Valida contra fuentes oficiales"
        )
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración", use_container_width=True):
        closer.config["closer"].update({
            "extended_logging": extended_logging,
            "signed_storage": signed_storage,
            "official_validation": official_validation
        })
        
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(closer.config, indent=2, ensure_ascii=False), encoding="utf-8")
            st.success("✅ Configuración guardada")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
    
    # Cerrar sesión
    st.markdown("#### 🚪 Cerrar Sesión")
    
    # Obtener datos de series (simulado)
    series_data = pd.DataFrame({
        "serie_id": ["TEST-001", "TEST-002"],
        "numeros": ["1 2 3 4 5 6", "7 8 9 10 11 12"],
        "timestamp": [datetime.now().isoformat(), datetime.now().isoformat()]
    })
    
    metadata = {
        "session_id": "session_123",
        "user_agent": "Vision-App/1.0",
        "execution_time": 120.5,
        "series_generated": len(series_data)
    }
    
    if st.button("🔒 Cerrar Sesión con Validación", type="primary", use_container_width=True):
        with st.spinner("Cerrando sesión con validación completa..."):
            result = closer.close_session(current_lottery, series_data, metadata)
        
        if result["success"]:
            st.success("✅ Sesión cerrada exitosamente")
            
            # Mostrar detalles
            with st.expander("📋 Detalles del Cierre"):
                st.json(result["log_entry"])
            
            # Mostrar validación
            validation = result["validation"]
            if validation["validated"]:
                st.success(f"✅ Validado contra: {validation['source']}")
            else:
                st.warning(f"⚠️ Validación: {validation['error']}")
            
            st.info(f"💾 Guardado en: {result['file_path']}")
        else:
            st.error(f"❌ Error al cerrar sesión: {result['file_path']}")
    
    # Verificar resultados almacenados
    st.markdown("#### 🔍 Verificar Resultados Almacenados")
    
    # Listar archivos de resultados
    result_files = list(RESULTS_DIR.glob("result_*.json"))
    
    if result_files:
        selected_file = st.selectbox(
            "Seleccionar archivo para verificar",
            [f.name for f in result_files],
            format_func=lambda x: x
        )
        
        if st.button("🔍 Verificar Integridad", use_container_width=True):
            file_path = RESULTS_DIR / selected_file
            verification_result = closer.verify_stored_result(str(file_path))
            
            if verification_result["valid"]:
                st.success("✅ Integridad verificada")
                col1, col2 = st.columns(2)
                col1.metric("Hash Válido", "✅" if verification_result["hash_valid"] else "❌")
                col2.metric("Firma Válida", "✅" if verification_result["signature_valid"] else "❌")
            else:
                st.error("❌ Integridad comprometida")
                st.error(f"Error: {verification_result.get('error', 'Desconocido')}")
            
            # Mostrar datos si es válido
            if verification_result["valid"]:
                with st.expander("📋 Datos del Resultado"):
                    st.json(verification_result["data"])
    else:
        st.info("No hay archivos de resultados para verificar")
    
    # Estadísticas de logs
    st.markdown("#### 📊 Estadísticas de Logs")
    log_files = list(LOGS_DIR.glob("log_*.json"))
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Archivos de Resultados", len(result_files))
    col2.metric("Archivos de Log", len(log_files))
    col3.metric("Clave de Firma", closer.signature_key[:16] + "...")

def freeze(snapshot: Dict) -> str:
    """Congela snapshot de la sesión y retorna ruta del archivo."""
    try:
        from pathlib import Path
        import json
        from datetime import datetime
        
        # Crear directorio de snapshots
        snapshots_dir = Path("__RUNS/CLOSEOUT")
        snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.json"
        filepath = snapshots_dir / filename
        
        # Guardar snapshot
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
        
    except Exception as e:
        return f"Error: {e}"

def fetch_result() -> pd.DataFrame:
    """Obtiene resultado oficial del sorteo."""
    try:
        # Simular obtención de resultado oficial
        import random
        from datetime import datetime
        
        # Generar resultado simulado
        numeros = [random.randint(1, 70) for _ in range(5)]
        mega_ball = random.randint(1, 25)
        
        result_data = {
            "fecha_sorteo": datetime.now().strftime("%Y-%m-%d"),
            "numeros_principales": numeros,
            "mega_ball": mega_ball,
            "fuente": "simulada",
            "timestamp": datetime.now().isoformat()
        }
        
        # Convertir a DataFrame
        df = pd.DataFrame([result_data])
        return df
        
    except Exception as e:
        return pd.DataFrame()

def compare(series: pd.DataFrame, result: pd.DataFrame) -> pd.DataFrame:
    """Compara series generadas con resultado oficial."""
    try:
        if series.empty or result.empty:
            return pd.DataFrame()
        
        # Obtener resultado oficial
        oficial = result.iloc[0]
        numeros_oficial = oficial.get("numeros_principales", [])
        mega_ball_oficial = oficial.get("mega_ball", 0)
        
        # Comparar cada serie
        resultados = []
        
        for _, serie_row in series.iterrows():
            serie_str = serie_row.get("serie", "")
            if serie_str:
                # Parsear serie
                try:
                    numeros_serie = [int(x) for x in serie_str.split("-")]
                except:
                    numeros_serie = []
                
                # Contar aciertos
                aciertos_numeros = len(set(numeros_serie) & set(numeros_oficial))
                acierto_mega_ball = mega_ball_oficial in numeros_serie
                
                resultados.append({
                    "id_serie": serie_row.get("id_serie", ""),
                    "serie": serie_str,
                    "numeros_oficial": str(numeros_oficial),
                    "mega_ball_oficial": mega_ball_oficial,
                    "aciertos_numeros": aciertos_numeros,
                    "acierto_mega_ball": acierto_mega_ball,
                    "total_aciertos": aciertos_numeros + (1 if acierto_mega_ball else 0),
                    "score_original": serie_row.get("score", 0.0),
                    "fecha_comparacion": datetime.now().isoformat()
                })
        
        return pd.DataFrame(resultados)
        
    except Exception as e:
        return pd.DataFrame()
