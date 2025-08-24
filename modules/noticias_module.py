# modules/noticias_module.py — Acopio Emoción Social (USA)
# sin filtros UI; con scoring, dedup semántica, bitácora, papelera,
# acopio/selección manual, buffers para GEM/SUBLIMINAL/T70 y mapeo T70.
# Blindado contra errores de frontend (removeChild/NotFoundError):
# - Estructura de layout estable (número de columns/slots fijo)
# - keys fijas y únicas
# - Reruns disciplinados (flags en session_state + st.stop())

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re
import time
import csv
import json
import hashlib
import requests
import feedparser
import pandas as pd
import streamlit as st

# =================== Paths base ===================
ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "__RUNS" / "NEWS"
LEDGER_DIR = ROOT / "__RUNS" / "NEWS" / "ledger"
TRASH_DIR = ROOT / "__RUNS" / "NEWS" / ".trash"
BUFF_GEM = ROOT / "__RUNS" / "GEMATRIA_IN"
BUFF_SUB = ROOT / "__RUNS" / "SUBLIMINAL_IN"
BUFF_T70 = ROOT / "__RUNS" / "T70_IN"
T70_PATH = ROOT / "T70.csv"
RAW_LAST = OUT_DIR / "ultimo_acopio_bruto.csv"         # snapshot último acopio
SEL_LAST = OUT_DIR / "ultima_seleccion_es.csv"         # snapshot última selección

for p in [OUT_DIR, LEDGER_DIR, TRASH_DIR, BUFF_GEM, BUFF_SUB, BUFF_T70]:
    p.mkdir(parents=True, exist_ok=True)

# =================== Config fija (sin UI) ===================
CFG = {
    "RECENCY_HOURS": 120,          # ventana de 5 días
    "MIN_TOKENS": 8,               # tamaño mínimo de texto útil
    "MAX_PER_SOURCE": 4,           # diversidad por dominio
    "SEMANTIC_ON": True,           # deduplicación semántica (TF-IDF)
    "SEMANTIC_THR": 0.82,          # umbral cosine
    "SOFT_DEDUP_NORM": True,       # normalización de titulares
}

SPAM_BLOCK = [
    "news.google.com", "feedproxy.google.com"
]

# =================== Fuentes ===================
RSS_SOURCES = [
    "https://www.reuters.com/rssFeed/usNews",
    "https://feeds.npr.org/1001/rss.xml",
    "https://feeds.abcnews.com/abcnews/usheadlines",
    "https://www.cbsnews.com/latest/rss/us/",
    "https://www.theguardian.com/us-news/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
]

# Google News RSS (consultas de emoción social)
GNEWS_QUERIES = [
    # EN
    "protest OR strike OR riot OR looting site:us",
    "shortage OR blackout OR curfew OR evacuation site:us",
    "boycott OR layoffs OR outage OR wildfire OR hurricane OR flood site:us",
    "mass shooting OR unrest OR clashes site:us",
    # ES (comunidad hispana en USA)
    "protesta OR huelga OR disturbios OR saqueo sitio:us",
    "desabasto OR apagón OR toque de queda OR evacuación sitio:us",
    "boicot OR despidos OR tiroteo masivo sitio:us",
]

def _gnews_rss_url(q: str) -> str:
    from urllib.parse import quote_plus
    return f"https://news.google.com/rss/search?q={quote_plus(q)}&hl=en-US&gl=US&ceid=US:en"

# =================== Utilidades base ===================
def _now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]

def _domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        if d.startswith("www."):
            d = d[4:]
        return d
    except Exception:
        return ""

def _tokens(text: str) -> int:
    if not isinstance(text, str):
        return 0
    return len(re.findall(r"\w+", text))

def _coerce_dt_from_feed(entry) -> datetime | None:
    try:
        tt = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
        if tt:
            return datetime(*tt[:6], tzinfo=timezone.utc)
    except Exception:
        pass
    return None

def _recency_factor(ts_utc: datetime | None) -> float:
    if ts_utc is None:
        return 0.7
    hours = (datetime.now(timezone.utc) - ts_utc).total_seconds() / 3600.0
    if hours <= 24: return 1.0
    if hours <= 72: return 0.9
    if hours <= 120: return 0.8
    return 0.7

