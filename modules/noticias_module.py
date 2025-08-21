# modules/noticias_module.py — Filtro emocional PRO (USA) + mini-menú in-app
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
import requests
import re
# ==== Helpers para NewsAPI y utilidades ====
from datetime import datetime, timedelta
import requests

NEWS_COLS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen","etiquetas",
    "nivel_emocional_diccionario","nivel_emocional_modelo","nivel_emocional_final",
    "noticia_relevante","categorias_t70_ref","url"
]

def _ensure_news_cols(df: pd.DataFrame) -> pd.DataFrame:
    for c in NEWS_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[NEWS_COLS]

def _read_news_csv(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8")
        df = _ensure_news_cols(df)
        return df
    except Exception:
        return pd.DataFrame(columns=NEWS_COLS)

def _write_news_csv(path: Path, df: pd.DataFrame):
    df = _ensure_news_cols(df)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")

def _newsapi_key() -> str | None:
    try:
        return st.secrets["newsapi"]["api_key"]
    except Exception:
        return None

def fetch_news_newsapi(query: str, date_from: str, date_to: str, page_size: int = 50) -> list[dict]:
    """Devuelve lista simplificada de artículos usando NewsAPI (si hay clave)."""
    api_key = _newsapi_key()
    if not api_key:
        st.warning("No hay API key en .streamlit/secrets.toml → [newsapi].")
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "from": date_from,
        "to": date_to,
        "sortBy": "relevancy",
        "pageSize": max(1, min(page_size, 100)),
        "apiKey": api_key,
    }
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        arts = data.get("articles", [])
        out = []
        for a in arts:
            out.append({
                "fecha": (a.get("publishedAt","") or "")[:10],
                "fuente": (a.get("source",{}) or {}).get("name",""),
                "titular": a.get("title","") or "",
                "resumen": a.get("description","") or "",
                "url": a.get("url","") or "",
                "pais": "US",         # asumimos foco en EE.UU.
                "sorteo": "",         # usuario podrá ajustar luego
                "etiquetas": "",
                "nivel_emocional_diccionario": "",
                "nivel_emocional_modelo": "",
                "nivel_emocional_final": "",
                "noticia_relevante": "",
                "categorias_t70_ref": "",
            })
        return out
    except Exception as e:
        st.error(f"Error consultando NewsAPI: {e}")
        return []

def _make_id(prefix: str = "N") -> str:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"{prefix}-{ts}"
ROOT = Path(__file__).resolve().parent.parent
NEWS_CSV = ROOT / "noticias.csv"
RUNS_NEWS = ROOT / "__RUNS" / "NEWS"
RUNS_NEWS.mkdir(parents=True, exist_ok=True)
STAMP = RUNS_NEWS / "last_fetch_UTC.txt"   # marca diario (YYYY-MM-DD)

# ================== Config general ==================
REQUIRED_COLS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen",
    "etiquetas","nivel_emocional_diccionario","nivel_emocional_modelo",
    "nivel_emocional_final","noticia_relevante","categorias_t70_ref","url"
]

UMBRAL_DEFECTO = 60  # umbral de alto impacto (0–100)

# Palabras de alto impacto para rescate rápido (sin dep. de modelo)
PALABRAS_ALTO_IMPACTO_DEFAULT = [
    "mortal","muertes","fallecidos","tragedia","desastre","emergencia","crisis",
    "huracán","tormenta","tornado","inundación","terremoto","incendio","evacuación",
    "tiroteo","ataque","explosión","guerra","conflicto","terrorismo",
    "récord","histórico","masivo","colapso","apagón","quiebra","pánico",
]

