# modules/noticias_module.py — Acopio Emoción Social (USA) · Día del protocolo (Cuba)
# - Amplio (RSS + Google News + Bing News), real (feeds públicos), sin inventos.
# - Concurrencia, listas editables (__CONFIG/*.txt), bloqueo de spam/agregadores.
# - Filtro ESTRICTO: SOLO noticias del "día del protocolo" según hora de Cuba (America/Havana).
# - Scoring emocional + relevancia + recencia, dedup semántica, límite por fuente.
# - UI: reloj Cuba, KPIs, papelera, bitácora, buffers (GEM/SUBLIMINAL/T70), depuración, export CSV/JSON.
# - Red: requests con timeouts y reintentos antes de parsear via feedparser.
# - Caché: implementación MANUAL con TTL dinámico (sin decoradores).

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import re, time, hashlib, io, json
import feedparser
import requests
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
    "RECENCY_HOURS": 72,         # ventana de recencia dura
    "MIN_TOKENS": 8,             # tamaño mínimo de texto útil
    "MAX_PER_SOURCE": 4,         # diversidad por dominio
    "SEMANTIC_ON": True,         # deduplicación semántica
    "SEMANTIC_THR": 0.82,        # umbral coseno TF-IDF
    "SOFT_DEDUP_NORM": True,     # normalización de titulares fallback
    "MAX_WORKERS": 12,           # concurrencia de fetch
    "STRICT_SAME_DAY": True,     # SOLO día del protocolo (Cuba)
    "HTTP_TIMEOUT": 8,           # seg. por petición RSS/News
    "HTTP_RETRIES": 3,           # reintentos por URL
    "CACHE_TTL_SEC": 300,        # objetivo de TTL (usado por caché manual)
}

# Bloqueo de agregadores/duplicadores (base)
SPAM_BLOCK_BASE = [
    "news.google.com", "feedproxy.google.com", "news.yahoo.com", "bing.com"
]

# =================== Config externo (listas editables) ===================
CONFIG_DIR = ROOT / "__CONFIG"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
RSS_TXT = CONFIG_DIR / "rss_sources.txt"
GNEWS_TXT = CONFIG_DIR / "gnews_queries.txt"
BING_TXT = CONFIG_DIR / "bing_queries.txt"
BLOCKED_TXT = CONFIG_DIR / "blocked_domains.txt"

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

def _load_blocked_domains() -> list[str]:
    try:
        if BLOCKED_TXT.exists():
            return [ln.strip().lower() for ln in BLOCKED_TXT.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    except Exception:
        pass
    return []

def _save_blocked_domains(domains: list[str]) -> None:
    try:
        uniq = sorted(set([d.strip().lower() for d in domains if d.strip()]))
        BLOCKED_TXT.write_text("\n".join(uniq) + "\n", encoding="utf-8")
    except Exception:
        pass

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

def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8")
    return buf.getvalue().encode("utf-8")

def _to_json_bytes(df: pd.DataFrame) -> bytes:
    def _ser(o):
        if isinstance(o, pd.Timestamp):
            if o.tzinfo is None:
                return o.tz_localize("UTC").isoformat()
            return o.isoformat()
        return str(o)
    data = json.loads(df.to_json(orient="records", date_unit="s"))
    return json.dumps(data, ensure_ascii=False, default=_ser, indent=2).encode("utf-8")

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
    if any(flag in t for tflag in ["breaking", "última hora", "urgente"] for flag in [t]):
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
        from sklearn.metrics.pairwise import cosine_similarity as _cos
    except Exception:
        return _soft_dedup(df)
    texts = (df["titular"].fillna("") + " " + df["resumen"].fillna("")).tolist()
    vec = TfidfVectorizer(max_features=25000, ngram_range=(1,2), lowercase=True, strip_accents="unicode")
    X = vec.fit_transform(texts)
    sim = _cos(X, dense_output=False)
    keep, removed = [], set()
    n = len(df)
    for i in range(n):
        if i in removed: continue
        keep.append(i)
        row = sim.getrow(i)
        near = row.nonzero()[1]
        for j in near:
            if j != i and row[0, j] >= thr:
                removed.add(j)
    return df.iloc[keep].copy()
# =================== Fetch ===================
def _parse_rss_bytes(content: bytes, src_url: str) -> list[dict]:
    data = feedparser.parse(content)
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
            "raw_source": src_url,
        })
    return out

