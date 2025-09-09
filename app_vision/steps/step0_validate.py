# ============================================
# 📌 PASO 0: VALIDACIÓN Y CONFIGURACIÓN INICIAL
# Carga configuración y determina bloque actual
# ============================================

import os
import yaml
from app_vision.modules.runtime_guards import block_now_et

def run(ctx, data):
    """Paso 0: Validación y configuración inicial"""
    
    # Cargar config opcional
    cfg_path = data.get("config_path") or os.environ.get("PU_CONFIG", "config/protocolo_universal.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg_loaded = yaml.safe_load(f) or {}
    else:
        cfg_loaded = {}
    
    payload = data.get("payload", {})
    payload["tz"] = "ET"
    payload["run_id"] = ctx.run_id
    
    # Determinar bloque actual
    am_end = cfg_loaded.get("blocks", {}).get("am_end", "06:30")
    mid_end = cfg_loaded.get("blocks", {}).get("mid_end", "14:10")
    payload["block_now"] = block_now_et(data.get("now_et"), am_end=am_end, mid_end=mid_end)
    
    # Cargar configuración en payload
    payload["config"] = cfg_loaded
    
    return payload