# Lexicón emocional básico (ponderado)
EMO_LEX = {
    "miedo":     {"crisis":3,"amenaza":3,"pánico":3,"temor":2,"colapso":3,"alarma":3,"emergencia":3,"evacuación":3,"huracán":3,"tormenta":3,"tornado":3,"inundación":3,"terremoto":3,"incendio":3,"apagón":2},
    "tristeza":  {"tragedia":3,"pérdida":2,"luto":2,"derrota":2,"accidente":2,"fallecidos":3,"muertes":3,"víctimas":3,"desaparición":2},
    "ira":       {"golpe":2,"ataque":3,"violencia":3,"furia":2,"rabia":2,"corrupción":3,"abuso":3,"indignación":3,"fraude":3,"escándalo":3},
    "esperanza": {"récord":2,"histórico":2,"avance":2,"renace":2,"mejora":2,"ayuda":2,"rescate":3,"solidaridad":2,"reconstrucción":2},
    "euforia":   {"éxito":2,"victoria":2,"celebra":2,"triunfo":2,"récord":2,"histórico":2,"campeón":2},
    "shock":     {"explosión":3,"derrumbe":3,"catastrófico":3,"devastador":3,"colapso":3},
}

# Categorías amplias (regex) — multi-etiqueta
CATEGORY_PATTERNS = {
    "desastre_natural":  r"\b(huracán|tormenta|tornado|inundaci[oó]n|terremoto|sismo|incendio forestal|ola de calor|nevada|granizo)\b",
    "crisis_publica":    r"\b(emergencia|evacuaci[oó]n|escasez|apag[oó]n|brotes?|epidemia|pandemia)\b",
    "conflicto_violencia": r"\b(guerra|conflicto|ataque|tiroteo|terrorismo|disturbios|mot[ií]n|bomba|explosi[oó]n)\b",
    "muertes_tragedias": r"\b(muert[eo]s?|fallecid[oa]s?|víctimas?|tragedia|luto|funeral|masacre)\b",
    "economia_mercados": r"\b(crisis|inflaci[oó]n|recesi[oó]n|quiebra|default|ca[ií]da|colapso|r[eé]cord|hist[oó]rico)\b",
    "politica_justicia": r"\b(esc[aá]ndalo|corrupci[oó]n|fraude|acusaci[oó]n|juicio|arresto|impeachment)\b",
    "ciencia_tec":       r"\b(ciberataque|brecha de datos|apag[oó]n|fallo t[eé]cnico|IA|inteligencia artificial|hackeo)\b",
    "cultura_deportes":  r"\b(celebridad|famos[oa]|campe[oó]n|t[ií]tulo|final|ol[ií]mpicos|r[eé]cord)\b",
}

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
    if "fecha" in df.columns:
        df["fecha"] = df["fecha"].astype(str).str.slice(0, 10)
    return df[REQUIRED_COLS]

def _save_news(df: pd.DataFrame):
    df.to_csv(NEWS_CSV, index=False, encoding="utf-8")
    _load_news.clear()
    st.toast("noticias.csv guardado", icon="💾")

def _to_int(x, default=0):
    try: return int(str(x).strip())
    except: return default

def _nlp_backend(text: str) -> dict | None:
    """Intento de usar modelo si existe; si no, devuelve None."""
    try:
        from transformers import pipeline  # opcional
        clf = pipeline("sentiment-analysis")
        out = clf(text[:512])[0]
        label = str(out.get("label","")).lower()
        score = float(out.get("score", 0.0))
        # Normalizamos 0–100
        if "pos" in label:   return {"emocion": "esperanza", "modelo": int(50 + score*50)}
        if "neg" in label:   return {"emocion": "miedo",     "modelo": int(50 + score*50)}
        if "neu" in label:   return {"emocion": "neutral",   "modelo": int(score*50)}
        return {"emocion": "shock", "modelo": int(40 + score*60)}
    except Exception:
        return None

def _lexicon_score(text: str) -> tuple[str,int]:
    """Retorna (emocion_dominante, score_lexicon 0–100)."""
    t = text.lower()
    scores = {emo:0 for emo in EMO_LEX}
    for emo, bag in EMO_LEX.items():
        for w, wgt in bag.items():
            scores[emo] += wgt * len(re.findall(rf"\b{re.escape(w)}\b", t))
    if sum(scores.values()) == 0:
        return "neutral", 0
    emo_dom = max(scores, key=scores.get)
    # Escala simple a 0–100
    total = sum(scores.values())
    scaled = max(10, min(100, 40 + scores[emo_dom]*10)) if total>0 else 0
    return emo_dom, scaled