TRIGGERS = {
    "protest": 1.0, "strike": 1.0, "riot": 1.0, "looting": 1.0, "shortage": 0.9,
    "blackout": 0.9, "curfew": 1.0, "evacuation": 0.9, "boycott": 0.9,
    "mass shooting": 1.0, "unrest": 0.9, "clashes": 0.9, "layoffs": 0.8, "outage": 0.8,
    # ES
    "protesta": 1.0, "huelga": 1.0, "disturbios": 1.0, "saqueo": 1.0,
    "desabasto": 0.9, "apagón": 0.9, "toque de queda": 1.0, "evacuación": 0.9,
    "boicot": 0.9, "tiroteo": 1.0, "despidos": 0.8
}
TOPICS = {
    "salud": ["hospital","infección","brote","vacuna","epidemia","health","outbreak"],
    "economía": ["inflación","devaluación","desempleo","cierres","layoffs","crash"],
    "seguridad": ["tiroteo","secuestro","violencia","homicidio","shooting","kidnapping"],
    "clima": ["huracán","sismo","terremoto","inundación","ola de calor","heatwave","wildfire","hurricane","flood"],
    "política": ["elecciones","protesta","parlamento","congreso","impeachment"],
}

def _emo_heuristics(text: str) -> float:
    t = (text or "").lower()
    score = 0.0
    for k, w in TRIGGERS.items():
        if k in t: score += w
    score += 0.1 * t.count("!")
    score += 0.15 if ("breaking" in t or "última hora" in t or "urgente" in t) else 0.0
    return min(score, 3.0) / 3.0

def _topic_relevance(text: str) -> float:
    t = (text or "").lower()
    hits = 0
    for kws in TOPICS.values():
        if any(k in t for k in kws):
            hits += 1
    return min(0.2 * hits, 1.0)

def _source_weight(domain: str) -> float:
    if not domain: return 1.0
    d = domain.lower()
    majors = ["reuters","apnews","npr","bbc","abcnews","cbsnews","nytimes","wsj","guardian","nbcnews","latimes"]
    locals_ = ["miamiherald","chicagotribune","houstonchronicle"]
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
    vec = TfidfVectorizer(max_features=20000, ngram_range=(1,2), lowercase=True, strip_accents="unicode")
    X = vec.fit_transform(texts)
    sim = cosine_similarity(X, dense_output=False)
    keep, removed = [], set()
    n = len(df)
    for i in range(n):
        if i in removed: continue
        keep.append(i)
        row = sim[i].toarray().ravel()
        near = [j for j in range(n) if j != i and row[j] >= thr]
        for j in near:
            removed.add(j)
    return df.iloc[keep].copy()

# =================== Mapeo T70 ===================
@st.cache_data(show_spinner=False)
def _t70_map() -> dict[str, list[str]]:
    """
    Devuelve dict {categoria_normalizada: [numeros]} leído desde T70.csv.
    Espera columnas: categoria, numero (o nombres cercanos).
    """
    out: dict[str, list[str]] = {}
    if not T70_PATH.exists():
        return out
    try:
        df = pd.read_csv(T70_PATH, dtype=str, encoding="utf-8")
        cols = {c.lower(): c for c in df.columns}
        cat_col = cols.get("categoria") or cols.get("category") or list(df.columns)[0]
        num_col = cols.get("numero") or cols.get("number") or list(df.columns)[1]
        for _, row in df.iterrows():
            cat = str(row.get(cat_col, "")).strip().lower()
            num = str(row.get(num_col, "")).strip()
            if not cat or not num: continue
            out.setdefault(cat, []).append(num)
    except Exception:
        pass
    return out

def _map_news_to_t70(categories: str) -> list[str]:
    if not categories:
        return []
    m = _t70_map()
    nums: list[str] = []
    for raw in re.split(r"[;,/|]+", str(categories)):
        k = raw.strip().lower()
        if not k: continue
        nums.extend(m.get(k, []))
    seen, uniq = set(), []
    for x in nums:
        if x not in seen:
            seen.add(x); uniq.append(x)
    return uniq

