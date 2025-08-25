# modules/noticias_module.py — Acopio Emoción Social (USA) · Día del protocolo (Cuba)
# - Amplio (RSS + Google News + Bing News), real (feeds públicos), sin inventos.
# - Concurrencia, listas editables (__CONFIG/*.txt), bloqueo de spam/agregadores.
# - Filtro ESTRICTO: SOLO noticias del "día del protocolo" según hora de Cuba (America/Havana).
# - Scoring emocional + relevancia + recencia, dedup semántica, límite por fuente.
# - UI estable con reloj Cuba, métricas, papelera, bitácora y buffers (GEM/SUBLIMINAL/T70).

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import re, time, hashlib
import feedparser
import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

# =================== Paths base ===================
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "__RUNS" / "NEWS"
LEDGER_DIR = OUT_DIR / "ledger"
TRASH_DIR = OUT_DIR / ".trash"
BUFF_GEM = ROOT / "__RUNS" / "GEMATRIA_IN"
BUFF_SUB = ROOT / "__RUNS" / "SUBLIMINAL_IN"
BUFF_T70 = ROOT / "__RUNS" / "T70_IN"
T70_PATH = ROOT / "T70.csv"
RAW_LAST = OUT_DIR / "ultimo_acopio_bruto.csv"
SEL_LAST = OUT_DIR / "ultima_seleccion_es.csv"

for p in [OUT_DIR, LEDGER_DIR, TRASH_DIR, BUFF_GEM, BUFF_SUB, BUFF_T70]:
    p.mkdir(parents=True, exist_ok=True)

# =================== Config núcleo ===================
PROTOCOL_TZ = "America/Havana"   # Reloj y día del protocolo (Cuba)
CFG = {
    "RECENCY_HOURS": 72,         # ventana de recencia dura (además del "mismo día")
    "MIN_TOKENS": 8,             # tamaño mínimo de texto útil
    "MAX_PER_SOURCE": 4,         # diversidad por dominio
    "SEMANTIC_ON": True,         # deduplicación semántica
    "SEMANTIC_THR": 0.82,        # umbral coseno TF-IDF
    "SOFT_DEDUP_NORM": True,     # normalización de titulares fallback
    "MAX_WORKERS": 12,           # concurrencia de fetch
    "STRICT_SAME_DAY": True,     # SOLO día del protocolo (Cuba)
}

# Bloqueo de agregadores/duplicadores
SPAM_BLOCK = [
    "news.google.com", "feedproxy.google.com", "news.yahoo.com", "bing.com"
]

# =================== Config externo (listas editables) ===================
CONFIG_DIR = ROOT / "__CONFIG"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
RSS_TXT = CONFIG_DIR / "rss_sources.txt"
GNEWS_TXT = CONFIG_DIR / "gnews_queries.txt"
BING_TXT = CONFIG_DIR / "bing_queries.txt"

def _load_list(path: Path, defaults: list[str]) -> list[str]:
    items = []
    try:
        if path.exists():
            for raw in path.read_text(encoding="utf-8").splitlines():
                s = raw.strip()
                if not s or s.startswith("#"):
                    continue
                items.append(s)
    except Exception:
        pass
    return items if items else list(defaults)

# Defaults robustos (USA)
RSS_SOURCES_DEFAULT = [
    "https://www.reuters.com/rssFeed/usNews",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.abcnews.com/abcnews/usheadlines",
    "https://www.cbsnews.com/latest/rss/us/",
    "https://www.theguardian.com/us-news/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
    "http://rss.cnn.com/rss/cnn_us.rss",
    "http://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
    "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",
]
GNEWS_QUERIES_DEFAULT = [
    # EN (impacto social en USA)
    "protest OR strike OR riot OR looting site:us",
    "shortage OR blackout OR curfew OR evacuation site:us",
    "boycott OR layoffs OR outage OR wildfire OR hurricane OR flood site:us",
    "mass shooting OR unrest OR clashes site:us",
    # ES (comunidad hispana en USA)
    "protesta OR huelga OR disturbios OR saqueo site:us",
    "desabasto OR apagón OR toque de queda OR evacuación site:us",
    "boicot OR despidos OR tiroteo masivo site:us",
]
BING_QUERIES_DEFAULT = list(GNEWS_QUERIES_DEFAULT)

