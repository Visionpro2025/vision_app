# modules/noticias_module.py — Noticias PRO (filtro emocional + mini-menú in-app)
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta, date
import pandas as pd
import streamlit as st
import requests
import re

# ================== Rutas base ==================
ROOT = Path(__file__).resolve().parent.parent
NEWS_CSV = ROOT / "noticias.csv"
RUNS_NEWS = ROOT / "__RUNS" / "NEWS"
RUNS_NEWS.mkdir(parents=True, exist_ok=True)
STAMP = RUNS_NEWS / "last_fetch_UTC.txt"   # marca diario (YYYY-MM-DD)

# ================== Columnas y config ==================
REQUIRED_COLS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen",
    "etiquetas","nivel_emocional_diccionario","nivel_emocional_modelo",
    "nivel_emocional_final","noticia_relevante","categorias_t70_ref","url"
]
UMBRAL_DEFECTO = 60

PALABRAS_ALTO_IMPACTO_DEFAULT = [
    "mortal","muertes","fallecidos","tragedia","desastre","emergencia","crisis",
    "huracán","tormenta","tornado","inundación","terremoto","incendio","evacuación",
    "tiroteo","ataque","explosión","guerra","conflicto","terrorismo",
    "récord","histórico","masivo","colapso","apagón","quiebra","pánico",
]

EMO_LEX = {
    "miedo":     {"crisis":3,"amenaza":3,"pánico":3,"temor":2,"colapso":3,"alarma":3,"emergencia":3,"evacuación":3,"huracán":3,"tormenta":3,"tornado":3,"inundación":3,"terremoto":3,"incendio":3,"apagón":2},
    "tristeza":  {"tragedia":3,"pérdida":2,"luto":2,"derrota":2,"accidente":2,"fallecidos":3,"muertes":3,"víctimas":3,"desaparición":2},
    "ira":       {"golpe":2,"ataque":3,"violencia":3,"furia":2,"rabia":2,"corrupción":3,"abuso":3,"indignación":3,"fraude":3,"escándalo":3},
    "esperanza": {"récord":2,"histórico":2,"avance":2,"renace":2,"mejora":2,"ayuda":2,"rescate":3,"solidaridad":2,"reconstrucción":2},
    "euforia":   {"éxito":2,"victoria":2,"celebra":2,"triunfo":2,"récord":2,"histórico":2,"campeón":2},
    "shock":     {"explosión":3,"derrumbe":3,"catastrófico":3,"devastador":3,"colapso":3},
}

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

# ================== Helpers base ==================
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

def _gen_id(prefix="N") -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    base = f"{prefix}-{today}"
    df = _load_news(NEWS_CSV)
    n = sum(df["id_noticia"].astype(str).str.startswith(base)) + 1
    return f"{base}-{n:03d}"

def _newsapi_key() -> str | None:
    try:
        return st.secrets["newsapi"]["api_key"]
    except Exception:
        return None
    def _default_queries() -> list[str]:
    # Temas de alto impacto (en / es) — centrados en USA
    return [
        # desastres naturales / clima severo
        "hurricane OR tropical storm OR wildfire OR earthquake OR flood OR tornado OR heatwave",
        "huracán OR tormenta tropical OR incendio forestal OR terremoto OR inundación OR tornado OR ola de calor",
        # violencia / seguridad
        "mass shooting OR explosion OR terror attack OR active shooter",
        "tiroteo masivo OR explosión OR ataque terrorista OR atentado",
        # crisis públicas / fallas críticas
        "blackout OR grid failure OR cyberattack OR data breach OR chemical spill",
        "apagón OR fallo eléctrico OR ciberataque OR brecha de datos OR derrame químico",
        # economía / colapsos
        "recession OR bankruptcy OR market crash OR bank failure",
        "recesión OR quiebra OR colapso bursátil OR cierre bancario",
        # récords / eventos “históricos”
        "record high OR historic OR unprecedented",
        "récord histórico OR sin precedentes",
    ]

# ====== NLP / Lexicón ======
def _nlp_backend(text: str) -> dict | None:
    try:
        from transformers import pipeline  # opcional
        clf = pipeline("sentiment-analysis")
        out = clf(text[:512])[0]
        label = str(out.get("label","")).lower()
        score = float(out.get("score", 0.0))
        if "pos" in label:   return {"emocion": "esperanza", "modelo": int(50 + score*50)}
        if "neg" in label:   return {"emocion": "miedo",     "modelo": int(50 + score*50)}
        if "neu" in label:   return {"emocion": "neutral",   "modelo": int(score*50)}
        return {"emocion": "shock", "modelo": int(40 + score*60)}
    except Exception:
        return None

def _lexicon_score(text: str) -> tuple[str,int]:
    t = text.lower()
    scores = {emo:0 for emo in EMO_LEX}
    for emo, bag in EMO_LEX.items():
        for w, wgt in bag.items():
            scores[emo] += wgt * len(re.findall(rf"\b{re.escape(w)}\b", t))
    if sum(scores.values()) == 0:
        return "neutral", 0
    emo_dom = max(scores, key=scores.get)
    scaled = max(10, min(100, 40 + scores[emo_dom]*10))
    return emo_dom, scaled

