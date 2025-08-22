# modules/noticias_module.py
# ---------------------------------------------------------------------
# Noticias — Filtro emocional PRO (robusto y autosuficiente)
# Funciona aunque faltan dependencias externas (usa fallbacks).
# ---------------------------------------------------------------------
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta
import os, re
import pandas as pd
import streamlit as st

# Dependencias opcionales (no obligatorias)
try:
    import feedparser  # RSS
except Exception:
    feedparser = None

try:
    import requests  # NewsAPI
except Exception:
    requests = None

# ================== PARTE 0 — Constantes, rutas y helpers base ==================

# Columnas esperadas en noticias/cola/papelera (orden canónico)
REQUIRED_COLS = [
    "id_noticia", "fecha", "sorteo", "pais", "fuente",
    "titular", "resumen", "etiquetas",
    "nivel_emocional_diccionario", "nivel_emocional_modelo",
    "nivel_emocional_final", "noticia_relevante",
    "categorias_t70_ref", "url",
]

# Rutas base (el módulo vive en vision_app/modules/)
ROOT = Path(__file__).resolve().parent.parent
RUNS_NEWS = ROOT / "__RUNS" / "NEWS"
RUNS_NEWS.mkdir(parents=True, exist_ok=True)
NEWS_CSV = ROOT / "noticias.csv"

@st.cache_data(show_spinner=False)
def _load_news(path: Path) -> pd.DataFrame:
    """Carga CSV de noticias y asegura columnas/orden."""
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception:
        df = pd.DataFrame()
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[REQUIRED_COLS].fillna("")

def _save_news(df: pd.DataFrame) -> None:
    """Guarda noticias y limpia caché."""
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    df[REQUIRED_COLS].to_csv(NEWS_CSV, index=False, encoding="utf-8")
    _load_news.clear()

def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

# ================== PARTE 1 — Router, backup, papelera, cola, pegado ==================

# ---- Router/Navegación (persistente) ----
NAV_KEY = "_nav"
NAV_LABELS = {
    "noticias_crudas":   ["🗞️ Crudas", "Crudas"],
    "noticias_filtradas":["🔥 Filtradas", "Filtradas"],
    "noticias_procesar": ["⚙️ Procesar", "Procesar"],
    "noticias_explorar": ["🔎 Explorador / Ingreso", "Explorador", "Ingreso"],
    "noticias_papelera": ["🗑️ Papelera", "Papelera"],
    "noticias_limpiar":  ["🧹 Limpiar", "Limpiar"],
    "gematria":          ["🔡 Gematría", "Gematría", "Gematria"],
    "subliminal":        ["🌀 Subliminal", "Análisis subliminal"],
}

def _router_go(target_key: str):
    labels = NAV_LABELS.get(target_key, [target_key])
    target = labels[0]
    # Redundancia amistosa
    st.session_state[NAV_KEY] = target
    st.session_state["nav"] = target
    st.session_state["page"] = target
    st.rerun()

# ---- Generador de IDs robusto ----
def _gen_id(prefix: str = "N") -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    base = f"{prefix}-{today}"
    try:
        df = _load_news(NEWS_CSV)
    except Exception:
        df = pd.DataFrame()
    serie = df.get("id_noticia", pd.Series([], dtype=str)).astype(str)
    n = int(serie.str.startswith(base).sum()) + 1
    return f"{base}-{n:03d}"

# ---- Backup explícito ----
def _backup_now(df: pd.DataFrame) -> Path:
    RUNS_NEWS.mkdir(parents=True, exist_ok=True)
    bpath = RUNS_NEWS / f"backup_noticias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv"
    df.to_csv(bpath, index=False, encoding="utf-8")
    return bpath

# ---- Papelera ----
TRASH_CSV = RUNS_NEWS / ".trash.csv"

def _load_trash() -> pd.DataFrame:
    try:
        tdf = pd.read_csv(TRASH_CSV, dtype=str, encoding="utf-8").fillna("") if _exists(TRASH_CSV) else pd.DataFrame()
    except Exception:
        tdf = pd.DataFrame()
    for c in REQUIRED_COLS:
        if c not in tdf.columns:
            tdf[c] = ""
    return tdf[REQUIRED_COLS]