RSS_SOURCES = _load_list(RSS_TXT, RSS_SOURCES_DEFAULT)
GNEWS_QUERIES = _load_list(GNEWS_TXT, GNEWS_QUERIES_DEFAULT)
BING_QUERIES = _load_list(BING_TXT, BING_QUERIES_DEFAULT)

def _gnews_rss_url(q: str) -> str:
    from urllib.parse import quote_plus
    return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"

def _bingnews_rss_url(q: str) -> str:
    from urllib.parse import quote_plus
    return f"https://www.bing.com/news/search?q={quote_plus(q)}&format=RSS&setmkt=en-US&setlang=en-US"

# =================== Utilidades ===================
def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _now_cuba() -> datetime:
    return datetime.now(ZoneInfo(PROTOCOL_TZ))

def _today_cuba_date_str() -> str:
    return _now_cuba().strftime("%Y-%m-%d")

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()[:16]

def _domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except Exception:
        return ""

def _tokens(text: str) -> int:
    return len(re.findall(r"\w+", str(text or "")))

def _coerce_dt_from_feed(entry) -> datetime | None:
    try:
        tt = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
        if tt:
            # Asumimos UTC al no tener tz; feedparser devuelve tupla de tiempo
            return datetime(*tt[:6], tzinfo=timezone.utc)
    except Exception:
        pass
    return None

def _recency_factor(ts_utc: datetime | None) -> float:
    if ts_utc is None:
        return 0.6
    hours = (_now_utc() - ts_utc).total_seconds() / 3600.0
    if hours <= 12: return 1.0
    if hours <= 24: return 0.95
    if hours <= 48: return 0.9
    if hours <= 72: return 0.8
    return 0.7

# Triggers y temas (impacto emocional)
TRIGGERS = {
    "protest":1.0,"strike":1.0,"riot":1.0,"looting":1.0,"shortage":0.9,
    "blackout":0.9,"curfew":1.0,"evacuation":0.9,"boycott":0.9,"mass shooting":1.0,
    "unrest":0.9,"clashes":0.9,"layoffs":0.8,"outage":0.8,
    "protesta":1.0,"huelga":1.0,"disturbios":1.0,"saqueo":1.0,"desabasto":0.9,
    "apagón":0.9,"toque de queda":1.0,"evacuación":0.9,"boicot":0.9,"tiroteo":1.0,"despidos":0.8
}
TOPICS = {
    "salud":["hospital","infección","brote","vacuna","epidemia","health","outbreak"],
    "economía":["inflación","desempleo","cierres","layoffs","crash","recesión"],
    "seguridad":["tiroteo","violencia","homicidio","shooting","kidnapping","unrest"],
    "clima":["huracán","terremoto","inundación","ola de calor","heatwave","wildfire","hurricane","flood"],
    "política":["elecciones","protesta","congreso","parlamento","impeachment"],
}

def _emo_heuristics(text: str) -> float:
    t = (text or "").lower()
    score = 0.0
    for k, w in TRIGGERS.items():
        if k in t: score += w
    score += 0.1 * t.count("!")
    if any(flag in t for flag in ["breaking", "última hora", "urgente"]):
        score += 0.15
    return min(score, 3.0) / 3.0

def _topic_relevance(text: str) -> float:
    t = (text or "").lower()
    hits = sum(1 for kws in TOPICS.values() if any(k in t for k in kws))
    return min(0.2 * hits, 1.0)

def _source_weight(domain: str) -> float:
    d = (domain or "").lower()
    majors = ["reuters","apnews","npr","bbc","abcnews","cbsnews","nytimes","wsj","guardian","nbcnews","latimes","usatoday","cnn"]
    locals_ = ["miamiherald","chicagotribune","houstonchronicle","dallasnews","sfchronicle"]
    if any(m in d for m in majors): return 1.15
    if any(l in d for l in locals_): return 1.05
    return 1.0