def _categorize(text: str) -> list[str]:
    t = text.lower()
    cats = []
    for name, pat in CATEGORY_PATTERNS.items():
        if re.search(pat, t, flags=re.IGNORECASE):
            cats.append(name)
    return cats

def _final_score(lex: int, model: int | None) -> int:
    if model is None:
        return lex
    # mezcla conservadora: 60% modelo, 40% lexicón
    return int(round(0.6*model + 0.4*lex))

def _motivo_inclusion(fin: int, umbral: int, alto_hit: bool) -> str:
    if fin >= umbral and alto_hit:
        return f"Incluida: emoción={fin}≥{umbral} + alto impacto"
    if fin >= umbral:
        return f"Incluida: emoción={fin}≥{umbral}"
    if alto_hit:
        return f"Incluida: alto impacto (emocion={fin}<{umbral})"
    return f"Excluida: emoción={fin}<{umbral} sin alto impacto"

def _high_impact_hit(text: str, palabras: list[str]) -> bool:
    t = text.lower()
    return any(re.search(rf"\b{re.escape(w)}\b", t) for w in palabras)

def _gen_id(prefix="N") -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    base = f"{prefix}-{today}"
    df = _load_news(NEWS_CSV)
    n = sum(df["id_noticia"].astype(str).str.startswith(base)) + 1
    return f"{base}-{n:03d}"

# ================== NewsAPI (opcional) ==================
def _newsapi_key() -> str | None:
    try:
        return st.secrets["newsapi"]["api_key"]
    except Exception:
        return None

def _default_query() -> str:
    # Consulta amplia por alto impacto emocional (en español)
    return (
        "huracán OR tormenta OR tornado OR inundación OR terremoto OR incendio OR evacuación OR emergencia "
        "OR tiroteo OR ataque OR explosión OR guerra OR conflicto OR terrorismo OR tragedia OR muertos OR fallecidos "
        "OR crisis OR colapso OR apagón OR quiebra OR récord OR histórico"
    )

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

