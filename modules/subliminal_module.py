from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import re

# ===========================
# Configuración y utilidades
# ===========================

RUNS_DIR = Path("__RUNS") / "SUBLIMINAL"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

def _repo_root() -> Path:
    try:
        return Path(__file__).resolve().parent.parent
    except Exception:
        return Path.cwd()

def _load_csv_safe(path: Path):
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer {path.name}: {e}")
        return None

# =========================================
# Backend NLP (opcional) + plan B diccionario
# =========================================

def _nlp_backend(text: str):
    """
    Intenta usar un backend NLP si está instalado.
    Si no hay modelo disponible, devuelve None y se usará el plan B por diccionario.
    """
    try:
        from transformers import pipeline  # tipo: ignore
        # Intento genérico multilenguaje (si el runtime lo tiene)
        clf = pipeline("sentiment-analysis")
        out = clf(text[:512])[0]  # truncamos para robustez
        # Normalizamos a escala 0–100
        label = str(out.get("label", "")).lower()
        score = float(out.get("score", 0.0))
        if "pos" in label:
            return {"emocion": "esperanza", "intensidad": int(50 + score * 50)}
        if "neg" in label:
            return {"emocion": "miedo", "intensidad": int(50 + score * 50)}
        if "neu" in label:
            return {"emocion": "neutral", "intensidad": int(score * 50)}
        # fallback
        return {"emocion": "indignación", "intensidad": int(40 + score * 60)}
    except Exception:
        return None

# Diccionario básico de emociones (plan B)
EMO_LEX = {
    "miedo": ["crisis", "amenaza", "pánico", "temor", "colapso", "alarma"],
    "esperanza": ["récord", "histórico", "avance", "renace", "mejora", "ayuda"],
    "indignación": ["fraude", "escándalo", "corrupción", "abuso", "protesta"],
    "tristeza": ["tragedia", "pérdida", "luto", "derrota", "accidente"],
    "ira": ["golpe", "ataque", "violencia", "furia", "rabia"],
}

# Patrones de arquetipos (regex sencillas / palabras clave)
ARCHETYPES = {
    "Héroe": [r"\bresc(a|ate)\b", r"\bvalien\w*\b", r"\bvence\w*\b", r"\blogr(a|o)\b"],
    "Víctima": [r"\bvíctim\w*\b", r"\bafectad\w*\b", r"\bdamnificad\w*\b", r"\bperjudicad\w*\b"],
    "Confrontación": [r"\bchoque\b", r"\bdisputa\b", r"\bconflict\w*\b", r"\bconfronta\w*\b"],
    "Renacimiento": [r"\brenace\w*\b", r"\breconstru\w*\b", r"\brecupera\w*\b", r"\bnuevo comienzo\b"],
}

# ==============================
# 1) Analizar sentimiento
# ==============================

def analizar_sentimiento(texto: str) -> dict:
    texto_n = (texto or "").lower()

    # Intento NLP real
    nlp_res = _nlp_backend(texto_n)
    if nlp_res is not None:
        return nlp_res

    # Plan B: conteo por diccionario
    scores = {emo: 0 for emo in EMO_LEX}
    for emo, palabras in EMO_LEX.items():
        for w in palabras:
            scores[emo] += len(re.findall(rf"\b{re.escape(w)}\b", texto_n))

    # Escala de intensidad simple
    emo_dom = max(scores, key=scores.get) if scores else "neutral"
    total = sum(scores.values())
    intensidad = 20 if total == 0 else min(100, 40 + total * 10)
    return {"emocion": emo_dom, "intensidad": intensidad}

# ==============================
# 2) Clasificar arquetipo
# ==============================

def clasificar_arquetipo(texto: str) -> str:
    texto_n = (texto or "").lower()
    for nombre, patrones in ARCHETYPES.items():
        for pat in patrones:
            if re.search(pat, texto_n):
                return nombre
    # Heurística muy simple si no hay match:
    if any(w in texto_n for w in ["récord", "logro", "ganador", "premio"]):
        return "Héroe"
    if any(w in texto_n for w in ["fraude", "escándalo", "acusación"]):
        return "Confrontación"
    return "Víctima"

# ==============================
# 3) Extraer mensaje subliminal
# ==============================

def extraer_mensaje_subliminal(texto: str) -> dict:
    s = analizar_sentimiento(texto)
    a = clasificar_arquetipo(texto)
    mensaje = (
        f"La noticia se enmarca en un Arquetipo de {a} con un sentimiento de "
        f"{s['emocion']} (intensidad {s['intensidad']})."
    )
    return {
        "emocion": s["emocion"],
        "intensidad": s["intensidad"],
        "arquetipo": a,
        "mensaje": mensaje,
    }

# ==================================================
# Vista Streamlit: procesa noticias y exporta CSV
# ==================================================

def render_subliminal():
    st.subheader("🌀 Análisis del mensaje subliminal")

    root = _repo_root()
    ruta_news = root / "noticias.csv"
    st.caption(f"🔎 noticias.csv: {ruta_news} | existe={ruta_news.exists()}")

    if not ruta_news.exists():
        st.error("No encuentro `noticias.csv` en la raíz del repo.")
        return

    df = _load_csv_safe(ruta_news)
    if df is None or df.empty:
        st.warning("`noticias.csv` vacío o ilegible.")
        return

    # Selección simple
    fechas = sorted([f for f in df["fecha"].dropna().unique() if f])
    fecha_sel = st.selectbox("Fecha", options=["(todas)"] + fechas)

    if fecha_sel != "(todas)":
        df = df[df["fecha"] == fecha_sel]

    st.info(f"Noticias a procesar: {len(df)}")

    # Procesar todo
    out_rows = []
    for _, r in df.iterrows():
        text_full = " ".join([
            str(r.get("titular", "")),
            str(r.get("resumen", "")),
            str(r.get("etiquetas", "")),
        ])
        res = extraer_mensaje_subliminal(text_full)
        out_rows.append({
            "id_noticia": r.get("id_noticia", ""),
            "emocion": res["emocion"],
            "intensidad": res["intensidad"],
            "arquetipo": res["arquetipo"],
            "mensaje": res["mensaje"],
            "timestamp_extraccion": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        })

    df_out = pd.DataFrame(out_rows)
    st.dataframe(df_out, use_container_width=True, hide_index=True)

    # Export
    fn = f"subliminal_news_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    out_path = RUNS_DIR / fn
    df_out.to_csv(out_path, index=False, encoding="utf-8")
    st.success(f"✅ Exportado: {out_path}")

    st.download_button(
        "⬇️ Descargar resultados (CSV)",
        df_out.to_csv(index=False).encode("utf-8"),
        file_name=fn,
        mime="text/csv"
      )