# =================== Acopio: fetch & normalizar ===================
def _fetch_rss(url: str, timeout: float = 7.0) -> list[dict]:
    try:
        data = feedparser.parse(url, request_headers={"User-Agent":"Mozilla/5.0"})
        items = []
        for e in data.entries:
            title = getattr(e, "title", "") or ""
            summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
            link = getattr(e, "link", "") or ""
            ts = _coerce_dt_from_feed(e)
            items.append({
                "titular": title.strip(),
                "resumen": re.sub("<[^<]+?>", "", summary).strip(),
                "url": link.strip(),
                "fecha_dt": ts,
                "fuente": _domain(link),
                "raw_source": url,
            })
        return items
    except Exception:
        return []

def _fetch_all_sources() -> tuple[pd.DataFrame, dict]:
    started = time.time()
    logs = {"sources": [], "errors": []}

    all_items = []
    # RSS directos
    for s in RSS_SOURCES:
        it = _fetch_rss(s)
        logs["sources"].append({"source": s, "items": len(it)})
        all_items.extend(it)

    # Google News RSS queries
    for q in GNEWS_QUERIES:
        url = _gnews_rss_url(q)
        it = _fetch_rss(url)
        logs["sources"].append({"source": f"GNEWS:{q}", "items": len(it)})
        all_items.extend(it)

    df = pd.DataFrame(all_items)
    if not df.empty:
        df["fuente"] = df["fuente"].fillna("").str.strip().str.lower()
        df = df[~df["fuente"].isin(SPAM_BLOCK)]
        df["fecha_dt"] = pd.to_datetime(df["fecha_dt"], utc=True, errors="coerce")
        df = df[df["fecha_dt"].notna()]
        df["titular"] = df["titular"].fillna("").str.strip()
        df["resumen"] = df["resumen"].fillna("").str.strip()
        df["tokens"] = (df["titular"] + " " + df["resumen"]).map(_tokens)
        df = df[df["tokens"] >= CFG["MIN_TOKENS"]]
        cutoff = datetime.now(timezone.utc) - timedelta(hours=CFG["RECENCY_HOURS"])
        df = df[df["fecha_dt"] >= cutoff]
        df["id_noticia"] = df.apply(lambda r: _hash((r["titular"] or "") + (r["url"] or "")), axis=1)
        df["pais"] = "US"
        df["_texto"] = (df["titular"] + " " + df["resumen"]).str.strip()

    logs["elapsed_sec"] = round(time.time() - started, 2)
    return df, logs