def _fetch_rss(url: str) -> list[dict]:
    headers = {"User-Agent":"Mozilla/5.0 (Vision-News/1.0)"}
    for attempt in range(1, CFG["HTTP_RETRIES"]+1):
        try:
            r = requests.get(url, headers=headers, timeout=CFG["HTTP_TIMEOUT"])
            if r.status_code and r.status_code >= 400:
                continue
            return _parse_rss_bytes(r.content, url)
        except Exception:
            if attempt == CFG["HTTP_RETRIES"]:
                return []
            time.sleep(0.4 * attempt)
    return []

def _fetch_all_sources(strict_same_day: bool | None = None,
                       recency_hours_override: int | None = None,
                       extra_blocklist: list[str] | None = None) -> tuple[pd.DataFrame, dict]:
    started = time.time()
    logs = {"sources": [], "errors": []}

    if strict_same_day is None:
        strict_same_day = CFG["STRICT_SAME_DAY"]
    rec_hours = int(recency_hours_override) if recency_hours_override else CFG["RECENCY_HOURS"]

    persisted_block = set(_load_blocked_domains())
    block = set(SPAM_BLOCK_BASE) | persisted_block | set([b.strip().lower() for b in (extra_blocklist or []) if b.strip()])
    logs["blocked_domains_persisted"] = sorted(list(persisted_block))

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
        df = df[~df["fuente"].isin(block)]

        df["fecha_dt"] = pd.to_datetime(df["fecha_dt"], utc=True, errors="coerce")
        df = df[df["fecha_dt"].notna()]

        # Filtro de recencia dura
        cutoff = _now_utc() - timedelta(hours=rec_hours)
        df = df[df["fecha_dt"] >= cutoff]

        # Filtro “mismo día Cuba” (condicional)
        if strict_same_day:
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

        df = df.drop(columns=["_date_cuba"], errors="ignore")

    logs["elapsed_sec"] = round(time.time() - started, 2)
    logs["recency_hours_used"] = rec_hours
    logs["strict_same_day"] = bool(strict_same_day)
    logs["blocked_domains_effective"] = sorted(list(block))
    return df, logs

# =================== Scoring y límite por fuente ===================
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

def _validate_schema(df: pd.DataFrame) -> tuple[bool, list[str]]:
    required = ["id_noticia","titular","resumen","url","fecha_dt","fuente","pais","_score_es"]
    missing = [c for c in required if c not in df.columns]
    return (len(missing) == 0, missing)

# =================== Health Check ===================
def _health_check(n_to_test: int = 5) -> pd.DataFrame:
    urls = []
    urls.extend(RSS_SOURCES[:max(0, n_to_test-2)])
    if GNEWS_QUERIES:
        urls.append(_gnews_rss_url(GNEWS_QUERIES[0]))
    if BING_QUERIES:
        urls.append(_bingnews_rss_url(BING_QUERIES[0]))

    rows = []
    headers = {"User-Agent":"Mozilla/5.0 (Vision-News/1.0)"}
    for u in urls:
        t0 = time.time()
        status = "ok"; code = None; items = 0
        try:
            r = requests.get(u, headers=headers, timeout=CFG["HTTP_TIMEOUT"])
            code = r.status_code
            if code and code >= 400:
                status = "http_error"
            else:
                parsed = feedparser.parse(r.content)
                items = len(getattr(parsed, "entries", []) or [])
        except requests.Timeout:
            status = "timeout"
        except Exception:
            status = "error"
        dt = round(time.time()-t0, 2)
        rows.append({"source": u, "status": status, "http_code": code, "latency_s": dt, "items": items})
    return pd.DataFrame(rows)
   # =================== UI principal (con caché manual dinámica) ===================