def _move_to_trash(df: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    if not ids:
        return df
    sel = df[df["id_noticia"].isin(ids)].copy()
    if sel.empty:
        return df
    trash = _load_trash()
    new_trash = pd.concat([trash, sel], ignore_index=True)
    new_trash = new_trash.drop_duplicates(subset=["id_noticia"], keep="last").reset_index(drop=True)
    new_trash.to_csv(TRASH_CSV, index=False, encoding="utf-8")
    cleaned = df[~df["id_noticia"].isin(ids)].reset_index(drop=True)
    _save_news(cleaned)
    return cleaned

def _restore_from_trash(ids: list[str]) -> None:
    if not ids:
        return
    trash = _load_trash()
    sel = trash[trash["id_noticia"].isin(ids)].copy()
    if sel.empty:
        return
    base = _load_news(NEWS_CSV)
    merged = pd.concat([base, sel], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url", "id_noticia"], keep="first").reset_index(drop=True)
    _save_news(merged)
    remain = trash[~trash["id_noticia"].isin(ids)].reset_index(drop=True)
    remain.to_csv(TRASH_CSV, index=False, encoding="utf-8")

def _purge_trash() -> None:
    pd.DataFrame(columns=REQUIRED_COLS).to_csv(TRASH_CSV, index=False, encoding="utf-8")

def _ui_papelera():
    st.subheader("🗑️ Papelera de noticias")
    tdf = _load_trash()
    if tdf.empty:
        st.info("La papelera está vacía.")
        return
    view = tdf.sort_values(["fecha", "fuente", "titular"], ascending=[False, True, True]).reset_index(drop=True)
    st.caption(f"En papelera: **{len(view)}**")
    ids = st.multiselect("Selecciona id_noticia para actuar", options=view["id_noticia"].tolist())
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("♻️ Restaurar seleccionadas", use_container_width=True, disabled=not ids):
            _restore_from_trash(ids); st.success(f"Restauradas {len(ids)}."); st.rerun()
    with c2:
        if st.button("🧹 Vaciar papelera", use_container_width=True):
            _purge_trash(); st.success("Papelera vaciada."); st.rerun()
    with c3:
        st.download_button(
            "⬇️ Exportar papelera (CSV)",
            view.to_csv(index=False).encode("utf-8"),
            file_name=f"papelera_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ---- Cola de procesamiento ----
QUEUE_CSV = RUNS_NEWS / "queue_to_process.csv"

def _queue_list() -> pd.DataFrame:
    try:
        if _exists(QUEUE_CSV):
            qdf = pd.read_csv(QUEUE_CSV, dtype=str, encoding="utf-8").fillna("")
        else:
            qdf = pd.DataFrame(columns=REQUIRED_COLS)
    except Exception:
        qdf = pd.DataFrame(columns=REQUIRED_COLS)
    for c in REQUIRED_COLS:
        if c not in qdf.columns:
            qdf[c] = ""
    return qdf[REQUIRED_COLS]

def _queue_add(rows: pd.DataFrame | list[dict]) -> None:
    base = _queue_list()
    add = pd.DataFrame(rows) if isinstance(rows, list) else rows.copy()
    for c in REQUIRED_COLS:
        if c not in add.columns:
            add[c] = ""
    merged = pd.concat([base, add[REQUIRED_COLS]], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url", "id_noticia"], keep="first")
    merged.to_csv(QUEUE_CSV, index=False, encoding="utf-8")

def _queue_clear() -> None:
    pd.DataFrame(columns=REQUIRED_COLS).to_csv(QUEUE_CSV, index=False, encoding="utf-8")

def _ui_queue():
    st.subheader("📥 Cola de procesamiento (Gematría / Subliminal)")
    qdf = _queue_list()
    st.caption(f"En cola: **{len(qdf)}**")
    if qdf.empty:
        st.info("No hay elementos en la cola.")
        return
    show = qdf[["id_noticia", "fecha", "fuente", "titular", "url"]].reset_index(drop=True)
    st.dataframe(show, use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔤 Ir a Gematría", use_container_width=True):
            _router_go("gematria")
    with c2:
        if st.button("🌀 Ir a Subliminal", use_container_width=True):
            _router_go("subliminal")
    with c3:
        if st.button("🗑️ Vaciar cola", use_container_width=True):
            _queue_clear(); st.success("Cola vaciada."); st.rerun()

# ---- Enumerador para vistas ordenadas ----
def _enumerate_df(df: pd.DataFrame) -> pd.DataFrame:
    dff = df.reset_index(drop=True).copy()
    dff.insert(0, "#", range(1, len(dff) + 1))
    return dff

# ---- Pegado manual ----
def _manual_paste_parse(raw_text: str) -> pd.DataFrame:
    rows = []
    for line in (raw_text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        tit, res, fue, url = "", "", "", ""
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 1: tit = parts[0]
            if len(parts) >= 2: res = parts[1]
            if len(parts) >= 3: fue = parts[2]
            if len(parts) >= 4: url = parts[3]
        elif " — " in line:
            parts = [p.strip() for p in line.split(" — ", 1)]
            tit = parts[0]; res = parts[1] if len(parts) > 1 else ""
        else:
            if line.startswith("http"):
                url = line
                tit = "Noticia (manual)"
        rows.append({
            "id_noticia": _gen_id("N"),
            "fecha": datetime.utcnow().strftime("%Y-%m-%d"),
            "sorteo": "", "pais": "US", "fuente": fue or "manual",
            "titular": tit, "resumen": res, "etiquetas": "manual;ingreso",
            "nivel_emocional_diccionario": "", "nivel_emocional_modelo": "",
            "nivel_emocional_final": "", "noticia_relevante": "",
            "categorias_t70_ref": "", "url": url,
        })
    return pd.DataFrame(rows).fillna("")

def _ingest_manual(rows: pd.DataFrame, destino: str = "crudas"):
    if rows is None or rows.empty:
        st.warning("No hay entradas válidas para ingresar.")
        return
    for c in REQUIRED_COLS:
        if c not in rows.columns:
            rows[c] = ""
    if destino == "cola":
        _queue_add(rows[REQUIRED_COLS])
        st.success(f"Agregadas {len(rows)} a la cola.")
    else:
        base = _load_news(NEWS_CSV)
        merged = pd.concat([base, rows[REQUIRED_COLS]], ignore_index=True)
        if "url" in merged.columns:
            merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
        _save_news(merged)
        st.success(f"Agregadas {len(merged) - len(base)} noticias al acopio.")

# ================== PARTE 2 — Recolección + barra de herramientas ==================

# Consultas por defecto
DEFAULT_QUERIES = [
    "lotería OR loteria OR lottery OR powerball OR megamillions",
    "inteligencia artificial OR IA OR AI",
    "economía OR economía global OR inflation OR inflación",
]

def _default_queries() -> list[str]:
    return DEFAULT_QUERIES

def _default_query() -> str:
    return DEFAULT_QUERIES[0]

def _newsapi_key() -> str | None:
    key = os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")
    return key.strip() if key else None

def _df_norm(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows).fillna("")
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[REQUIRED_COLS]

def _fetch_news_rss_google(query: str, max_items: int = 50, days: int = 1) -> pd.DataFrame:
    """Trae desde Google News RSS. Si no hay feedparser, retorna vacío."""
    if feedparser is None:
        return pd.DataFrame(columns=REQUIRED_COLS)
    q = query.replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={q}&hl=es-419&gl=US&ceid=US:es-419"
    try:
        feed = feedparser.parse(url)
    except Exception:
        return pd.DataFrame(columns=REQUIRED_COLS)
    cutoff = datetime.utcnow() - timedelta(days=int(days))
    rows = []
    for e in feed.entries[:max_items]:
        published = None
        if hasattr(e, "published_parsed") and e.published_parsed:
            published = datetime(*e.published_parsed[:6])
        fecha = (published or datetime.utcnow()).strftime("%Y-%m-%d")
        if published and published < cutoff:
            continue
        rows.append({
            "id_noticia": _gen_id("N"),
            "fecha": fecha,
            "sorteo": "", "pais": "US", "fuente": getattr(e, "source", {}).get("title", "rss") if hasattr(e, "source") else "rss",
            "titular": getattr(e, "title", ""),
            "resumen": re.sub(r"<.*?>", "", getattr(e, "summary", "")),
            "etiquetas": "rss",
            "nivel_emocional_diccionario": "", "nivel_emocional_modelo": "",
            "nivel_emocional_final": "", "noticia_relevante": "",
            "categorias_t70_ref": "",
            "url": getattr(e, "link", ""),
        })
    return _df_norm(rows)

def _fetch_news_newsapi(query: str, page_size: int = 50, pages: int = 1) -> pd.DataFrame:
    """Trae desde NewsAPI si hay clave y requests; si no, vacío."""
    key = _newsapi_key()
    if not key or requests is None:
        return pd.DataFrame(columns=REQUIRED_COLS)
    rows = []
    url = "https://newsapi.org/v2/everything"
    headers = {"X-Api-Key": key}
    for page in range(1, int(pages) + 1):
        try:
            r = requests.get(url, params={"q": query, "pageSize": int(page_size), "page": page, "language": "es"}, headers=headers, timeout=12)
            if r.status_code != 200:
                break
            data = r.json()
        except Exception:
            break
        arts = data.get("articles") or []
        for a in arts:
            fecha = (a.get("publishedAt") or "")[:10] or datetime.utcnow().strftime("%Y-%m-%d")
            rows.append({
                "id_noticia": _gen_id("N"),
                "fecha": fecha,
                "sorteo": "", "pais": (a.get("source") or {}).get("name", "")[:2].upper() or "US",
                "fuente": (a.get("source") or {}).get("name", "newsapi"),
                "titular": a.get("title", "") or "",
                "resumen": a.get("description", "") or "",
                "etiquetas": "newsapi",
                "nivel_emocional_diccionario": "", "nivel_emocional_modelo": "",
                "nivel_emocional_final": "", "noticia_relevante": "",
                "categorias_t70_ref": "",
                "url": a.get("url", "") or "",
            })
    return _df_norm(rows)

def _fetch_emergent_now(window_days: int = 1, limit_each: int = 60) -> int:
    frames = []
    for q in _default_queries():
        dfr = _fetch_news_rss_google(q, max_items=int(limit_each), days=int(window_days))
        if not dfr.empty:
            frames.append(dfr)
    if _newsapi_key():
        for q in _default_queries():
            dfa = _fetch_news_newsapi(q, page_size=min(int(limit_each), 100), pages=2)
            if not dfa.empty:
                frames.append(dfa)
    if not frames:
        return 0
    extra = pd.concat(frames, ignore_index=True)
    if "url" in extra.columns:
        extra = extra.drop_duplicates(subset=["url"]).reset_index(drop=True)
    base = _load_news(NEWS_CSV)
    merged = pd.concat([base, extra], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
    _save_news(merged)
    return len(merged) - len(base)

def _target_progress(today_df: pd.DataFrame, target: int = 200) -> tuple[int, int]:
    return len(today_df), target

def _ui_toolbar_global(df_today: pd.DataFrame):
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("🔄 Buscar emergentes ahora", use_container_width=True):
            added = _fetch_emergent_now(window_days=1, limit_each=60)
            st.success(f"Nuevas agregadas: {added}"); st.rerun()
    with c2:
        if st.button("🛰 Variedad (multi-consulta)", use_container_width=True):
            added = _fetch_emergent_now(window_days=3, limit_each=100)
            st.success(f"Variedad agregada: {added}"); st.rerun()
    with c3:
        if st.button("📦 Backup ahora", use_container_width=True):
            path = _backup_now(_load_news(NEWS_CSV))
            st.toast(f"Backup guardado: {path.name}", icon="📦")
    with c4:
        if st.button("📥 Ver cola", use_container_width=True):
            st.session_state[NAV_KEY] = NAV_LABELS["noticias_procesar"][0]
            st.session_state["_show_queue"] = True
            st.rerun()
    with c5:
        if st.button("🗑️ Papelera", use_container_width=True):
            _router_go("noticias_papelera")
    n, goal = _target_progress(df_today, target=200)
    st.caption(f"🎯 Progreso del día: **{n}/{goal}** crudas")

# ================== PARTE 3 — Scoring sencillo + UIs de vistas ==================

PALABRAS_ALTO_IMPACTO_DEFAULT = [
    "récord","récords","récordes","récord histórico","histórico",
    "crisis","urge","alerta","riesgo","pánico","colapso","explosión",
    "millonario","multimillonario","jackpot","bote","ganador","acumulado",
]

def _lexicon_score(text: str) -> tuple[str, int]:
    """Mini diccionario muy simple (0..100)."""
    t = (text or "").lower()
    score = 0
    score += 20 if any(w in t for w in ["récord","histórico","jackpot","bote"]) else 0
    score += 15 if any(w in t for w in ["crisis","pánico","colapso"]) else 0
    score += 10 if any(w in t for w in ["millonario","acumulado","ganador"]) else 0
    score = max(0, min(100, score))
    label = "alto" if score >= 60 else "medio" if score >= 30 else "bajo"
    return label, score

def _nlp_backend(text: str) -> dict | None:
    """Stub: sin modelo ML, devolvemos None."""
    return None

def _final_score(lex_score: int, model_score: int | None) -> int:
    return int(model_score) if model_score is not None else int(lex_score)

def _categorize(text: str) -> list[str]:
    t = (text or "").lower()
    cats = []
    if any(w in t for w in ["powerball","mega millions","megamillions","lotería","loteria","lottery"]):
        cats.append("loterias")
    if any(w in t for w in ["ia","ai","inteligencia artificial","modelo"]):
        cats.append("ia")
    if any(w in t for w in ["inflación","inflacion","economía","economia","mercado"]):
        cats.append("economia")
    return cats

def _high_impact_hit(text: str, palabras: list[str]) -> bool:
    t = (text or "").lower()
    return any(w.lower() in t for w in palabras)

# ========= Crudas =========
def _ui_crudas_v2(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("🗞️ Noticias crudas (primarias)")
    if df.empty:
        st.info("No hay noticias crudas para mostrar.")
        return df
   # ========= Filtradas =========
def _ui_filtradas_v2(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("🔥 Noticias filtradas (alto impacto)")

    colU, colW = st.columns(2)
    with colU:
        umbral = st.slider("Umbral emoción final", 0, 100, 60, key="sl_fil_umbral")
    with colW:
        alto = st.multiselect(
            "Palabras de alto impacto",
            PALABRAS_ALTO_IMPACTO_DEFAULT,
            default=PALABRAS_ALTO_IMPACTO_DEFAULT[:10],
            key="ms_fil_alto",
        )

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
        motivo = (
            f"Incluida: emoción={final}≥{umbral} + alto impacto" if (final >= umbral and hit) else
            f"Incluida: emoción={final}≥{umbral}" if (final >= umbral) else
            f"Incluida: alto impacto (emocion={final}<{umbral})" if hit else
            f"Excluida: emoción={final}<{umbral} sin alto impacto"
        )
        enriched.append({
            **r.to_dict(),
            "emocion_dominante": (nlp["emocion"] if (nlp and nlp.get("emocion")) else emo_lex),
            "nivel_emocional_lexicon": score_lex,
            "nivel_emocional_modelo": (score_model if score_model is not None else ""),
            "nivel_emocional_final": final,
            "categorias_emocionales": ";".join(sorted(set(cats))) if cats else "",
            "motivo_filtrado": motivo,
            "es_alto_impacto": motivo.startswith("Incluida"),
        })

    dff = pd.DataFrame(enriched)
    ok = dff[dff["es_alto_impacto"] == True].copy()  # noqa: E712
    ok = ok.sort_values(["fecha","fuente","titular"], ascending=[False, True, True]).reset_index(drop=True)
    ok = _enumerate_df(ok)

    st.caption(f"Seleccionadas: **{len(ok)}** / {len(dff)}")
    st.dataframe(
        ok[["#", "fecha","fuente","titular","nivel_emocional_final","categorias_emocionales","motivo_filtrado","url"]],
        use_container_width=True,
        hide_index=True,
        key="df_filtradas",
    )

    ids = st.multiselect(
        "Selecciona id_noticia (filtradas) para acciones",
        options=ok["id_noticia"].tolist(),
        key="ms_fil_ids",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📤 Enviar a Cola", use_container_width=True, disabled=not ids, key="btn_fil_cola"):
            _queue_add(ok[ok["id_noticia"].isin(ids)])
            st.success(f"Enviadas {len(ids)} a la cola.")
            st.experimental_rerun()
    with c2:
        if st.button("🔤 Ir a Gematría", use_container_width=True, disabled=not ids, key="btn_fil_gema"):
            _queue_add(ok[ok["id_noticia"].isin(ids)])
            _router_go("gematria")
    with c3:
        if st.button("🌀 Ir a Subliminal", use_container_width=True, disabled=not ids, key="btn_fil_sub"):
            _queue_add(ok[ok["id_noticia"].isin(ids)])
            _router_go("subliminal")
    with c4:
        if st.button("🗑️ Mover a Papelera", use_container_width=True, disabled=not ids, key="btn_fil_trash"):
            base = _load_news(NEWS_CSV)
            _move_to_trash(base, ids)
            st.success(f"Movidas {len(ids)} a papelera.")
            st.experimental_rerun()

    return ok


# ========= Procesar =========
def _ui_procesar():
    st.subheader("⚙️ Procesar / Analizar noticias")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔤 Abrir Gematría", use_container_width=True, key="btn_proc_gema"):
            _router_go("gematria")
    with c2:
        if st.button("🌀 Abrir Subliminal", use_container_width=True, key="btn_proc_sub"):
            _router_go("subliminal")
    with c3:
        if st.button("📥 Ver cola (pendientes)", use_container_width=True, key="btn_proc_cola"):
            st.session_state["_show_queue"] = True
            st.experimental_rerun()
    if st.session_state.get("_show_queue"):
        _ui_queue()


# ========= Explorador / Ingreso =========
def _ui_explorador_v2(df: pd.DataFrame):
    st.subheader("🔎 Explorador / Ingreso")
    st.caption("Trae más noticias desde varias fuentes o agrega manualmente. Todo se queda en la app.")

    fuente = st.selectbox("Fuente", ["Google News (RSS)", "NewsAPI"], index=0, key="sb_exp_fuente")
    q = st.text_input("Consulta (amplia)", _default_query(), key="ti_exp_q")
    n = st.slider("Cantidad a traer por consulta", 20, 100, 60, step=10, key="sl_exp_n")
    window = st.selectbox("Ventana temporal", ["24h","48h","72h"], index=0, key="sb_exp_window")
    days = {"24h":1, "48h":2, "72h":3}[window]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Traer noticias", use_container_width=True, key="btn_exp_traer"):
            extra = (_fetch_news_rss_google(q, max_items=int(n), days=days)
                     if fuente == "Google News (RSS)"
                     else _fetch_news_newsapi(q, page_size=int(n), pages=2))
            if extra is None or extra.empty:
                st.warning("No se trajo nada (prueba otra consulta/fuente).")
            else:
                merged = pd.concat([df, extra], ignore_index=True)
                if "url" in merged.columns:
                    merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
                _save_news(merged)
                st.success(f"+{len(merged)-len(df)} noticias nuevas.")
                st.experimental_rerun()
    with c2:
        if st.button("🛰 Traer variedad (multi-consulta)", use_container_width=True, key="btn_exp_var"):
            added = _fetch_emergent_now(window_days=days, limit_each=100)
            st.success(f"Variedad agregada: {added}")
            st.experimental_rerun()

    st.markdown("---")
    st.markdown("### ✍️ Pegar noticias manuales (una por línea)")
    raw = st.text_area(
        "Pega aquí (formato: título | resumen | fuente | url, o 'título — resumen')",
        height=160,
        key="ta_exp_paste",
    )

    colp1, colp2, colp3 = st.columns([1,1,1])
    with colp1:
        if st.button("➕ Ingresar a Crudas", use_container_width=True, disabled=not raw.strip(), key="btn_exp_ing_crudas"):
            rows = _manual_paste_parse(raw)
            _ingest_manual(rows, destino="crudas")
            st.experimental_rerun()
    with colp2:
        if st.button("📤 Ingresar a Cola (procesar)", use_container_width=True, disabled=not raw.strip(), key="btn_exp_ing_cola"):
            rows = _manual_paste_parse(raw)
            _ingest_manual(rows, destino="cola")
            st.experimental_rerun()
    with colp3:
        st.download_button(
            "⬇️ Descargar noticias actuales (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv",
            use_container_width=True,
            key="dl_exp_actuales",
        )


# ========= Utilidad de limpieza =========
def _clean_news_file():
    """Asegura columnas y quita duplicados por URL e id."""
    base = _load_news(NEWS_CSV)
    if base.empty:
        st.info("No hay nada que limpiar.")
        return
    before = len(base)
    if "url" in base.columns:
        base = base.drop_duplicates(subset=["url"], keep="first")
    base = base.drop_duplicates(subset=["id_noticia"], keep="first")
    _save_news(base)
    st.success(f"Limpieza completa. Filas: {before} → {len(base)}")


# ========= Render principal =========
def render_noticias():
    st.header("📰 Noticias — Filtro emocional PRO")

    # Carga base + “del día” (para progreso)
    df_all = _load_news(NEWS_CSV)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    df_today = df_all[df_all["fecha"] == today_str].copy()

    # Barra de herramientas superior
    _ui_toolbar_global(df_today)
    st.markdown("---")

    # Subnavegación
    options = [
        NAV_LABELS["noticias_crudas"][0],
        NAV_LABELS["noticias_filtradas"][0],
        NAV_LABELS["noticias_procesar"][0],
        NAV_LABELS["noticias_explorar"][0],
        NAV_LABELS["noticias_papelera"][0],
        NAV_LABELS["noticias_limpiar"][0],
    ]
    current = st.session_state.get(NAV_KEY, options[0])
    sel = st.radio(
        "Sección",
        options,
        index=options.index(current) if current in options else 0,
        horizontal=True,
        label_visibility="collapsed",
        key="radio_news_section",
    )
    st.session_state[NAV_KEY] = sel  # persistir

    # Ramas
    if sel == NAV_LABELS["noticias_crudas"][0]:
        _ui_crudas_v2(df_all)
    elif sel == NAV_LABELS["noticias_filtradas"][0]:
        _ui_filtradas_v2(df_all)
    elif sel == NAV_LABELS["noticias_procesar"][0]:
        _ui_procesar()
    elif sel == NAV_LABELS["noticias_explorar"][0]:
        _ui_explorador_v2(df_all)
    elif sel == NAV_LABELS["noticias_papelera"][0]:
        _ui_papelera()
    elif sel == NAV_LABELS["noticias_limpiar"][0]:
        _clean_news_file()

    # Pie
    st.caption(f"📁 Archivo base: `{NEWS_CSV.name}` · Carpeta de trabajo: `{RUNS_NEWS}`")
    dff = df.sort_values(["fecha", "fuente", "titular"], ascending=[False, True, True]).reset_index(drop=True)
    dff = _enumerate_df(dff)
    st.caption(f"Total crudas visibles: **{len(dff)}**")
    st.dataframe(dff[["#", "fecha","fuente","titular","url","etiquetas"]], use_container_width=True, hide_index=True)

    ids = st.multiselect("Selecciona id_noticia para acciones", options=df["id_noticia"].tolist())
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📤 Enviar a Cola (Gematría/Subliminal)", use_container_width=True, disabled=not ids):
            _queue_add(df[df["id_noticia"].isin(ids)])
            st.success(f"Enviadas {len(ids)} a la cola."); st.rerun()
    with c2:
        if st.button("🗑️ Mover a Papelera", use_container_width=True, disabled=not ids):
            cleaned = _move_to_trash(df, ids)
            st.success(f"Movidas {len(ids)} a papelera."); st.rerun()
    with c3:
        st.download_button(
            "⬇️ Descargar crudas (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_crudas_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv", use_container_width=True,
        )
    return df


# ========= Filtradas =========
def _ui_filtradas_v2(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("🔥 Noticias filtradas (alto impacto)")
    colU, colW = st.columns(2)
    with colU:
        umbral = st.slider("Umbral emoción final", 0, 100, 60)
    with colW:
        alto = st.multiselect("Palabras de alto impacto", PALABRAS_ALTO_IMPACTO_DEFAULT, default=PALABRAS_ALTO_IMPACTO_DEFAULT[:10])

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
        motivo = (
            f"Incluida: emoción={final}≥{umbral} + alto impacto" if (final >= umbral and hit) else
            f"Incluida: emoción={final}≥{umbral}" if (final >= umbral) else
            f"Incluida: alto impacto (emocion={final}<{umbral})" if hit else
            f"Excluida: emoción={final}<{umbral} sin alto impacto"
        )
        enriched.append({
            **r.to_dict(),
            "emocion_dominante": (nlp["emocion"] if (nlp and nlp.get("emocion")) else emo_lex),
            "nivel_emocional_lexicon": score_lex,
            "nivel_emocional_modelo": (score_model if score_model is not None else ""),
            "nivel_emocional_final": final,
            "categorias_emocionales": ";".join(sorted(set(cats))) if cats else "",
            "motivo_filtrado": motivo,
            "es_alto_impacto": motivo.startswith("Incluida"),
        })

    dff = pd.DataFrame(enriched)
    ok = dff[dff["es_alto_impacto"] == True].copy()  # noqa: E712
    ok = ok.sort_values(["fecha","fuente","titular"], ascending=[False, True, True]).reset_index(drop=True)
    ok = _enumerate_df(ok)
    st.caption(f"Seleccionadas: **{len(ok)}** / {len(dff)}")
    st.dataframe(
        ok[["#", "fecha","fuente","titular","nivel_emocional_final","categorias_emocionales","motivo_filtrado","url"]],
        use_container_width=True, hide_index=True
    )

    ids = st.multiselect("Selecciona id_noticia (filtradas) para acciones", options=ok["id_noticia"].tolist())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📤 Enviar a Cola", use_container_width=True, disabled=not ids):
            _queue_add(ok[ok["id_noticia"].isin(ids)])
            st.success(f"Enviadas {len(ids)} a la cola."); st.rerun()
    with c2:
        if st.button("🔤 Ir a Gematría", use_container_width=True, disabled=not ids):
            _queue_add(ok[ok["id_noticia"].isin(ids)]); _router_go("gematria")
    with c3:
        if st.button("🌀 Ir a Subliminal", use_container_width=True, disabled=not ids):
            _queue_add(ok[ok["id_noticia"].isin(ids)]); _router_go("subliminal")
    with c4:
        if st.button("🗑️ Mover a Papelera", use_container_width=True, disabled=not ids):
            base = _load_news(NEWS_CSV)
            cleaned = _move_to_trash(base, ids)
            st.success(f"Movidas {len(ids)} a papelera."); st.rerun()
    return ok
   def _ui_procesar():
    st.subheader("⚙️ Procesar / Analizar noticias")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔤 Abrir Gematría", use_container_width=True):
            _router_go("gematria")
    with c2:
        if st.button("🌀 Abrir Subliminal", use_container_width=True):
            _router_go("subliminal")
    with c3:
        if st.button("📥 Ver cola (pendientes)", use_container_width=True):
            st.session_state["_show_queue"] = True
            st.rerun()
    if st.session_state.get("_show_queue"):
        _ui_queue()


def _ui_explorador_v2(df: pd.DataFrame):
    st.subheader("🔎 Explorador / Ingreso")
    st.caption("Trae más noticias desde varias fuentes o agrega manualmente.")
    fuente = st.selectbox("Fuente", ["Google News (RSS)", "NewsAPI"], index=0)
    q = st.text_input("Consulta (amplia)", _default_query())
    n = st.slider("Cantidad a traer por consulta", 20, 100, 60, step=10)
    window = st.selectbox("Ventana temporal", ["24h","48h","72h"], index=0)
    days = {"24h":1, "48h":2, "72h":3}[window]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Traer noticias", use_container_width=True):
            extra = _fetch_news_rss_google(q, max_items=int(n), days=days) if fuente == "Google News (RSS)" else _fetch_news_newsapi(q, page_size=int(n), pages=2)
            if extra is None or extra.empty:
                st.warning("No se trajo nada (prueba otra consulta/fuente).")
            else:
                merged = pd.concat([df, extra], ignore_index=True)
                if "url" in merged.columns: merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
                _save_news(merged); st.success(f"+{len(merged)-len(df)} noticias nuevas."); st.rerun()
    with c2:
        if st.button("🛰 Traer variedad (multi-consulta)", use_container_width=True):
            added = _fetch_emergent_now(window_days=days, limit_each=100)
            st.success(f"Variedad agregada: {added}"); st.rerun()

    st.markdown("---")
    st.markdown("### ✍️ Pegar noticias manuales (una por línea)")
    raw = st.text_area("Formato: título | resumen | fuente | url  (o)  'título — resumen'", height=160)
    colp1, colp2, colp3 = st.columns(3)
    with colp1:
        if st.button("➕ Ingresar a Crudas", use_container_width=True, disabled=not raw.strip()):
            rows = _manual_paste_parse(raw); _ingest_manual(rows, destino="crudas"); st.rerun()
    with colp2:
        if st.button("📤 Ingresar a Cola (procesar)", use_container_width=True, disabled=not raw.strip()):
            rows = _manual_paste_parse(raw); _ingest_manual(rows, destino="cola"); st.rerun()
    with colp3:
        st.download_button(
            "⬇️ Descargar noticias actuales (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv", use_container_width=True,
        )


def _clean_news_file():
    """Utilidad de limpieza: asegura columnas, quita duplicados por URL."""
    base = _load_news(NEWS_CSV)
    if base.empty:
        st.info("No hay nada que limpiar.")
        return
    before = len(base)
    if "url" in base.columns:
        base = base.drop_duplicates(subset=["url"], keep="first")
    base = base.drop_duplicates(subset=["id_noticia"], keep="first")
    _save_news(base)
    st.success(f"Limpieza completa. Filas: {before} → {len(base)}")


def render_noticias():
    st.header("📰 Noticias — Filtro emocional PRO")

    # Carga base + “del día” (para progreso)
    df_all = _load_news(NEWS_CSV)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    df_today = df_all[df_all["fecha"] == today_str].copy()

    # Barra de herramientas superior
    _ui_toolbar_global(df_today)
    st.markdown("---")

    # Subnavegación
    options = [
        NAV_LABELS["noticias_crudas"][0],
        NAV_LABELS["noticias_filtradas"][0],
        NAV_LABELS["noticias_procesar"][0],
        NAV_LABELS["noticias_explorar"][0],
        NAV_LABELS["noticias_papelera"][0],
        NAV_LABELS["noticias_limpiar"][0],
    ]
    current = st.session_state.get(NAV_KEY, options[0])
    sel = st.radio(
        "Sección",
        options,
        index=options.index(current) if current in options else 0,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state[NAV_KEY] = sel  # persistir

    # Ramas
    if sel == NAV_LABELS["noticias_crudas"][0]:
        _ui_crudas_v2(df_all)
    elif sel == NAV_LABELS["noticias_filtradas"][0]:
        _ui_filtradas_v2(df_all)
    elif sel == NAV_LABELS["noticias_procesar"][0]:
        _ui_procesar()
    elif sel == NAV_LABELS["noticias_explorar"][0]:
        _ui_explorador_v2(df_all)
    elif sel == NAV_LABELS["noticias_papelera"][0]:
        _ui_papelera()
    elif sel == NAV_LABELS["noticias_limpiar"][0]:
        _clean_news_file()

    # Pie
    st.caption(f"📁 Archivo base: `{NEWS_CSV.name}` · Carpeta de trabajo: `{RUNS_NEWS}`") 
        
