# ============================================
# 📌 PASO 4: RECOPILACIÓN DE NOTICIAS CON GUARDAS
# Mínimo 25 noticias o error
# ============================================

from app_vision.modules.runtime_guards import ensure

def run(ctx, data):
    """Paso 4: Recopilación de noticias con guardas estrictas"""
    
    # Extraer datos del payload
    payload = data.get("payload", {})
    noticias = payload.get("noticias", [])
    tried_count = payload.get("tried_count", 0)
    rej_domain = payload.get("rej_domain", 0)
    rej_recency = payload.get("rej_recency", 0)
    
    # --- GUARDAS DE VALIDACIÓN ---
    ensure(isinstance(noticias, list), "InputError", "Paso4: noticias no es lista.")
    ensure(len(noticias) >= 25, "ThresholdFail", f"Paso4: {len(noticias)} < 25 (ajustar allowlist/ventana/keywords).")
    
    # --- PAYLOAD DE SALIDA ---
    result_payload = {
        "news": noticias,
        "news_stats": {
            "tried": tried_count,
            "accepted": len(noticias),
            "rejected_by_domain": rej_domain,
            "rejected_by_recency": rej_recency
        }
    }
    
    return result_payload



