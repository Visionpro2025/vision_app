# modules/noticias_module.py — Dual view + auto-acopio diario
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
import requests

ROOT = Path(__file__).resolve().parent.parent
NEWS_CSV = ROOT / "noticias.csv"
RUNS_NEWS = ROOT / "__RUNS" / "NEWS"; RUNS_NEWS.mkdir(parents=True, exist_ok=True)
STAMP = RUNS_NEWS / "last_fetch_UTC.txt"

def _ensure_cols(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["id_noticia","fecha","sorteo","pais","fuente","titular","resumen",
            "etiquetas","nivel_emocional_diccionario","nivel_emocional_modelo",
            "nivel_emocional_final","noticia_relevante","categorias_t70_ref","url"]
    for c in cols:
        if c not in df.columns: df[c] = ""
    return df[cols]

def _fetch_news(query: str) -> pd.DataFrame:
    try:
        api_key = st.secrets["newsapi"]["api_key"]
    except Exception:
        st.info("Configura [newsapi] en .streamlit/secrets.toml para acopio automático.")
        return pd.DataFrame()
    url = "https://newsapi.org/v2/everything"
    params = {"q": query, "language":"es","sortBy":"publishedAt","pageSize":50,"apiKey":api_key}
    try:
        r = requests.get(url, params=params, timeout=20); r.raise_for_status()
        arts = r.json().get("articles", [])
        if not arts: return pd.DataFrame()
        raw = pd.DataFrame(arts)
        df = pd.DataFrame({
            "id_noticia": raw["url"].fillna("").apply(lambda u: f"API-{abs(hash(u))}"[:18]),
            "fecha": raw.get("publishedAt",""),
            "sorteo": "",
            "pais": "",
            "fuente": raw.get("source","").apply(lambda s: (s or {}).get("name","")) if "source" in raw.columns else "",
            "titular": raw.get("title",""),
            "resumen": raw.get("description",""),
            "etiquetas": "",
            "nivel_emocional_diccionario": "",
            "nivel_emocional_modelo": "",
            "nivel_emocional_final": "",
            "noticia_relevante": True,
            "categorias_t70_ref": "",
            "url": raw.get("url",""),
        })
        return _ensure_cols(df).drop_duplicates(subset=["url"])
    except Exception as e:
        st.error(f"Acopio falló: {e}"); return pd.DataFrame()

def _auto_harvest_if_needed(current_lottery: str):
    """Ejecuta 1 vez por día UTC al abrir la sección."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    last = STAMP.read_text().strip() if STAMP.exists() else ""
    if last == today: return
    # query por lotería activa
    qmap = {
        "megamillions": "megamillions OR mega millions",
        "powerball": "powerball",
    }
    query = qmap.get(current_lottery, "lotería OR loteria OR jackpot OR sorteo")
    df_new = _fetch_news(query)
    if df_new.empty:
        STAMP.write_text(today); return
    if NEWS_CSV.exists():
        try: df_old = pd.read_csv(NEWS_CSV, dtype=str, encoding="utf-8")
        except: df_old = pd.DataFrame()
    else:
        df_old = pd.DataFrame()
    merged = pd.concat([df_old, df_new], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
    merged.to_csv(NEWS_CSV, index=False, encoding="utf-8")
    STAMP.write_text(today)
    st.toast(f"Noticias actualizadas para {current_lottery}. Filas totales: {len(merged)}", icon="📰")

def _reason_row(row: pd.Series, umbral: int = 60) -> str:
    """Motivo de filtrado para vista 'Filtrada'."""
    try:
        em_dic = int(str(row.get("nivel_emocional_diccionario","") or 0))
        em_mod = int(str(row.get("nivel_emocional_modelo","") or 0))
        em_fin = int(str(row.get("nivel_emocional_final","") or 0))
    except: em_dic = em_mod = em_fin = 0
    tags = str(row.get("etiquetas",""))
    # Criterio ejemplo: final >= umbral OR contiene palabras de alto impacto
    alto_impacto = any(w in (str(row.get("titular",""))+" "+str(row.get("resumen",""))).lower()
                       for w in ["récord","fraude","escándalo","crisis","millones","histórico"])
    if em_fin >= umbral or alto_impacto:
        return f"Incluida: nivel_emocional_final={em_fin} (umbral={umbral}){' + alto impacto' if alto_impacto else ''}"
    return f"Excluida: nivel_emocional_final={em_fin} < umbral={umbral}"

def render_noticias(current_lottery: str):
    st.caption(f"Lotería activa: **{current_lottery}**")
    # Auto-acopio 1 vez por día
    _auto_harvest_if_needed(current_lottery)

    if not NEWS_CSV.exists():
        st.error("No encuentro noticias.csv en la raíz del repo."); return
    try:
        df = pd.read_csv(NEWS_CSV, dtype=str, encoding="utf-8").fillna("")
    except Exception as e:
        st.error(f"No pude leer noticias.csv: {e}"); return
    if df.empty:
        st.info("noticias.csv está vacío."); return

    # Filtros rápidos
    colf1, colf2, colf3 = st.columns([1,1,2])
    fechas = ["(todas)"] + sorted([f for f in df["fecha"].unique() if f])
    fsel = colf1.selectbox("Fecha", options=fechas)
    sopts = sorted(df.get("sorteo","").unique())
    ssel = colf2.multiselect("Sorteo(s)", options=sopts, default=[])
    q = colf3.text_input("Buscar (titular/resumen/etiquetas)")

    dff = df.copy()
    if fsel != "(todas)": dff = dff[dff["fecha"] == fsel]
    if ssel: dff = dff[dff["sorteo"].isin(ssel)]
    if q.strip():
        qn = q.lower()
        dff = dff[
            dff["titular"].str.lower().str.contains(qn, na=False) |
            dff["resumen"].str.lower().str.contains(qn, na=False) |
            dff["etiquetas"].str.lower().str.contains(qn, na=False)
        ]

    st.info(f"Coincidencias tras filtros: **{len(dff)}**")
    st.markdown("---")

    # Doble ventana: Cruda vs Filtrada
    colL, colR = st.columns(2)

    with colL:
        st.subheader("🗞️ Cruda (primaria)")
        st.caption("Noticias tal cual llegan del acopio / CSV (sin filtro).")
        for _, r in dff.head(50).iterrows():  # limitar para performance
            with st.expander(f"📰 {r['titular'][:90]}"):
                st.write(r["resumen"] or "—")
                st.write(f"**Fuente:** {r['fuente']} · **Fecha:** {r['fecha']} · **Sorteo:** {r['sorteo'] or '—'}")
                if r.get("url"):
                    st.markdown(f"[🔗 Abrir fuente]({r['url']})")
                st.caption(f"Etiquetas: `{r['etiquetas']}` • Emoción(dic/mod/fin): {r['nivel_emocional_diccionario']}/{r['nivel_emocional_modelo']}/{r['nivel_emocional_final']}")

    with colR:
        st.subheader("✅ Filtrada (alta relevancia)")
        umbral = st.slider("Umbral de emoción final", 0, 100, 60)
        # aplica criterio
        mask = []
        reasons = []
        for _, rr in dff.iterrows():
            reason = _reason_row(rr, umbral=umbral)
            reasons.append(reason)
            mask.append(reason.startswith("Incluida"))
        dff["__reason"] = reasons
        df_ok = dff[mask]
        st.caption(f"Seleccionadas: **{len(df_ok)}** / {len(dff)}")
        for _, r in df_ok.head(50).iterrows():
            with st.expander(f"🔥 {r['titular'][:90]}"):
                st.write(r["resumen"] or "—")
                st.write(f"**Motivo:** {r['__reason']}")
                st.write(f"**Fuente:** {r['fuente']} · **Fecha:** {r['fecha']} · **Sorteo:** {r['sorteo'] or '—'}")
                if r.get("url"):
                    st.markdown(f"[🔗 Abrir fuente]({r['url']})")
                st.caption(f"Etiquetas: `{r['etiquetas']}` • Emoción(dic/mod/fin): {r['nivel_emocional_diccionario']}/{r['nivel_emocional_modelo']}/{r['nivel_emocional_final']}")

    st.markdown("---")
    # Descargas rápidas
    cdl, cdr = st.columns(2)
    with cdl:
        st.download_button("⬇️ Descargar vista cruda (CSV)", dff.drop(columns=["__reason"], errors="ignore").to_csv(index=False).encode("utf-8"), "noticias_cruda.csv", "text/csv")
    with cdr:
        st.download_button("⬇️ Descargar vista filtrada (CSV)", df_ok.drop(columns=["__reason"], errors="ignore").to_csv(index=False).encode("utf-8"), "noticias_filtrada.csv", "text/csv")
     
