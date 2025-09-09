# ============================================
# 📌 PASO 3: ANÁLISIS DEL SORTEO ANTERIOR CON GUARDAS
# Gematría + Subliminal + Candado canónico
# ============================================

from app_vision.engine.contracts import StepError
from app_vision.modules.runtime_guards import ensure, ET
from datetime import datetime

def run(ctx, data):
    """Paso 3: Análisis del sorteo anterior con guardas estrictas"""
    
    # Extraer datos del payload
    payload = data.get("payload", {})
    pick3 = payload.get("pick3")
    pick4 = payload.get("pick4")
    date = payload.get("date")
    block = payload.get("block")
    source = payload.get("source", "unknown")
    
    # --- GUARDAS DE ENTRADA ---
    ensure(pick3 and len(pick3) == 3, "InputError", "Paso3: falta Pick3 del bloque.")
    ensure(pick4 and len(pick4) == 4, "InputError", "Paso3: falta Pick4 (no se puede formar candado).")
    
    # --- FUNCIONES AUXILIARES ---
    def _fijo2_p3(p3):  return f"{p3[1]}{p3[2]}"
    def _front2_p4(p4): return f"{p4[0]}{p4[1]}" if p4 and len(p4) == 4 else None
    def _back2_p4(p4):  return f"{p4[2]}{p4[3]}" if p4 and len(p4) == 4 else None
    
    # --- FORMACIÓN DEL CANDADO CANÓNICO ---
    fijo = _fijo2_p3(pick3)
    front = _front2_p4(pick4)
    back = _back2_p4(pick4)
    candado = [x for x in (fijo, front, back) if x]
    
    ensure(len(candado) >= 2, "InputError", "Paso3: candado incompleto (se requieren ≥2 cifras).")
    
    # Generar parlés
    parles = [[candado[i], candado[j]] for i in range(len(candado)) for j in range(i+1, len(candado))]
    
    # --- ESTRUCTURA DEL CANDADO ---
    candado_item = {
        "date": date, 
        "block": block, 
        "fijo2d": fijo, 
        "p4_front2d": front, 
        "p4_back2d": back,
        "candado": candado, 
        "parles": parles, 
        "source": source,
        "fetched_at": datetime.now(ET).isoformat(timespec="seconds")
    }
    
    # --- GEMATRÍA + SUBLIMINAL ---
    # Nota: Aquí deberías llamar a tu función existente de gematría y subliminal
    # Por ahora, simulamos la respuesta para mantener la estructura
    topics, keywords, message, trace_local = do_gematria_and_subliminal(candado_item)
    
    # Limpiar duplicados manteniendo orden
    topics = list(dict.fromkeys(topics or []))
    keywords = list(dict.fromkeys(keywords or []))
    
    # --- GUARDAS DE SALIDA ---
    ensure(bool(topics) and bool(keywords), "NoSignal", "Paso3: sin señal (topics/keywords vacíos).")
    ensure(bool(message and message.strip()), "NoSignal", "Paso3: mensaje vacío.")
    
    # --- PAYLOAD DE SALIDA ---
    result_payload = {
        "candado_items": [candado_item],
        "mensaje_guia_parcial": {
            "topics": topics[:6], 
            "keywords": keywords[:10], 
            "message": message
        },
        "trace3": trace_local or []
    }
    
    return result_payload

def do_gematria_and_subliminal(candado_item):
    """Función placeholder para gematría y subliminal"""
    # TODO: Reemplazar con tu implementación real
    topics = ["prosperidad", "cambio", "nuevo_inicio", "abundancia"]
    keywords = ["oportunidad", "crecimiento", "transformación", "éxito"]
    message = f"Mensaje guía basado en candado {candado_item['candado']}"
    trace = ["gematria_calculada", "subliminal_analizado"]
    
    return topics, keywords, message, trace