def _cache_get() -> dict | None:
    return st.session_state.get("__news_cache__", None)

def _cache_set(payload: dict):
    st.session_state["__news_cache__"] = payload

def _run_pipeline_manual(strict_flag: bool, rec_hours: int, extra_blocklist: list[str], ttl_sec: int
                         ) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    # Clave de caché dependiente de parámetros + día Cuba (para coherencia operativa)
    cache_key = {
        "strict": bool(strict_flag),
        "rec_hours": int(rec_hours),
        "extra_blocklist": sorted([b.strip().lower() for b in (extra_blocklist or [])]),
        "day_cu": _today_cuba_date_str(),
    }
    now_ts = time.time()
    cache = _cache_get()
    if cache and cache.get("key") == cache_key and (now_ts - cache.get("created_ts", 0)) < ttl_sec:
        return cache["df_raw"], cache["df_sel"], cache["logs"]

    # Ejecutar pipeline
    df_raw, logs = _fetch_all_sources(
        strict_same_day=cache_key["strict"],
        recency_hours_override=cache_key["rec_hours"],
        extra_blocklist=cache_key["extra_blocklist"],
    )
    if df_raw.empty:
        df_sel = df_raw
    else:
        df = _score_emocion_social(df_raw)
        if CFG["SEMANTIC_ON"]:
            df = _semantic_dedup(df, CFG["SEMANTIC_THR"])
        if CFG["SOFT_DEDUP_NORM"]:
            df = _soft_dedup(df)
        df = _limit_per_source(df, CFG["MAX_PER_SOURCE"])
        df_sel = df.sort_values(by=["_score_es", "fecha_dt"], ascending=[False, False]).reset_index(drop=True)
        _save_csv(df_raw, RAW_LAST)
        _save_csv(df_sel, SEL_LAST)

    payload = {"key": cache_key, "created_ts": now_ts, "df_raw": df_raw, "df_sel": df_sel, "logs": logs}
    _cache_set(payload)
    return df_raw, df_sel, logs

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
            _cache_set(None)
            st.rerun()

        st.markdown("#### Depuración (temporal)")
        relax = st.toggle(
            "Ignorar 'mismo día Cuba' (solo usa ventana de recencia)",
            value=False,
            help="Úsalo solo para auditar. No cambia el decreto por defecto.",
            key="toggle_relax_same_day",
        )
        st.session_state["_relax_same_day"] = bool(relax)

        rec_override = st.slider(
            "Ventana de recencia (horas)",
            min_value=6,
            max_value=168,
            value=CFG["RECENCY_HOURS"],
            step=6,
            help="Solo depuración. No persiste en CFG.",
            key="slider_recency_hours",
        )

        cache_ttl = st.slider(
            "TTL de caché (segundos)",
            min_value=30,
            max_value=1800,
            value=CFG["CACHE_TTL_SEC"],
            step=30,
            help="Tiempo durante el cual se reusa el resultado del pipeline.",
            key="slider_cache_ttl",
        )
        # Si cambia el TTL, invalidamos la caché para que tome efecto de inmediato
        if "prev_cache_ttl" not in st.session_state:
            st.session_state["prev_cache_ttl"] = cache_ttl
        if cache_ttl != st.session_state["prev_cache_ttl"]:
            st.session_state["prev_cache_ttl"] = cache_ttl
            _cache_set(None)
            st.toast("Caché reiniciada por cambio de TTL.", icon="♻️")

        st.markdown("#### Bloquear dominios (sesión)")
        blocked = st.text_input(
            "Listado separados por coma",
            value="",
            key="blocked_domains_input",
            help="Ej: example.com, another.com",
        )
        extra_block = [x.strip().lower() for x in blocked.split(",") if x.strip()]

        st.markdown("#### Bloqueo persistente (__CONFIG/blocked_domains.txt)")
        current_persisted = ", ".join(_load_blocked_domains()) or "(ninguno)"
        st.caption(f"Actual: {current_persisted}")
        new_persist = st.text_input(
            "Agregar dominios (coma)",
            value="",
            key="blocked_domains_persist_add",
        )
        if st.button("💾 Guardar en __CONFIG", use_container_width=True, key="btn_save_blocked"):
            to_save = _load_blocked_domains() + [x.strip().lower() for x in new_persist.split(",") if x.strip()]
            _save_blocked_domains(to_save)
            st.toast("Bloqueo persistente actualizado.", icon="✅")
            st.rerun()

        st.markdown("#### Descargas")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            if RAW_LAST.exists():
                st.download_button("Acopio bruto (CSV)", RAW_LAST.read_bytes(), "acopio_bruto_ultimo.csv",
                                   use_container_width=True, key="dl_raw")
        with col_dl2:
            if SEL_LAST.exists():
                st.download_button("Selección ES (CSV)", SEL_LAST.read_bytes(), "seleccion_es_ultima.csv",
                                   use_container_width=True, key="dl_sel")

        st.markdown("#### Health check")
        if st.button("📶 Probar 5 fuentes", use_container_width=True, key="btn_health"):
            df_health = _health_check(5)
            st.dataframe(df_health, use_container_width=True, hide_index=True)

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
                    if "T70_map" not in sel2.columns:
                        sel2["T70_map"] = ""
                    p = _export_buffer(sel2, "T70")
                    st.toast(f"T70: {p.name if p else 'sin datos'}", icon="✅")

        st.markdown("#### Bitácora (por sorteo)")
        current_lottery = st.session_state.get("current_lottery", "GENERAL")
        if st.button("Guardar selección en bitácora", use_container_width=True, key="save_ledger"):
            sel = st.session_state.get("news_selected_df", pd.DataFrame())
            if not sel.empty:
                ok, missing = _validate_schema(sel.assign(_score_es=sel.get("_score_es", 0)))
                if not ok:
                    st.warning(f"Selección con esquema incompleto: faltan {missing}")
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

    # ===== Ejecutar pipeline con caché manual =====
    strict_flag = not st.session_state.get("_relax_same_day", False)
    rec_hours = st.session_state.get("slider_recency_hours", CFG["RECENCY_HOURS"])
    ttl_sec = st.session_state.get("slider_cache_ttl", CFG["CACHE_TTL_SEC"])

    df_raw, df_sel, logs = _run_pipeline_manual(strict_flag, rec_hours, extra_block, ttl_sec)
    st.session_state["news_selected_df"] = df_sel.copy()

    if st.session_state.get("_relax_same_day", False):
        st.warning(
            "Depuración activa: se IGNORA el filtro de **mismo día Cuba**. "
            f"Solo se aplica la ventana de recencia de {logs.get('recency_hours_used', CFG['RECENCY_HOURS'])} horas.",
            icon="⚠️"
        )

    # Encabezado KPIs
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Fuentes", f"{len(logs.get('sources', []))}")
    m2.metric("Bruto (filtro actual)", f"{len(df_raw)}")
    m3.metric("Seleccionadas", f"{len(df_sel)}")
    m4.metric("Ventana (h)", f"{logs.get('recency_hours_used', CFG['RECENCY_HOURS'])}")
    m5.metric("Tiempo (s)", f"{logs.get('elapsed_sec', 0)}")

    if df_raw.empty:
        st.warning("No se obtuvieron noticias con la configuración actual. Verifica conectividad o ajusta recencia.", icon="⛔")
    elif df_sel.empty:
        st.info("Hay acopio bruto pero la selección quedó vacía tras filtros. Revisa MIN_TOKENS, límite por fuente o keywords.", icon="ℹ️")

    # Expanders de auditoría
    with st.expander("📦 Selección (ordenada por score y fecha)"):
        if not df_sel.empty:
            view = df_sel.copy()
            view["fecha_cuba"] = view["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d %H:%M:%S")
            view["hace_horas"] = ((_now_utc() - view["fecha_dt"]).dt.total_seconds()/3600).round(1)
            st.dataframe(view[["id_noticia","titular","fuente","fecha_cuba","hace_horas","_score_es"]], use_container_width=True, hide_index=True)
        else:
            st.write("—")

    with st.expander("🧱 Acopio bruto (auditoría)"):
        if not df_raw.empty:
            rawv = df_raw.copy()
            rawv["fecha_cuba"] = rawv["fecha_dt"].dt.tz_convert(ZoneInfo(PROTOCOL_TZ)).dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(rawv[["titular","fuente","fecha_cuba","url","resumen"]], use_container_width=True, hide_index=True)
        else:
            st.write("—")

    with st.expander("🧩 Logs del acopio"):
        try:
            st.markdown(f"**Mismo día Cuba:** {logs.get('strict_same_day', True)}  |  **Ventana (h):** {logs.get('recency_hours_used')}")
            st.markdown("**Dominios bloqueados (persistentes)**")
            st.code(", ".join(logs.get("blocked_domains_persisted", [])))
            st.markdown("**Dominios bloqueados efectivos (base + persistentes + sesión)**")
            st.code(", ".join(logs.get("blocked_domains_effective", [])))
            df_src = pd.DataFrame(logs.get("sources", []))
            if not df_src.empty:
                st.markdown("**Fuentes procesadas**")
                st.dataframe(df_src, use_container_width=True, hide_index=True)
            errs = pd.DataFrame(logs.get("errors", []))
            if not errs.empty:
                st.markdown("**Errores**")
                st.dataframe(errs, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Logs no disponibles: {e}")

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
    st.markdown("#### Acciones sobre selección")
    sel_ids = st.multiselect("Selecciona ID(s) de noticia:", options=df_sel.get("id_noticia", []),
                             label_visibility="collapsed", key="ms_sel_ids")
    bar1, bar2, bar3 = st.columns(3)

    with bar1:
        if st.button("📋 Copiar/Ver seleccionadas", key="btn_copy_sel", use_container_width=True):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)][["titular", "url", "resumen"]].copy()
            if subset.empty:
                st.info("No hay filas seleccionadas.")
            else:
                st.success(f"{len(subset)} noticia(s) preparadas.")
                st.dataframe(subset, use_container_width=True, hide_index=True)
                text_block = "\n\n".join([f"• {r.titular}\n{r.url}\n{r.resumen}" for r in subset.itertuples(index=False)])
                st.text_area("Bloque de texto (selecciona y copia):", value=text_block, height=200)
                st.download_button("⬇️ CSV (subset)", data=_to_csv_bytes(subset),
                                   file_name=f"noticias_subset_{_ts()}.csv", use_container_width=True)
                st.download_button("⬇️ JSON (subset)", data=_to_json_bytes(subset),
                                   file_name=f"noticias_subset_{_ts()}.json", use_container_width=True)

    with bar2:
        motivo = st.text_input("Motivo papelera", value="manual", key="trash_reason")
        if st.button("🗑️ Enviar a papelera", key="btn_to_trash", use_container_width=True):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)].copy()
            if subset.empty:
                st.info("No hay filas seleccionadas.")
            else:
                _append_trash(subset, reason=motivo.strip() or "manual")
                st.toast(f"Enviadas {len(subset)} a papelera.", icon="🗑️")
                st.rerun()

    with bar3:
        dest = st.selectbox("Exportar a", options=["GEM","SUB","T70"], key="subset_dest")
        if st.button("🚚 Exportar subset", key="btn_export_subset", use_container_width=True):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)].copy()
            if subset.empty:
                st.info("No hay filas seleccionadas.")
            else:
                if dest == "T70" and "T70_map" not in subset.columns:
                    subset["T70_map"] = ""
                p = _export_buffer(subset, dest)
                st.toast(f"Exportado a {dest}: {p.name if p else 'sin datos'}", icon="✅")

    # Exportación de selección completa (JSON extra)
    if not df_sel.empty:
        st.markdown("#### Exportación de selección completa")
        st.download_button("⬇️ Selección ES (JSON)", data=_to_json_bytes(df_sel),
                           file_name=f"seleccion_es_{_ts()}.json", use_container_width=True) 