def _auto_harvest_if_needed():
    """Ejecuta 1 vez/día y garantiza volumen mínimo (60) si hay API."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    last = STAMP.read_text().strip() if STAMP.exists() else ""
    df_current = _load_news(NEWS_CSV)

    # Ejecutar una vez al día
    if last != today and _newsapi_key():
        extra = _fetch_news_newsapi(_default_query(), page_size=50)
        if not extra.empty:
            merged = pd.concat([df_current, extra], ignore_index=True)
            if "url" in merged.columns:
                merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
            _save_news(merged)
            df_current = merged
            st.toast("📰 Acopio diario ejecutado (NewsAPI).", icon="🕘")
        STAMP.write_text(today)

    # Garantizar mínimo 60 crudas (intenta ampliar si hay API)
    if len(df_current) < 60 and _newsapi_key():
        extra = _fetch_news_newsapi(_default_query(), page_size=100)
        if not extra.empty:
            merged = pd.concat([df_current, extra], ignore_index=True)
            if "url" in merged.columns:
                merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
            _save_news(merged)
            st.toast(f"🔎 Ampliado automáticamente: {len(merged)} filas.", icon="➕")

# ================== UI: Secciones ==================
def _ui_crudas(df: pd.DataFrame):
    st.subheader("🗞️ Noticias crudas (primarias)")
    st.caption("Lista sin filtro. Ordenadas por fecha descendente. Todo se visualiza dentro de la app.")
    dff = df.sort_values(["fecha", "fuente", "titular"], ascending=[False, True, True]).reset_index(drop=True)
    if dff.empty:
        st.info("No hay noticias crudas para mostrar.")
        return dff
    for i in range(min(len(dff), 200)):
        r = dff.iloc[i]
        titulo = (r["titular"] or "—").strip()
        with st.expander(f"📰 {r['fecha']} · {r['fuente'] or '—'} · {titulo[:100]}"):
            st.write(r["resumen"] or "—")
            st.caption(f"Etiquetas: `{r['etiquetas']}` · País: {r['pais'] or '—'} · Sorteo: {r['sorteo'] or '—'}")
            if r.get("url") and r["url"]:
                st.markdown(f"[🔗 Ver fuente (opcional)]({r['url']})")
    return dff

def _ui_filtradas(df: pd.DataFrame):
    st.subheader("🔥 Noticias filtradas (alto impacto)")
    colU, colW, colX = st.columns([1, 1, 1])
    with colU:
        umbral = st.slider("Umbral emoción final", 0, 100, UMBRAL_DEFECTO)
    with colW:
        alto = st.multiselect(
            "Palabras de alto impacto (ajustables)",
            PALABRAS_ALTO_IMPACTO_DEFAULT,
            default=PALABRAS_ALTO_IMPACTO_DEFAULT[:10]
        )
    with colX:
        st.caption("Las categorías detectadas se muestran por noticia.")

    if df.empty:
        st.info("No hay noticias para filtrar.")
        return pd.DataFrame()

    # Calcular emoción + categorías + motivo
    enriched = []
    for _, r in df.iterrows():
        text = f"{r.get('titular','')} {r.get('resumen','')}"
        emo_lex, score_lex = _lexicon_score(text)
        nlp = _nlp_backend(text)
        score_model = nlp["modelo"] if nlp else None
        final = _final_score(score_lex, score_model)
        cats = _categorize(text)
        hit = _high_impact_hit(text, alto)
        motivo = _motivo_inclusion(final, umbral, hit)
        enriched.append({
            **r.to_dict(),
            "emocion_dominante": emo_lex if not (nlp and nlp.get("emocion")) else nlp["emocion"],
            "nivel_emocional_lexicon": score_lex,
            "nivel_emocional_modelo": (score_model if score_model is not None else ""),
            "nivel_emocional_final": final,
            "categorias_emocionales": ";".join(sorted(set(cats))) if cats else "",
            "motivo_filtrado": motivo,
            "es_alto_impacto": motivo.startswith("Incluida"),
        })

    dff = pd.DataFrame(enriched)
    ok = dff[dff["es_alto_impacto"] == True].copy()  # noqa: E712
    ok = ok.sort_values(["fecha","fuente","titular"], ascending=[False, True, True])
    st.caption(f"Seleccionadas: **{len(ok)}** / {len(dff)}")
    if ok.empty:
        st.info("Ninguna supera el criterio actual.")
        return ok

    for i in range(min(len(ok), 120)):
        r = ok.iloc[i]
        titulo = (str(r.get("titular","")) or "—").strip()
        with st.expander(f"✅ {r['fecha']} · {r.get('fuente','—')} · {titulo[:100]}"):
            st.write(r.get("resumen","") or "—")
            st.write(f"**Motivo:** {r.get('motivo_filtrado','')}")
            st.caption(
                f"Emoción (lex/model/final): {r.get('nivel_emocional_lexicon','')}/"
                f"{r.get('nivel_emocional_modelo','')}/{r.get('nivel_emocional_final','')}"
            )
            st.caption(f"Categorías: `{r.get('categorias_emocionales','') or '—'}`")
            if r.get("url"):
                st.markdown(f"[🔗 Ver fuente (opcional)]({r['url']})")
    return ok

def _ui_procesar():
    st.subheader("⚙️ Procesar / Analizar noticias (in-app)")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔤 Abrir Gematría", use_container_width=True):
            st.session_state["_nav"] = "🔡 Gematría"; st.rerun()
    with c2:
        if st.button("🌀 Abrir Subliminal", use_container_width=True):
            st.session_state["_nav"] = "🌀 Análisis subliminal"; st.rerun()
    st.caption("Sugerencia: pasa a análisis solo las noticias filtradas (alto impacto).")

def _ui_explorador(df: pd.DataFrame):
    st.subheader("🔎 Explorador / Ingreso")
    st.caption("Trae más noticias (NewsAPI) o agrega manualmente. Todo se queda dentro de la app.")
    q = st.text_input("Consulta (amplia)", _default_query())
    n = st.slider("Cantidad a traer (NewsAPI)", 20, 100, 50, step=10)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌐 Traer con NewsAPI", use_container_width=True, disabled=_newsapi_key() is None):
            extra = _fetch_news_newsapi(q, page_size=int(n))
            if extra.empty:
                st.warning("No se trajo nada (revisa API key o consulta).")
            else:
                merged = pd.concat([df, extra], ignore_index=True)
                if "url" in merged.columns:
                    merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
                _save_news(merged); st.success(f"+{len(merged)-len(df)} noticias nuevas."); st.rerun()
    with c2:
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
        fuente = st.text_input("Fuente (ej. Reuters)")
        titular = st.text_input("Titular")
        resumen = st.text_area("Resumen", height=120)
        url = st.text_input("URL (opcional)")
        sorteo = st.text_input("Sorteo (opcional)", "")
        pais = st.text_input("País", "US")
        etiquetas = st.text_input("Etiquetas separadas por ;", "manual;ingreso")
        submitted = st.form_submit_button("➕ Agregar")
    if submitted:
        if not titular.strip():
            st.error("El titular es obligatorio.")
        else:
            df2 = df.copy()
            new_row = {
                "id_noticia": _gen_id("N"),
                "fecha": (fecha.isoformat() if fecha else datetime.utcnow().strftime("%Y-%m-%d")),
                "sorteo": sorteo.strip(), "pais": pais.strip(), "fuente": fuente.strip(),
                "titular": titular.strip(), "resumen": resumen.strip(), "etiquetas": etiquetas.strip(),
                "nivel_emocional_diccionario": "", "nivel_emocional_modelo": "", "nivel_emocional_final": "",
                "noticia_relevante": "", "categorias_t70_ref": "", "url": url.strip(),
            }
            df2 = pd.concat([df2, pd.DataFrame([new_row])], ignore_index=True)
            _save_news(df2); st.success("Noticia agregada."); st.rerun()

    st.markdown("### ⬆️ Cargar CSV adicional")
    up = st.file_uploader("Subir CSV con mismas columnas de noticias.csv", type=["csv"])
    if up is not None:
        try:
            extra = pd.read_csv(up, dtype=str, encoding="utf-8").fillna("")
            for c in REQUIRED_COLS:
                if c not in extra.columns: extra[c] = ""
            merged = pd.concat([df, extra[REQUIRED_COLS]], ignore_index=True)
            if "url" in merged.columns:
                merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
            _save_news(merged); st.success(f"Se agregaron {len(merged)-len(df)} filas."); st.rerun()
        except Exception as e:
            st.error(f"No pude leer el CSV subido: {e}")

def _ui_limpiar(df: pd.DataFrame):
    st.subheader("🧹 Limpiar residuos / duplicados")
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
        try: dff = dff[dff["titular"].str.contains(regex, flags=re.IGNORECASE, na=False, regex=True)]
        except Exception as e: st.warning(f"Regex inválida: {e}")
    st.caption(f"Candidatas: {len(dff)}")
    ids = st.multiselect("Selecciona id_noticia a eliminar", options=dff["id_noticia"].tolist())
    colD1, colD2 = st.columns(2)
    with colD1:
        if st.button("🗑️ Eliminar seleccionadas", use_container_width=True, disabled=not ids):
            cleaned = df[~df["id_noticia"].isin(ids)].reset_index(drop=True)
            _save_news(cleaned); st.success(f"Eliminadas {len(ids)} filas."); st.rerun()
    with colD2:
        st.download_button(
            "⬇️ Descargar copia limpia (CSV)",
            (df[~df["id_noticia"].isin(ids)]).to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_limpio_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv", use_container_width=True,
        )

def _ui_archivo(df: pd.DataFrame):
    st.subheader("🗂️ Archivo / Historial")
    if df.empty:
        st.info("Sin historial aún."); return
    c1, c2 = st.columns(2)
    fechas = ["(todas)"] + sorted(df["fecha"].unique())
    sorteos = ["(todos)"] + sorted(df["sorteo"].unique())
    fs = c1.selectbox("Fecha", options=fechas); ss = c2.selectbox("Sorteo", options=sorteos)
    dff = df.copy()
    if fs != "(todas)": dff = dff[dff["fecha"] == fs]
    if ss != "(todos)": dff = dff[dff["sorteo"] == ss]
    st.dataframe(dff.sort_values(["fecha","fuente","titular"], ascending=[False, True, True]),
                 use_container_width=True, hide_index=True)

# ================== Vista principal ==================
def render_noticias():
    """Módulo de Noticias (in-app): crudas, filtradas, procesar, explorador, limpiar, archivo."""
    # 1) Acopio diario y volumen mínimo (si hay NewsAPI)
    _auto_harvest_if_needed()
# === Contadores visibles
cA, cB = st.columns(2)
with cA:
    st.metric("📰 Crudas (primarias)", len(df_cruda))
with cB:
    st.metric("✅ Filtradas (alto impacto)", len(df_filtrada))
    # ================= Acciones finales sobre noticias =================
st.markdown("----")
st.subheader("⚙️ Acciones sobre la selección")

# Intentamos usar los DF que ya calculaste arriba;
# si no existen, creamos vacíos para no romper la app.
try:
    df_cruda  # noqa: F821
except NameError:
    df_cruda = pd.DataFrame()

try:
    df_filtrada  # noqa: F821
except NameError:
    df_filtrada = pd.DataFrame()

# ¿Qué conjunto quieres analizar?
base_set = st.radio(
    "Conjunto a procesar:",
    ["Filtrada (recomendada)", "Cruda (primaria)"],
    horizontal=True,
)
df_target = df_filtrada if base_set.startswith("Filtrada") else df_cruda

# Selección de noticias a enviar
titulos = list(df_target.get("titular", pd.Series(dtype=str)))
seleccion = st.multiselect(
    "Selecciona hasta 10 noticias para analizar:",
    titulos,
    max_selections=10,
)

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    analizador = st.selectbox("Analizador", ["Gematría", "Subliminal"])
with c2:
    lanzar = st.button("▶️ Procesar selección", use_container_width=True)
with c3:
    st.caption("No recarga la página; sólo marca en memoria lo que procesarás.")

if lanzar:
    st.session_state["to_analyze"] = {
        "analizador": analizador,
        "items": seleccion,
        "conjunto": "filtrada" if base_set.startswith("Filtrada") else "cruda",
    }
    st.success(
        f"Se enviaron {len(seleccion)} ítems a **{analizador}**. "
        "Abre el módulo correspondiente para ver/validar resultados."
    )

# ===== Descargas (unificadas) =====
st.markdown("### ⬇️ Exportar vistas")
d1, d2 = st.columns(2)
with d1:
    st.download_button(
        "Descargar vista cruda (CSV)",
        df_cruda.to_csv(index=False).encode("utf-8"),
        file_name="news_raw.csv",
        mime="text/csv",
        disabled=df_cruda.empty,
        use_container_width=True,
    )
with d2:
    st.download_button(
        "Descargar vista filtrada (CSV)",
        df_filtrada.to_csv(index=False).encode("utf-8"),
        file_name="news_filtered.csv",
        mime="text/csv",
        disabled=df_filtrada.empty,
        use_container_width=True,
    )
# ==================================================================
    # 2) Carga base
    df_all = _load_news(NEWS_CSV)

    # 3) Filtros globales (no dependen de lotería)
    colf1, colf2, colf3 = st.columns([1,1,2])
    fechas = ["(todas)"] + 
    
