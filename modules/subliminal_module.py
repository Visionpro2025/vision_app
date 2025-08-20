
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

# ====================================================
# Backend NLP (HuggingFace) + plan B (diccionario)
# ====================================================

def _cache_resource(func):
    if hasattr(st, "cache_resource"):
        return st.cache_resource(show_spinner=False)(func)
    return func

@_cache_resource
def _get_pipelines():
    """
    Carga:
      - Sentiment (prioriza español; luego multilingüe)
      - Zero-shot classification (arquetipos)
    Devuelve dict {'sentiment': pipeline|None, 'zsc': pipeline|None}
    """
    pipes = {"sentiment": None, "zsc": None}
    try:
        from transformers import pipeline

        # 1) Sentimiento
        for model_id in [
            "pysentimiento/robertuito-sentiment-analysis",      # ES
            "finiteautomata/beto-sentiment-analysis",           # ES
            "cardiffnlp/twitter-xlm-roberta-base-sentiment",    # multilingüe
            "nlptown/bert-base-multilingual-uncased-sentiment", # multilingüe (1–5)
        ]:
            try:
                pipes["sentiment"] = pipeline("sentiment-analysis", model=model_id)
                break
            except Exception:
                continue

        # 2) Zero-shot arquetipos
        for zsc_id in [
            "joeddav/xlm-roberta-large-xnli",   # multilingüe
            "facebook/bart-large-mnli"          # inglés (sirve)
        ]:
            try:
                pipes["zsc"] = pipeline("zero-shot-classification", model=zsc_id)
                break
            except Exception:
                continue
    except Exception:
        pass

    # Indicador visible en UI
    st.caption(
        "NLP backend: "
        f"sentiment{'✔' if pipes['sentiment'] else '❌'} | "
        f"zsc{'✔' if pipes['zsc'] else '❌'}"
    )
    return pipes

def _nlp_backend_sentiment(text: str):
    """
    Devuelve {'emocion','intensidad'} usando modelo si existe; si no, None.
    """
    pipes = _get_pipelines()
    clf = pipes.get("sentiment")
    if not clf:
        return None
    try:
        out = clf((text or "")[:512])[0]
        label = str(out.get("label", "")).lower()
        score = float(out.get("score", 0.0))
        if "pos" in label:
            return {"emocion": "esperanza", "intensidad": int(50 + score * 50)}
        if "neg" in label:
            return {"emocion": "miedo", "intensidad": int(50 + score * 50)}
        if "neu" in label:
            return {"emocion": "neutral", "intensidad": int(score * 50)}
        if any(c.isdigit() for c in label):  # modelos 1–5 estrellas
            try:
                stars = int("".join([c for c in label if c.isdigit()]))
                if stars <= 2:
                    return {"emocion": "miedo", "intensidad": 70}
                if stars == 3:
                    return {"emocion": "neutral", "intensidad": 40}
                return {"emocion": "esperanza", "intensidad": 70}
            except Exception:
                pass
        return {"emocion": "indignación", "intensidad": int(40 + score * 60)}
    except Exception:
        return None

ARQUETIPOS_CANDIDATOS = ["Héroe", "Víctima", "Confrontación", "Renacimiento"]

def _nlp_backend_arquetipo(text: str) -> str | None:
    """
    Zero-shot a arquetipos. Si no hay modelo o falla, devuelve None.
    """
    pipes = _get_pipelines()
    zsc = pipes.get("zsc")
    if not zsc:
        return None
    try:
        hyp = "Esta noticia es un ejemplo de {}."
        out = zsc((text or "")[:512], candidate_labels=ARQUETIPOS_CANDIDATOS,
                  hypothesis_template=hyp, multi_label=False)
        label = out["labels"][0] if out and "labels" in out and out["labels"] else None
        return label or None
    except Exception:
        return None

# -------- Plan B (diccionario/regex) --------
EMO_LEX = {
    "miedo": ["crisis", "amenaza", "pánico", "temor", "colapso", "alarma"],
    "esperanza": ["récord", "histórico", "avance", "renace", "mejora", "ayuda"],
    "indignación": ["fraude", "escándalo", "corrupción", "abuso", "protesta"],
    "tristeza": ["tragedia", "pérdida", "luto", "derrota", "accidente"],
    "ira": ["golpe", "ataque", "violencia", "furia", "rabia"],
}

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

    # 1) NLP real
    nlp_res = _nlp_backend_sentiment(texto_n)
    if nlp_res is not None:
        return nlp_res

    # 2) Plan B
    scores = {emo: 0 for emo in EMO_LEX}
    for emo, palabras in EMO_LEX.items():
        for w in palabras:
            scores[emo] += len(re.findall(rf"\b{re.escape(w)}\b", texto_n))

    emo_dom = max(scores, key=scores.get) if scores else "neutral"
    total = sum(scores.values())
    intensidad = 20 if total == 0 else min(100, 40 + total * 10)
    return {"emocion": emo_dom, "intensidad": intensidad}

# ==============================
# 2) Clasificar arquetipo
# ==============================

def clasificar_arquetipo(texto: str) -> str:
    texto_n = (texto or "").lower()

    # 1) NLP zero-shot
    z = _nlp_backend_arquetipo(texto_n)
    if z:
        return z

    # 2) Plan B
    for nombre, patrones in ARCHETYPES.items():
        for pat in patrones:
            if re.search(pat, texto_n):
                return nombre
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

    # Filtro simple por fecha
    fechas = sorted([f for f in df["fecha"].dropna().unique() if f])
    fecha_sel = st.selectbox("Fecha", options=["(todas)"] + fechas)
    if fecha_sel != "(todas)":
        df = df[df["fecha"] == fecha_sel]

    st.info(f"Noticias a procesar: {len(df)}")

    # Procesar
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