# =================== Scoring Emoción Social ===================
def _score_emocion_social(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    emos, recs, rels, srcw = [], [], [], []
    for _, row in df.iterrows():
        txt = f"{row.get('titular','')} {row.get('resumen','')}"
        emo = _emo_heuristics(txt)
        rel = _topic_relevance(txt)
        rec = _recency_factor(row.get("fecha_dt"))
        sw = _source_weight(row.get("fuente",""))
        emos.append(emo); recs.append(rec); rels.append(rel); srcw.append(sw)
    df = df.copy()
    df["_emo"] = emos
    df["_recency"] = recs
    df["_rel"] = rels
    df["_srcw"] = srcw
    df["_score_es"] = 0.35*df["_emo"] + 0.20*(df["_rel"]) + 0.20*(df["_recency"]) + 0.20*(df["_srcw"]) + 0.05
    return df

def _limit_per_source(df: pd.DataFrame, k: int) -> pd.DataFrame:
    if df.empty or k <= 0: return df
    df = df.copy()
    df["_rank_src"] = df.groupby("fuente")["_score_es"].rank(ascending=False, method="first")
    out = df[df["_rank_src"] <= k].drop(columns=["_rank_src"])
    return out

# =================== Persistencia utilitaria ===================
def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

def _save_csv(df: pd.DataFrame, path: Path):
    if df is None: return
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")

def _append_trash(df_rows: pd.DataFrame, reason: str = "manual"):
    if df_rows.empty: return
    trash = TRASH_DIR / "trash.csv"
    df_rows = df_rows.copy()
    df_rows["trash_reason"] = reason
    df_rows["trash_ts"] = _now_utc_str()
    if trash.exists():
        try:
            prev = pd.read_csv(trash, dtype=str, encoding="utf-8")
            df_rows = pd.concat([prev, df_rows], ignore_index=True)
        except Exception:
            pass
    _save_csv(df_rows, trash)

def _load_trash() -> pd.DataFrame:
    f = TRASH_DIR / "trash.csv"
    if not f.exists(): return pd.DataFrame()
    try:
        return pd.read_csv(f, dtype=str, encoding="utf-8")
    except Exception:
        return pd.DataFrame()

def _save_ledger(df_sel: pd.DataFrame, lottery: str):
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    folder = LEDGER_DIR / lottery / day
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"bitacora_{_ts()}.csv"
    _save_csv(df_sel, path)
    return path

# =================== Buffers a otros módulos ===================
def _export_buffer(df_rows: pd.DataFrame, kind: str) -> Path | None:
    # kind in {"GEM","SUB","T70"}
    if df_rows.empty: return None
    base = {"GEM": BUFF_GEM, "SUB": BUFF_SUB, "T70": BUFF_T70}[kind]
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"news_batch_{_ts()}.csv"
    _save_csv(df_rows, path)
    return path

# =================== Flags de acción (rerun disciplinado) ===================
def _flag(name: str):
    st.session_state[name] = True

def _consume_flag(name: str) -> bool:
    if st.session_state.get(name):
        st.session_state[name] = False
        return True
    return False

# =================== UI principal ===================
def render_noticias():
    st.subheader("📰 Acopio de noticias (Emoción social — EE. UU.)")
    st.caption(f"Última recarga: {_now_utc_str()}")

    # ---------- Acciones diferidas (previas al render) ----------
    # Si en el ciclo anterior se pulsó una acción que requiere recomputar, ejecútala ahora.
    if _consume_flag("__force_reacopio__"):
        st.cache_data.clear()
        # nada más; el flujo continúa con datos frescos

    if _consume_flag("__show_trash__"):
        st.session_state["__show_trash_mode__"] = True

    if _consume_flag("__hide_trash__"):
        st.session_state["__show_trash_mode__"] = False

    # ---------- Sidebar (estructura fija) ----------
    with st.sidebar:
        st.markdown("#### Noticias · Acciones")
        if st.button("↻ Reacopiar ahora", use_container_width=True, key="btn_reacopiar_now"):
            _flag("__force_reacopio__")
            st.stop()  # corta el render para rerun limpio

        st.markdown("#### Descargas")
        cdl, cdr = st.columns(2)

        raw_exists = RAW_LAST.exists()
        sel_exists = SEL_LAST.exists()
        raw_bytes = RAW_LAST.read_bytes() if raw_exists else b""
        sel_bytes = SEL_LAST.read_bytes() if sel_exists else b""

        with cdl:
            st.download_button(
                "Acopio bruto",
                data=raw_bytes,
                file_name="acopio_bruto_ultimo.csv",
                use_container_width=True,
                key="dl_raw_last",
                disabled=not raw_exists
            )
        with cdr:
            st.download_button(
                "Selección ES",
                data=sel_bytes,
                file_name="seleccion_es_ultima.csv",
                use_container_width=True,
                key="dl_sel_last",
                disabled=not sel_exists
            )
                    key="dl_raw_last"
                )
        with cdr:
            if SEL_LAST.exists():
                st.download_button(
                    "Selección ES",
                    SEL_LAST.read_bytes(),
                    file_name="seleccion_es_ultima.csv",
                    use_container_width=True,
                    key="dl_sel_last"
                )

        st.markdown("#### Enviar selección a")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔡 GEM", use_container_width=True, key="send_gem_btn"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "GEM")
                    st.toast(f"GEMATRÍA: {p.name if p else 'sin datos'}", icon="✅")
        with c2:
            if st.button("🌀 SUB", use_container_width=True, key="send_sub_btn"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "SUB")
                    st.toast(f"SUBLIMINAL: {p.name if p else 'sin datos'}", icon="✅")
        with c3:
            if st.button("📊 T70", use_container_width=True, key="send_t70_btn"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    sel2 = sel.copy()
                    if "categorias_t70_ref" in sel2.columns:
                        sel2["T70_map"] = sel2["categorias_t70_ref"].map(_map_news_to_t70)
                    p = _export_buffer(sel2, "T70")
                    st.toast(f"T70: {p.name if p else 'sin datos'}", icon="✅")

        st.markdown("#### Bitácora por sorteo")
        current_lottery = st.session_state.get("current_lottery", "GENERAL")
        if st.button("Guardar selección en bitácora", use_container_width=True, key="save_ledger_btn"):
            sel = st.session_state.get("news_selected_df", pd.DataFrame())
            if not sel.empty:
                sel2 = sel.copy()
                sel2["sorteo_aplicado"] = current_lottery
                p = _save_ledger(sel2, current_lottery)
                _save_csv(sel2, SEL_LAST)  # snapshot
                st.toast(f"Bitácora guardada: {p.name}", icon="🗂️")

        st.markdown("#### Papelera")
        cpa, cpb = st.columns(2)
        with cpa:
            if st.button("Ver", use_container_width=True, key="show_trash_btn"):
                _flag("__show_trash__"); st.stop()
        with cpb:
            if st.button("Ocultar", use_container_width=True, key="hide_trash_btn"):
                _flag("__hide_trash__"); st.stop()

    # ---------- Acopio (cacheado) ----------
    @st.cache_data(show_spinner=True)
    def _run_acopio() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
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

    df_raw, df_sel, logs = _run_acopio()
    # Mantén selección disponible para envíos/botones
    st.session_state["news_selected_df"] = df_sel.copy()

    # ---------- Encabezado de estado (estructura fija) ----------
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Fuentes", f"{len(logs.get('sources', []))}")
    s2.metric("Candidatas (bruto)", f"{len(df_raw)}")
    s3.metric("Seleccionadas", f"{len(df_sel)}")
    s4.metric("Ventana (h)", f"{CFG['RECENCY_HOURS']}")
    s5.metric("Tiempo (s)", f"{logs.get('elapsed_sec', 0)}")

    # ---------- Barra de acciones sobre selección (estructura fija) ----------
    st.markdown("##### Acciones sobre selección")
    sel_ids = st.multiselect(
        "Selecciona ID(s) de noticia:",
        options=df_sel["id_noticia"].tolist(),
        key="news_sel_ids",
        label_visibility="collapsed"
    )

    b1, b2, b3, b4, b5 = st.columns(5)  # cantidad fija
    with b1:
        if st.button("📋 Copiar seleccionadas", key="copy_sel_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)][["titular","url","resumen"]]
            payload = "\n\n".join([f"• {r.titular}\n{r.url}\n{r.resumen}" for r in subset.itertuples()])
            st.code(payload)

   with b2:
        if st.button("🗑️ Cortar a Papelera", key="to_trash_btn"):
            to_trash = df_sel[df_sel["id_noticia"].isin(sel_ids)]
            if not to_trash.empty:
                _append_trash(to_trash, reason="manual_batch")
                # No alteramos df_sel aquí para mantener estable el layout
                st.toast(f"Enviadas a papelera: {len(to_trash)}", icon="🗑️")

    with b3:
        if st.button("🔡 → GEMATRÍA", key="to_gem_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)]
            p = _export_buffer(subset, "GEM") if not subset.empty else None
            st.toast(f"Batch a GEMATRÍA: {p.name if p else 'sin datos'}", icon="✅")

    with b4:
        if st.button("🌀 → SUBLIMINAL", key="to_sub_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)]
            p = _export_buffer(subset, "SUB") if not subset.empty else None
            st.toast(f"Batch a SUBLIMINAL: {p.name if p else 'sin datos'}", icon="✅")

    with b5:
        if st.button("📊 → T70", key="to_t70_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)].copy()
            if not subset.empty and "categorias_t70_ref" in subset.columns:
                subset["T70_map"] = subset["categorias_t70_ref"].map(_map_news_to_t70)
            p = _export_buffer(subset, "T70") if not subset.empty else None
            st.toast(f"Batch a T70: {p.name if p else 'sin datos'}", icon="✅")

    # ---------- Tablas (estructura estable) ----------
    st.markdown("###### Selección actual (ordenada por score y fecha)")
    st.dataframe(
        df_sel[[
            c for c in ["id_noticia","fecha_dt","fuente","titular","_score_es"]
            if c in df_sel.columns
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("###### Log de fuentes")
    log_df = pd.DataFrame(logs.get("sources", []))
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin logs de fuentes.")

    # ---------- Papelera (vista opcional y estable) ----------
    if st.session_state.get("__show_trash_mode__", False):
        st.markdown("#### Papelera")
        trash_df = _load_trash()
        if trash_df.empty:
            st.info("Papelera vacía por ahora.")
        else:
            st.dataframe(trash_df, use_container_width=True, hide_index=True) 