# =================== Deduplicación ===================
def _soft_dedup(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: return df
    base = df.copy()
    base["_tit_norm"] = base["titular"].fillna("").str.lower().str.replace(r"[\W_]+"," ",regex=True).str.strip()
    base = base.drop_duplicates(subset=["_tit_norm"], keep="first")
    return base.drop(columns=["_tit_norm"], errors="ignore")

def _semantic_dedup(df: pd.DataFrame, thr: float) -> pd.DataFrame:
    if df.empty or len(df) == 1: return df
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except Exception:
        return _soft_dedup(df)
    texts = (df["titular"].fillna("") + " " + df["resumen"].fillna("")).tolist()
    vec = TfidfVectorizer(max_features=25000, ngram_range=(1,2), lowercase=True, strip_accents="unicode")
    X = vec.fit_transform(texts)
    sim = cosine_similarity(X, dense_output=False)
    keep, removed = [], set()
    n = len(df)
    for i in range(n):
        if i in removed: continue
        keep.append(i)
        row = sim.getrow(i)  # eficiente
        near = row.nonzero()[1]
        for j in near:
            if j != i and row[0, j] >= thr:
                removed.add(j)
    return df.iloc[keep].copy()

# =================== Fetch ===================
def _fetch_rss(url: str) -> list[dict]:
    try:
        data = feedparser.parse(url, request_headers={"User-Agent":"Mozilla/5.0"})
        out = []
        for e in data.entries:
            title = getattr(e, "title", "") or ""
            summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
            link = getattr(e, "link", "") or ""
            ts = _coerce_dt_from_feed(e)
            out.append({
                "titular": title.strip(),
                "resumen": re.sub("<[^<]+?>", "", summary).strip(),
                "url": link.strip(),
                "fecha_dt": ts,
                "fuente": _domain(link),
                "raw_source": url,
            })
        return out
    except Exception:
        return []

def _fetch_all_sources() -> tuple[pd.DataFrame, dict]:
    started = time.time()
    logs = {"sources": [], "errors": []}

    urls = []
    urls.extend(RSS_SOURCES)
    urls.extend([_gnews_rss_url(q) for q in GNEWS_QUERIES])
    urls.extend([_bingnews_rss_url(q) for q in BING_QUERIES])

    all_items: list[dict] = []
    max_workers = max(4, min(CFG["MAX_WORKERS"], len(urls))) if urls else 4
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        fut2src = {ex.submit(_fetch_rss, u): u for u in urls}
        for fut in as_completed(fut2src):
            src = fut2src[fut]
            try:
                items = fut.result() or []
                logs["sources"].append({"source": src, "items": len(items)})
                all_items.extend(items)
            except Exception as e:
                logs["errors"].append({"source": src, "error": str(e)})

    df = pd.DataFrame(all_items)
    if not df.empty:
        # Normalización + reglas duras
        df["fuente"] = df["fuente"].fillna("").str.strip().str.lower()
        df = df[~df["fuente"].isin(SPAM_BLOCK)]

        df["fecha_dt"] = pd.to_datetime(df["fecha_dt"], utc=True, errors="coerce")
        df = df[df["fecha_dt"].notna()]

        # Filtro de recencia dura
        cutoff = _now_utc() - timedelta(hours=CFG["RECENCY_HOURS"])
        df = df[df["fecha_dt"] >= cutoff]

        # Filtro “mismo día Cuba” (obligatorio si STRICT_SAME_DAY)
        if CFG["STRICT_SAME_DAY"]:
            today_cu = _today_cuba_date_str()
            df["_date_cuba"] = df["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d")
            df = df[df["_date_cuba"] == today_cu]

        df["titular"] = df["titular"].fillna("").str.strip()
        df["resumen"] = df["resumen"].fillna("").str.strip()
        df["tokens"] = (df["titular"] + " " + df["resumen"]).map(_tokens)
        df = df[df["tokens"] >= CFG["MIN_TOKENS"]]

        df["id_noticia"] = df.apply(lambda r: _hash((r["titular"] or "") + (r["url"] or "")), axis=1)
        df["pais"] = "US"
        df["_texto"] = (df["titular"] + " " + df["resumen"]).str.strip()

        # limpieza de columna temporal
        df = df.drop(columns=["_date_cuba"], errors="ignore")

    logs["elapsed_sec"] = round(time.time() - started, 2)
    return df, logs

# =================== Scoring ===================
def _score_emocion_social(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    emos, recs, rels, srcw = [], [], [], []
    for _, row in df.iterrows():
        txt = f"{row.get('titular','')} {row.get('resumen','')}"
        emos.append(_emo_heuristics(txt))
        recs.append(_recency_factor(row.get("fecha_dt")))
        rels.append(_topic_relevance(txt))
        srcw.append(_source_weight(row.get("fuente","")))
    df = df.copy()
    df["_emo"] = emos
    df["_recency"] = recs
    df["_rel"] = rels
    df["_srcw"] = srcw
    df["_score_es"] = 0.35*df["_emo"] + 0.20*df["_rel"] + 0.20*df["_recency"] + 0.20*df["_srcw"] + 0.05
    return df

def _limit_per_source(df: pd.DataFrame, k: int) -> pd.DataFrame:
    if df.empty or k <= 0: return df
    df = df.copy()
    df["_rank_src"] = df.groupby("fuente")["_score_es"].rank(ascending=False, method="first")
    out = df[df["_rank_src"] <= k].drop(columns=["_rank_src"], errors="ignore")
    return out

# =================== Persistencia ===================
def _ts() -> str: return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
def _save_csv(df: pd.DataFrame, path: Path):
    if df is None: return
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")

def _append_trash(df_rows: pd.DataFrame, reason: str = "manual"):
    if df_rows.empty: return
    trash = TRASH_DIR / "trash.csv"
    df_rows = df_rows.copy()
    df_rows["trash_reason"] = reason
    df_rows["trash_ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    if trash.exists():
        try:
            prev = pd.read_csv(trash, dtype=str, encoding="utf-8")
            df_rows = pd.concat([prev, df_rows], ignore_index=True)
        except Exception:
            pass
    _save_csv(df_rows, trash)

def _save_ledger(df_sel: pd.DataFrame, lottery: str):
    day = datetime.now(ZoneInfo(PROTOCOL_TZ)).strftime("%Y%m%d")  # día Cuba
    folder = LEDGER_DIR / lottery / day
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"bitacora_{_ts()}.csv"
    _save_csv(df_sel, path)
    return path

def _export_buffer(df_rows: pd.DataFrame, kind: str) -> Path | None:
    # kind in {"GEM","SUB","T70"}
    if df_rows.empty: return None
    base = {"GEM": BUFF_GEM, "SUB": BUFF_SUB, "T70": BUFF_T70}[kind]
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"news_batch_{_ts()}.csv"
    _save_csv(df_rows, path)
    return path

# =================== UI principal ===================
def render_noticias():
    # Reloj de Cuba (siempre visible)
    now_cu = _now_cuba()
    dia_cuba = now_cu.strftime("%Y-%m-%d")
    hora_cuba = now_cu.strftime("%H:%M:%S")
    st.subheader("📰 Noticias · Emoción Social (USA)")
    st.caption(f"🕒 Cuba (America/Havana): **{dia_cuba} {hora_cuba}**  ·  Filtro activo: SOLO día del protocolo en Cuba")

    # Sidebar fijo
    with st.sidebar:
        st.markdown("#### Acciones")
        if st.button("↻ Reacopiar ahora", use_container_width=True, key="btn_reacopiar"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("#### Descargas")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if RAW_LAST.exists():
                st.download_button("Acopio bruto", RAW_LAST.read_bytes(), "acopio_bruto_ultimo.csv",
                                   use_container_width=True, key="dl_raw")
        with col_dl2:
            if SEL_LAST.exists():
                st.download_button("Selección ES", SEL_LAST.read_bytes(), "seleccion_es_ultima.csv",
                                   use_container_width=True, key="dl_sel")

        st.markdown("#### Enviar selección a")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔡 GEM", use_container_width=True, key="send_gem"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "GEM")
                    st.toast(f"GEMATRÍA: {p.name if p else 'sin datos'}", icon="✅")
        with c2:
            if st.button("🌀 SUB", use_container_width=True, key="send_sub"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "SUB")
                    st.toast(f"SUBLIMINAL: {p.name if p else 'sin datos'}", icon="✅")
        with c3:
            if st.button("📊 T70", use_container_width=True, key="send_t70"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    sel2 = sel.copy()
                    # si quieres mapear a T70 aquí, añade tu lógica de categorías → números
                    sel2["T70_map"] = ""
                    p = _export_buffer(sel2, "T70")
                    st.toast(f"T70: {p.name if p else 'sin datos'}", icon="✅")

        st.markdown("#### Bitácora (por sorteo)")
        current_lottery = st.session_state.get("current_lottery", "GENERAL")
        if st.button("Guardar selección en bitácora", use_container_width=True, key="save_ledger"):
            sel = st.session_state.get("news_selected_df", pd.DataFrame())
            if not sel.empty:
                sel2 = sel.copy()
                sel2["sorteo_aplicado"] = current_lottery
                p = _save_ledger(sel2, current_lottery)
                _save_csv(sel2, SEL_LAST)  # snapshot
                st.toast(f"Bitácora guardada: {p.name}", icon="🗂️")

        st.markdown("#### Papelera")
        if st.button("Ver papelera", use_container_width=True, key="show_trash"):
            st.session_state["__show_trash__"] = True
            st.rerun()
        if st.button("Ocultar papelera", use_container_width=True, key="hide_trash"):
            st.session_state["__show_trash__"] = False
            st.rerun()

    # Acopio cacheado
    @st.cache_data(show_spinner=True)
    def _run_pipeline() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
        df_raw, logs = _fetch_all_sources()
        if df_raw.empty:
            return df_raw, df_raw, logs
        df = _score_emocion_social(df_raw)
        if CFG["SEMANTIC_ON"]:
            df = _semantic_dedup(df, CFG["SEMANTIC_THR"])
        if CFG["SOFT_DEDUP_NORM"]:
            df = _soft_dedup(df)
        df = _limit_per_source(df, CFG["MAX_PER_SOURCE"])
        df = df.sort_values(by=["_score_es", "fecha_dt"], ascending=[False, False]).reset_index(drop=True)
        _save_csv(df_raw, RAW_LAST)
        _save_csv(df, SEL_LAST)
        return df_raw, df, logs

    df_raw, df_sel, logs = _run_pipeline()
    st.session_state["news_selected_df"] = df_sel.copy()

    # Encabezado KPIs
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Fuentes", f"{len(logs.get('sources', []))}")
    m2.metric("Bruto (hoy CU)", f"{len(df_raw)}")
    m3.metric("Seleccionadas", f"{len(df_sel)}")
    m4.metric("Ventana (h)", f"{CFG['RECENCY_HOURS']}")
    m5.metric("Tiempo (s)", f"{logs.get('elapsed_sec', 0)}")

    # Papelera (opcional)
    if st.session_state.get("__show_trash__"):
        f = TRASH_DIR / "trash.csv"
        st.markdown("### 🗑️ Papelera")
        if f.exists():
            try:
                df_tr = pd.read_csv(f, dtype=str, encoding="utf-8")
                st.dataframe(df_tr, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"No se pudo leer papelera: {e}")
        else:
            st.info("Papelera vacía.")

    # Acciones sobre selección
    st.markdown("#### Acciones sobre selección actual")
    sel_ids = st.multiselect("Selecciona ID(s) de noticia:", options=df_sel.get("id_noticia", []), label_visibility="collapsed", key="ms_sel_ids")
    bar1, bar2, bar3 = st.columns(3)
    with bar1:
        if st.button("📋 Copiar seleccionadas", key="btn_copy_sel"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)][["titular", "url", "resumen"]]
          