def _final_score(lex: int, model: int | None) -> int:
    if model is None:
        return lex
    return int(round(0.6*model + 0.4*lex))

def _categorize(text: str) -> list[str]:
    t = text.lower()
    cats = []
    for name, pat in CATEGORY_PATTERNS.items():
        if re.search(pat, t, flags=re.IGNORECASE):
            cats.append(name)
    return cats

def _high_impact_hit(text: str, palabras: list[str]) -> bool:
    t = text.lower()
    return any(re.search(rf"\b{re.escape(w)}\b", t) for w in palabras)

def _motivo_inclusion(fin: int, umbral: int, alto_hit: bool) -> str:
    if fin >= umbral and alto_hit:
        return f"Incluida: emoción={fin}≥{umbral} + alto impacto"
    if fin >= umbral:
        return f"Incluida: emoción={fin}≥{umbral}"
    if alto_hit:
        return f"Incluida: alto impacto (emocion={fin}<{umbral})"
    return f"Excluida: emoción={fin}<{umbral} sin alto impacto"

# ================== NewsAPI ==================
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
            "pais": "US",
            "fuente": raw.get("source","").apply(lambda s: (s or {}).get("name","")) if "source" in raw.columns else "",
            "titular": raw.get("title",""),
            "resumen": raw.get("description",""),
            "etiquetas": "newsapi",
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
    today = datetime.utcnow().strftime("%Y-%m-%d")
    last = STAMP.read_text().strip() if STAMP.exists() else ""
    df_current = _load_news(NEWS_CSV)

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

    if len(df_current) < 60 and _newsapi_key():
        extra = _fetch_news_newsapi(_default_query(), page_size=100)
        if not extra.empty:
            merged = pd.concat([df_current, extra], ignore_index=True)
            if "url" in merged.columns:
                merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
            _save_news(merged)
            st.toast(f"🔎 Ampliado automáticamente: {len(merged)} filas.", icon="➕")

# ================== UI: listas ==================
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

# ================== Vista principal ==================
def render_noticias():
    """Módulo de Noticias (in-app): crudas, filtradas, procesar, explorador, limpiar, archivo."""
    _auto_harvest_if_needed()

    # 1) Carga base
    df_all = _load_news(NEWS_CSV)

    # 2) Filtros globales
    colf1, colf2, colf3 = st.columns([1, 1, 2])
    fechas = ["(todas)"] + sorted([f for f in df_all.get("fecha", pd.Series(dtype=str)).unique() if str(f).strip()])
    sorteos = ["(todos)"] + sorted([s for s in df_all.get("sorteo", pd.Series(dtype=str)).unique() if str(s).strip()])
    fsel = colf1.selectbox("Fecha", options=fechas, index=0)
    ssel = colf2.selectbox("Sorteo (opcional)", options=sorteos, index=0)
    q = colf3.text_input("Buscar (titular/resumen/etiquetas)")

    base = df_all.copy()
    if fsel != "(todas)": base = base[base["fecha"].astype(str) == fsel]
    if ssel != "(todos)": base = base[base["sorteo"].astype(str) == ssel]
    if q.strip():
        qn = q.lower().strip()
        base = base[
            base["titular"].astype(str).str.lower().str.contains(qn, na=False) |
            base["resumen"].astype(str).str.lower().str.contains(qn, na=False) |
            base["etiquetas"].astype(str).str.lower().str.contains(qn, na=False)
        ]

    st.info(f"Noticias tras filtros: **{len(base)}**")
    st.markdown("---")

    # 3) Métricas
    colM1, colM2 = st.columns(2)
    with colM1: st.metric("📰 Crudas (primarias)", len(base))
    with colM2: st.metric("⏱️ Última carga", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))

    # 4) Mini-menú
    b1, b2, b3, b4, b5 = st.columns(5)
    show_crudas     = b1.button("🗞️ Primarias",             use_container_width=True)
    show_filtradas  = b2.button("🔥 Filtradas (impacto)",   use_container_width=True)
    show_proc       = b3.button("⚙️ Procesar/Analizar",
    use_container_width=True)
    show_expl       = b4.button("🔎 Explorador / Ingreso",  use_container_width=True)
    show_clean      = b5.button("🧹 Limpiar",               use_container_width=True)

    if len(base) < 60 and _newsapi_key():
        st.warning(f"Menos de 60 crudas ({len(base)}). Usa **Explorador** para ampliar.")

    # 5) Render condicional
    if show_crudas:    _ui_crudas(base);     st.markdown("---")
    if show_filtradas: _ui_filtradas(base);  st.markdown("---")
    if show_proc:      _ui_procesar();       st.markdown("---")
    if show_expl:      _ui_explorador(df_all); st.markdown("---")
    if show_clean:     _ui_limpiar(df_all);  st.markdown("---")

    # 6) Descargas rápidas
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
        
