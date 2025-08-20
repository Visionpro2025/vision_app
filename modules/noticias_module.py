# modules/noticias_module.py — Noticias PRO con NewsAPI + auto-acopio diario
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
import requests
import re

ROOT = Path(__file__).resolve().parent.parent
NEWS_CSV = ROOT / "noticias.csv"
RUNS_NEWS = ROOT / "__RUNS" / "NEWS"
RUNS_NEWS.mkdir(parents=True, exist_ok=True)
STAMP = RUNS_NEWS / "last_fetch_UTC.txt"   # marca diario (YYYY-MM-DD)

REQUIRED_COLS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen",
    "etiquetas","nivel_emocional_diccionario","nivel_emocional_modelo",
    "nivel_emocional_final","noticia_relevante","categorias_t70_ref","url"
]

# ================== Utilidades base ==================
@st.cache_data(show_spinner=False)
def _load_news(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8").fillna("")
    except Exception:
        df = pd.DataFrame(columns=REQUIRED_COLS)
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    # normaliza fecha a YYYY-MM-DD
    if "fecha" in df.columns:
        df["fecha"] = df["fecha"].astype(str).str.slice(0, 10)
    return df[REQUIRED_COLS]

def _save_news(df: pd.DataFrame):
    df.to_csv(NEWS_CSV, index=False, encoding="utf-8")
    _load_news.clear()   # limpia caché
    st.toast("noticias.csv guardado", icon="💾")

def _to_int(x, default=0):
    try: return int(str(x).strip())
    except: return default

def _motivo(row: pd.Series, umbral: int, alto_impacto: list[str]) -> str:
    texto = f"{row.get('titular','')} {row.get('resumen','')}".lower()
    impact = any(w in texto for w in alto_impacto)
    fin = _to_int(row.get("nivel_emocional_final", 0), 0)
    if fin >= umbral and impact: return f"Incluida: emoción={fin}≥{umbral} + alto impacto"
    if fin >= umbral:           return f"Incluida: emoción={fin}≥{umbral}"
    if impact:                  return f"Incluida: alto impacto (emocion={fin}<{umbral})"
    return f"Excluida: emoción={fin}<{umbral} sin alto impacto"

def _gen_id(prefix="N") -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    base = f"{prefix}-{today}"
    df = _load_news(NEWS_CSV)
    n = sum(df["id_noticia"].astype(str).str.startswith(base)) + 1
    return f"{base}-{n:03d}"

# ============== NewsAPI ==============
def _newsapi_key() -> str | None:
    try:
        return st.secrets["newsapi"]["api_key"]
    except Exception:
        return None

def _newsapi_query_for_lottery(current_lottery: str | None) -> str:
    # Ajusta consultas por lotería; fallback general en español
    qmap = {
        "megamillions": '("mega millions" OR megamillions) OR lotería OR sorteo',
        "powerball": 'powerball OR lotería OR sorteo',
        "ny_lotto": '"new york lotto" OR "ny lotto" OR lotería',
        "california_superlotto": '"superlotto plus" OR "california lottery" OR lotería',
        "texas_lotto": '"texas lotto" OR "texas lottery" OR lotería',
    }
    return qmap.get(current_lottery or "", 'lotería OR sorteo OR jackpot OR "gran premio"')

def _fetch_news_newsapi(query: str, page_size: int = 50) -> pd.DataFrame:
    api_key = _newsapi_key()
    if not api_key:
        return pd.DataFrame()
    url = "https://newsapi.org/v2/everything"
    params = dict(q=query, language="es", sortBy="publishedAt", pageSize=page_size, apiKey=api_key)
    try:
        r = requests.get(url, params=params, timeout=25); r.raise_for_status()
        arts = r.json().get("articles", [])
        if not arts: return pd.DataFrame()
        raw = pd.DataFrame(arts)
        df = pd.DataFrame({
            "id_noticia": raw["url"].fillna("").apply(lambda u: f"API-{abs(hash(u))}"[:18]),
            "fecha": raw.get("publishedAt","").astype(str).str.slice(0, 10),
            "sorteo": "",
            "pais": "",
            "fuente": raw.get("source","").apply(lambda s: (s or {}).get("name","")) if "source" in raw.columns else "",
            "titular": raw.get("title",""),
            "resumen": raw.get("description",""),
            "etiquetas": "",
            "nivel_emocional_diccionario": "",
            "nivel_emocional_modelo": "",
            "nivel_emocional_final": "",
            "noticia_relevante": "",
            "categorias_t70_ref": "",
            "url": raw.get("url",""),
        }).fillna("")
        return df.drop_duplicates(subset=["url"])
    except Exception as e:
        st.error(f"NewsAPI falló: {e}")
        return pd.DataFrame()

def _auto_harvest_if_needed(current_lottery: str | None):
    """Se ejecuta 1 vez por día UTC. Si hay menos de 60 crudas tras filtros, intenta ampliar."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    last = STAMP.read_text().strip() if STAMP.exists() else ""
    df_current = _load_news(NEWS_CSV)

    # Ejecutar una vez al día
    if last != today:
        q = _newsapi_query_for_lottery(current_lottery)
        extra = _fetch_news_newsapi(q, page_size=50)
        if not extra.empty:
            merged = pd.concat([df_current, extra], ignore_index=True)
            if "url" in merged.columns:
                merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
            _save_news(merged)
            df_current = merged
            st.toast("📰 Acopio diario ejecutado (NewsAPI).", icon="🕘")
        STAMP.write_text(today)

    # Garantizar mínimo 60 crudas (intenta ampliar si hay API)
    if len(df_current) < 60:
        api_key = _newsapi_key()
        if api_key:
            q = _newsapi_query_for_lottery(current_lottery)
            extra = _fetch_news_newsapi(q, page_size=100)
            if not extra.empty:
                merged = pd.concat([df_current, extra], ignore_index=True)
                if "url" in merged.columns:
                    merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
                _save_news(merged)
                st.toast(f"🔎 Ampliado automáticamente: {len(merged)} filas.", icon="➕")

# ================== UI: Secciones ==================
def _ui_crudas(df: pd.DataFrame):
    st.subheader("🗞️ Noticias crudas (primarias)")
    st.caption("Lista sin filtro. Ordenadas por fecha descendente.")
    dff = df.sort_values(["fecha", "fuente", "titular"], ascending=[False, True, True]).reset_index(drop=True)
    if dff.empty:
        st.info("No hay noticias crudas para mostrar.")
        return dff
    for i in range(min(len(dff), 200)):
        r = dff.iloc[i]
        titulo = (r["titular"] or "—").strip()
        with st.expander(f"📰 {r['fecha']} · {r['fuente'] or '—'} · {titulo[:90]}"):
            st.write(r["resumen"] or "—")
            st.caption(f"Sorteo: {r['sorteo'] or '—'} · Etiquetas: `{r['etiquetas']}`")
            if r.get("url"): st.markdown(f"[🔗 Abrir fuente]({r['url']})")
    return dff

def _ui_filtradas(df: pd.DataFrame):
    st.subheader("🔥 Noticias filtradas (alto impacto)")
    colU, colW = st.columns([1, 1])
    with colU:
        umbral = st.slider("Umbral emoción final", 0, 100, 60)
    with colW:
        alto = st.multiselect(
            "Palabras de alto impacto",
            ["récord","fraude","escándalo","crisis","millones","histórico","emergencia","colapso","tragedia"],
            default=["récord","fraude","escándalo","crisis","millones","histórico"]
        )
    if df.empty:
        st.info("No hay noticias para filtrar.")
        return pd.DataFrame()
    reasons, mask = [], []
    for _, r in df.iterrows():
        m = _motivo(r, umbral, alto)
        reasons.append(m); mask.append(m.startswith("Incluida"))
    dff = df.copy(); dff["__motivo"] = reasons
    ok = dff[mask].sort_values(["fecha","fuente","titular"], ascending=[False, True, True])
    st.caption(f"Seleccionadas: **{len(ok)}** / {len(dff)}")
    if ok.empty:
        st.info("Ninguna supera el criterio actual.")
        return ok
    for i in range(min(len(ok), 120)):
        r = ok.iloc[i]
        titulo = (r["titular"] or "—").strip()
        with st.expander(f"✅ {r['fecha']} · {r['fuente'] or '—'} · {titulo[:90]}"):
            st.write(r["resumen"] or "—")
            st.write(f"**Motivo:** {r['__motivo']}")
            st.caption(f"Sorteo: {r['sorteo'] or '—'} · Etiquetas: `{r['etiquetas']}`")
            if r.get("url"): st.markdown(f"[🔗 Abrir fuente]({r['url']})")
    return ok

def _ui_procesar():
    st.subheader("⚙️ Procesar / Analizar noticias")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔤 Abrir Gematría", use_container_width=True):
            st.session_state["_nav"] = "🔡 Gematría"; st.rerun()
    with c2:
        if st.button("🌀 Abrir Subliminal", use_container_width=True):
            st.session_state["_nav"] = "🌀 Análisis subliminal"; st.rerun()
    st.caption("Valida primero en Filtradas y luego pasa solo las más fuertes.")

def _ui_explorador(df: pd.DataFrame, current_lottery: str | None):
    st.subheader("🔎 Explorador de noticias")
    st.caption("Busca más noticias. Si no hay NewsAPI, usa la carga manual o subir CSV.")
    q_default = _newsapi_query_for_lottery(current_lottery)
    q = st.text_input("Consulta (ej. powerball OR megamillions OR lotería)", q_default)
    n = st.slider("Cantidad a traer (NewsAPI)", 20, 100, 50, step=10)
    colB1, colB2 = st.columns(2)
    with colB1:
        if st.button("🌐 Traer con NewsAPI", use_container_width=True, disabled=_newsapi_key() is None):
            extra = _fetch_news_newsapi(q, page_size=int(n))
            if extra.empty:
                st.warning("No se trajo nada (revisa API key o consulta).")
            else:
                merged = pd.concat([df, extra], ignore_index=True)
                if "url" in merged.columns:
                    merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
                _save_news(merged)
                st.success(f"Agregadas {len(merged) - len(df)} noticias nuevas.")
                st.rerun()
    with colB2:
        st.download_button(
            "⬇️ Descargar noticias actuales (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("### ✍️ Ingreso manual (una noticia)")
    with st.form("manual_news"):
        fecha = st.date_input("Fecha (UTC)", value=None)
        sorteo = st.text_input("Sorteo (ej. MegaMillions)")
        pais = st.text_input("País", "US")
        fuente = st.text_input("Fuente (ej. Reuters)")
        titular = st.text_input("Titular")
        resumen = st.text_area("Resumen", height=120)
        url = st.text_input("URL (opcional)")
        etiquetas = st.text_input("Etiquetas separadas por ;", "manual;ingreso")
        submitted = st.form_submit_button("➕ Agregar a noticias.csv")
    if submitted:
        if not titular.strip():
            st.error("El titular es obligatorio.")
        else:
            df2 = df.copy()
            new_row = {
                "id_noticia": _gen_id("N"),
                "fecha": (fecha.isoformat() if fecha else datetime.utcnow().strftime("%Y-%m-%d")),
                "sorteo": sorteo.strip(),
                "pais": pais.strip(),
                "fuente": fuente.strip(),
                "titular": titular.strip(),
                "resumen": resumen.strip(),
                "etiquetas": etiquetas.strip(),
                "nivel_emocional_diccionario": "",
                "nivel_emocional_modelo": "",
                "nivel_emocional_final": "",
                "noticia_relevante": "",
                "categorias_t70_ref": "",
                "url": url.strip(),
            }
            df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=True)
            _save_news(df2)
            st.success("Noticia agregada.")
            st.rerun()

    st.markdown("### ⬆️ Cargar CSV adicional")
    up = st.file_uploader("Subir CSV con mismas columnas de noticias.csv", type=["csv"])
    if up is not None:
        try:
            extra = pd.read_csv(up, dtype=str, encoding="utf-8").fillna("")
            for c in REQUIRED_COLS:
                if c not in extra.columns:
                    extra[c] = ""
            merged = pd.concat([df, extra[REQUIRED_COLS]], ignore_index=True)
            if "url" in merged.columns:
                merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
            _save_news(merged)
            st.success(f"Se agregaron {len(merged)-len(df)} filas desde el CSV.")
            st.rerun()
        except Exception as e:
            st.error(f"No pude leer el CSV subido: {e}")

def _ui_limpiar(df: pd.DataFrame):
    st.subheader("🧹 Borrar basura / residuos")
    if df.empty:
        st.info("No hay nada para limpiar."); return
    c1, c2, c3 = st.columns(3)
    f_fecha = c1.selectbox("Filtrar por fecha", options=["(todas)"] + sorted(df["fecha"].unique()))
    f_fuente = c2.selectbox("Filtrar por fuente", options=["(todas)"] + sorted(df["fuente"].unique()))
    regex = c3.text_input("Filtrar por regex en titular (opcional)", "")
    dff = df.copy()
    if f_fecha != "(todas)": dff = dff[dff["fecha"] == f_fecha]
    if f_fuente != "(todas)": dff = dff[dff["fuente"] == f_fuente]
    if regex.strip():
        try:
            dff = dff[dff["titular"].str.contains(regex, flags=re.IGNORECASE, na=False, regex=True)]
        except Exception as e:
            st.warning(f"Regex inválida: {e}")
    st.caption(f"Candidatas: {len(dff)}")
    ids = st.multiselect("Selecciona id_noticia a eliminar", options=dff["id_noticia"].tolist())
    colD1, colD2 = st.columns(2)
    with colD1:
        if st.button("🗑️ Eliminar seleccionadas", use_container_width=True, disabled=not ids):
            cleaned = df[~df["id_noticia"].isin(ids)].reset_index(drop=True)
            _save_news(cleaned)
            st.success(f"Eliminadas {len(ids)} filas.")
            st.rerun()
    with colD2:
        st.download_button(
            "⬇️ Descargar copia limpia (CSV)",
            (df[~df["id_noticia"].isin(ids)]).to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_limpio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv",
            use_container_width=True,
        )

def _ui_archivo(df: pd.DataFrame):
    st.subheader("🗂️ Archivo / Historial")
    if df.empty:
        st.info("Sin historial aún."); return
    c1, c2 = st.columns(2)
    fechas = ["(todas)"] + sorted(df["fecha"].unique())
    sorteos = ["(todos)"] + sorted(df["sorteo"].unique())
    fs = c1.selectbox("Fecha", options=fechas)
    ss = c2.selectbox("Sorteo", options=sorteos)
    dff = df.copy()
    if fs != "(todas)": dff = dff[dff["fecha"] == fs]
    if ss != "(todos)": dff = dff[dff["sorteo"] == ss]
    st.dataframe(
        dff.sort_values(["fecha","fuente","titular"], ascending=[False, True, True]),
        use_container_width=True, hide_index=True
    )

# ================== Vista principal ==================
def render_noticias(current_lottery: str | None = None):
    """Render del módulo. current_lottery es opcional (compatibilidad con app.py antiguo)."""
    # 1) Auto-acopio (si hay API) y mínimo volumen
    _auto_harvest_if_needed(current_lottery)

    # 2) Cargar df base
    df_all = _load_news(NEWS_CSV)

    # 3) Filtros globales
    colf1, colf2, colf3 = st.columns([1,1,2])
    fechas = ["(todas)"] + sorted([f for f in df_all["fecha"].unique() if f])
    sorteos = ["(todos)"] + sorted([s for s in df_all["sorteo"].unique() if s])
    fsel = colf1.selectbox("Fecha", options=fechas)
    ssel = colf2.selectbox("Sorteo", options=sorteos)
    q = colf3.text_input("Buscar (titular/resumen/etiquetas)")

    base = df_all.copy()
    if fsel != "(todas)": base = base[base["fecha"] == fsel]
    if ssel != "(todos)": base = base[base["sorteo"] == ssel]
    if q.strip():
        qn = q.lower().strip()
        base = base[
            base["titular"].str.lower().str.contains(qn, na=False) |
            base["resumen"].str.lower().str.contains(qn, na=False) |
            base["etiquetas"].str.lower().str.contains(qn, na=False)
        ]

    st.info(f"Noticias tras filtros: **{len(base)}**")
    st.markdown("---")

    # 4) Botones de sección
    b1, b2, b3, b4, b5 = st.columns(5)
    show_crudas = b1.button("🗞️ Crudas (primarias)", type="secondary", use_container_width=True)
    show_filtradas = b2.button("🔥 Filtradas (impacto)", type="secondary", use_container_width=True)
    show_proc = b3.button("⚙️ Procesar/Analizar", type="secondary", use_container_width=True)
    show_expl = b4.button("🔎 Explorador / Ingreso", type="secondary", use_container_width=True)
    show_clean = b5.button("🧹 Limpiar", type="secondary", use_container_width=True)

    # Sugerencia si hay poco volumen
    if len(base) < 60 and _newsapi_key():
        st.warning(f"Menos de 60 noticias crudas ({len(base)}). Usa **Explorador** para ampliar.")
        show_expl = True

    # 5) Render condicional
    if show_crudas:
        _ui_crudas(base); st.markdown("---")
    if show_filtradas:
        _ui_filtradas(base); st.markdown("---")
    if show_proc:
        _ui_procesar(); st.markdown("---")
    if show_expl:
        _ui_explorador(df_all, current_lottery); st.markdown("---")
    if show_clean:
        _ui_limpiar(df_all); st.markdown("---")

    # 6) Archivo/historial siempre disponible
    with st.expander("🗂️ Ver archivo / historial"):
        _ui_archivo(df_all)

    # 7) Descargas rápidas
    colD1, colD2 = st.columns(2)
    with colD1:
        st.download_button(
            "⬇️ Descargar vista actual (CSV)",
            base.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_vista_{datetime.utcnow().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with colD2:
        st.download_button(
            "⬇️ Descargar noticias.csv completo",
            _load_news(NEWS_CSV).to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_completo_{datetime.utcnow().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
                                                       )
