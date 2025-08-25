# modules/subliminal_module.py — PRO UI (blindado)
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
import re

RUNS_DIR = Path("__RUNS") / "SUBLIMINAL"
RUNS_DIR.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parent.parent

# ---- Placeholders globales para mantener DOM estable ----
if "__sub_status_slot" not in st.session_state:
    st.session_state["__sub_status_slot"] = st.empty()   # mensajes/avisos
if "__sub_table_slot" not in st.session_state:
    st.session_state["__sub_table_slot"] = st.empty()    # tabla resultados

@st.cache_data(show_spinner=False)
def _load_csv_safe(path: Path):
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception:
        # No mostramos widgets aquí para no mutar el layout
        return None

# --- NLP opcional (best-effort, no rompe si falta transformers)
def _nlp_backend(text: str):
    try:
        from transformers import pipeline  # type: ignore
        clf = pipeline("sentiment-analysis")
        out = clf(text[:512])[0]
        label = str(out.get("label", "")).lower()
        score = float(out.get("score", 0.0))
        if "pos" in label:
            return {"emocion": "esperanza", "intensidad": int(50 + score * 50)}
        if "neg" in label:
            return {"emocion": "miedo", "intensidad": int(50 + score * 50)}
        if "neu" in label:
            return {"emocion": "neutral", "intensidad": int(score * 50)}
        return {"emocion": "indignación", "intensidad": int(40 + score * 60)}
    except Exception:
        return None

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

def analizar_sentimiento(texto: str) -> dict:
    texto_n = (texto or "").lower()
    nlp_res = _nlp_backend(texto_n)
    if nlp_res is not None:
        return nlp_res

    scores = {emo: 0 for emo in EMO_LEX}
    for emo, words in EMO_LEX.items():
        for w in words:
            scores[emo] += len(re.findall(rf"\b{re.escape(w)}\b", texto_n))
    emo_dom = max(scores, key=scores.get) if scores else "neutral"
    total = sum(scores.values())
    intensidad = 20 if total == 0 else min(100, 40 + total * 10)
    return {"emocion": emo_dom, "intensidad": intensidad}

def clasificar_arquetipo(texto: str) -> str:
    texto_n = (texto or "").lower()
    for nombre, pats in ARCHETYPES.items():
        for p in pats:
            if re.search(p, texto_n):
                return nombre
    if any(w in texto_n for w in ["récord", "logro", "ganador", "premio"]):
        return "Héroe"
    if any(w in texto_n for w in ["fraude", "escándalo", "acusación"]):
        return "Confrontación"
    return "Víctima"

def extraer_mensaje_subliminal(texto: str) -> dict:
    s = analizar_sentimiento(texto)
    a = clasificar_arquetipo(texto)
    mensaje = f"La noticia se enmarca en un Arquetipo de {a} con un sentimiento de {s['emocion']} (intensidad {s['intensidad']})."
    return {"emocion": s["emocion"], "intensidad": s["intensidad"], "arquetipo": a, "mensaje": mensaje}

def render_subliminal():
    st.subheader("🌀 Análisis del mensaje subliminal")

    ruta_news = ROOT / "noticias.csv"
    existe = ruta_news.exists()
    st.caption(f"🔎 noticias.csv: {ruta_news} | existe={existe}")

    # Cargamos datos (o None)
    df = _load_csv_safe(ruta_news) if existe else None
    has_data = df is not None and not df.empty

    # ===== Filtro de fecha SIEMPRE visible (se desactiva si no hay datos) =====
    if has_data and "fecha" in df.columns:
        fechas_validas = sorted([f for f in df["fecha"].dropna().unique() if f])
        opciones_fechas = ["(todas)"] + fechas_validas
    else:
        opciones_fechas = ["(todas)"]

    fecha_sel = st.selectbox(
        "Fecha",
        options=opciones_fechas,
        index=0,
        key="sub_fecha",
        disabled=not has_data
    )

    # ===== Mensaje de estado en SLOT FIJO =====
    with st.session_state["__sub_status_slot"].container():
        if not existe:
            st.error("No encuentro `noticias.csv` en la raíz del repo.")
        elif not has_data:
            st.warning("`noticias.csv` vacío o ilegible.")
        else:
            st.info(f"Noticias a procesar: **{len(df)}**")

    # Si no hay datos, deja el slot de tabla con un caption estable y sal
    if not has_data:
        with st.session_state["__sub_table_slot"].container():
            st.caption("Sin resultados para mostrar.")
        return

    # Aplica filtro de fecha (si procede)
    if fecha_sel != "(todas)" and "fecha" in df.columns:
        df = df[df["fecha"] == fecha_sel]

    # ===== Proceso principal =====
    rows = []
    with st.spinner("Procesando…"):
        for _, r in df.iterrows():
            text_full = " ".join([
                str(r.get("titular", "")),
                str(r.get("resumen", "")),
                str(r.get("etiquetas", "")),
            ])
            res = extraer_mensaje_subliminal(text_full)
            rows.append({
                "id_noticia": r.get("id_noticia", ""),
                "emocion": res["emocion"],
                "intensidad": res["intensidad"],
                "arquetipo": res["arquetipo"],
                "mensaje": res["mensaje"],
                "timestamp_extraccion": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            })
    df_out = pd.DataFrame(rows)

    # ===== KPIs (estructura fija) =====
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Noticias procesadas", len(df_out))
    with c2:
        vc = df_out["emocion"].value_counts()
        top = vc.index[0] if not vc.empty else "—"
        st.metric("Emoción dominante", str(top))
    with c3:
        st.metric("Export hoy", datetime.utcnow().strftime("%Y-%m-%d"))

    # ===== Tabla de resultados en SLOT FIJO =====
    with st.session_state["__sub_table_slot"].container():
        if df_out.empty:
            st.info("Sin resultados después del filtrado.")
        else:
            st.dataframe(df_out, use_container_width=True, hide_index=True)

    # ===== Export siempre disponible =====
    fn = f"subliminal_news_{datetime.utcnow().strftime('%Y%m%d')}.csv"
    out_path = RUNS_DIR / fn
    try:
        df_out.to_csv(out_path, index=False, encoding="utf-8")
        st.success(f"✅ Exportado: {out_path}")
    except Exception:
        st.warning("No se pudo escribir el CSV en disco (permiso o ruta).")

    st.download_button(
        "⬇️ Descargar resultados (CSV)",
        df_out.to_csv(index=False).encode("utf-8"),
        file_name=fn,
        mime="text/csv",
        use_container_width=True,
        key="sub_dl_csv"
        )
