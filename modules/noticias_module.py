# modules/noticias_module.py — Acopio Emoción Social (USA)
# Mejorado: más fuentes (RSS, Google News, Bing News), concurrencia, listas editables
# Blindado contra errores de frontend (removeChild/NotFoundError).
# Función: acopio, scoring, deduplicación, bitácora, papelera y buffers para GEM/SUBLIMINAL/T70.

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re, time, csv, json, hashlib, requests, feedparser
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

# =================== Config ===================
CFG = {
    "RECENCY_HOURS": 120,    # ventana de 5 días
    "MIN_TOKENS": 8,         # tamaño mínimo de texto útil
    "MAX_PER_SOURCE": 4,     # diversidad por dominio
    "SEMANTIC_ON": True,
    "SEMANTIC_THR": 0.82,
    "SOFT_DEDUP_NORM": True,
}

SPAM_BLOCK = ["news.google.com", "feedproxy.google.com", "news.yahoo.com", "bing.com"]

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

# Defaults seguros
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
    "protest OR strike OR riot OR looting site:us",
    "shortage OR blackout OR curfew OR evacuation site:us",
    "boycott OR layoffs OR outage OR wildfire OR hurricane OR flood site:us",
    "mass shooting OR unrest OR clashes site:us",
    "protesta OR huelga OR disturbios OR saqueo sitio:us",
    "desabasto OR apagón OR toque de queda OR evacuación sitio:us",
    "boicot OR despidos OR tiroteo masivo sitio:us",
]
BING_QUERIES_DEFAULT = GNEWS_QUERIES_DEFAULT

# Listas cargadas desde __CONFIG o defaults
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
def _now_utc_str() -> str: return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
def _hash(text: str) -> str: return hashlib.sha256(text.encode("utf-8","ignore")).hexdigest()[:16]
def _domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        d = urlparse(url).netloc.lower()
        return d[4:] if d.startswith("www.") else d
    except: return ""
def _tokens(text: str) -> int: return len(re.findall(r"\w+", str(text or "")))
def _coerce_dt_from_feed(entry):
    try:
        tt = getattr(entry,"published_parsed",None) or getattr(entry,"updated_parsed",None)
        if tt: return datetime(*tt[:6],tzinfo=timezone.utc)
    except: pass
    return None
def _recency_factor(ts):
    if ts is None: return 0.7
    hours = (datetime.now(timezone.utc)-ts).total_seconds()/3600
    if hours<=24: return 1.0
    if hours<=72: return 0.9
    if hours<=120: return 0.8
    return 0.7

TRIGGERS = {"protest":1.0,"strike":1.0,"riot":1.0,"looting":1.0,"shortage":0.9,
"blackout":0.9,"curfew":1.0,"evacuation":0.9,"boycott":0.9,"mass shooting":1.0,
"unrest":0.9,"clashes":0.9,"layoffs":0.8,"outage":0.8,
"protesta":1.0,"huelga":1.0,"disturbios":1.0,"saqueo":1.0,"desabasto":0.9,
"apagón":0.9,"toque de queda":1.0,"evacuación":0.9,"boicot":0.9,"tiroteo":1.0,"despidos":0.8}

def _emo_heuristics(text: str) -> float:
    t=text.lower(); score=sum(w for k,w in TRIGGERS.items() if k in t)
    score+=0.1*t.count("!"); score+=0.15 if any(x in t for x in["breaking","última hora","urgente"]) else 0
    return min(score,3.0)/3.0

def _topic_relevance(text: str)->float:
    TOPICS={"salud":["hospital","infección","brote","vacuna","epidemia"],
    "economía":["inflación","desempleo","cierres","layoffs","crash"],
    "seguridad":["tiroteo","violencia","shooting","kidnapping"],
    "clima":["huracán","terremoto","inundación","heatwave","wildfire","hurricane","flood"],
    "política":["elecciones","protesta","congreso","impeachment"]}
    t=text.lower(); hits=sum(1 for kws in TOPICS.values() if any(k in t for k in kws))
    return min(0.2*hits,1.0)

def _source_weight(domain: str)->float:
    majors=["reuters","apnews","npr","bbc","abcnews","cbsnews","nytimes","wsj","guardian","nbcnews","latimes"]
    locals_=["miamiherald","chicagotribune","houstonchronicle"]
    if any(m in domain for m in majors): return 1.15
    if any(l in domain for l in locals_): return 1.05
    return 1.0

# =================== Deduplicación ===================
def _soft_dedup(df):
    if df.empty: return df
    base=df.copy(); base["_tit_norm"]=base["titular"].str.lower().str.replace(r"[\W_]+"," ",regex=True)
    return base.drop_duplicates("_tit_norm").drop(columns=["_tit_norm"],errors="ignore")

def _semantic_dedup(df,thr):
    if df.empty or len(df)==1: return df
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
    except: return _soft_dedup(df)
    texts=(df["titular"].fillna("")+" "+df["resumen"].fillna("")).tolist()
    X=TfidfVectorizer(max_features=20000,ngram_range=(1,2),strip_accents="unicode").fit_transform(texts)
    sim=cosine_similarity(X,dense_output=False)
    keep,removed=[],set()
    for i in range(len(df)):
        if i in removed: continue
        keep.append(i)
        near=[j for j in range(len(df)) if j!=i and sim[i, j]>=thr]
        removed.update(near)
    return df.iloc[keep].copy()

# =================== Fetch ===================
def _fetch_rss(url: str)->list[dict]:
    try:
        data=feedparser.parse(url,request_headers={"User-Agent":"Mozilla/5.0"})
        return [{
            "titular":getattr(e,"title",""),
            "resumen":re.sub("<[^<]+?>","",getattr(e,"summary","")or getattr(e,"description","")or ""),
            "url":getattr(e,"link",""),
            "fecha_dt":_coerce_dt_from_feed(e),
            "fuente":_domain(getattr(e,"link","")),
            "raw_source":url} for e in data.entries]
    except: return []

def _fetch_all_sources()->tuple[pd.DataFrame,dict]:
    started=time.time(); logs={"sources":[], "errors":[]}
    urls=RSS_SOURCES+[ _gnews_rss_url(q) for q in GNEWS_QUERIES ]+[ _bingnews_rss_url(q) for q in BING_QUERIES ]
    all_items=[]
    with ThreadPoolExecutor(max_workers=min(16,len(urls))) as ex:
        fut2src={ex.submit(_fetch_rss,u):u for u in urls}
        for fut in as_completed(fut2src):
            src=fut2src[fut]
            try:
                items=fut.result() or []
                logs["sources"].append({"source":src,"items":len(items)})
                all_items.extend(items)
            except Exception as e: logs["errors"].append({"source":src,"error":str(e)})
    df=pd.DataFrame(all_items)
    if not df.empty:
        df["fuente"]=df["fuente"].fillna("").str.lower().str.strip()
        df=df[~df["fuente"].isin(SPAM_BLOCK)]
        df["fecha_dt"]=pd.to_datetime(df["fecha_dt"],utc=True,errors="coerce")
        df=df[df["fecha_dt"].notna()]
        df["titular"]=df["titular"].fillna("").str.strip()
        df["resumen"]=df["resumen"].fillna("").str.strip()
        df["tokens"]=(df["titular"]+" "+df["resumen"]).map(_tokens)
        df=df[df["tokens"]>=CFG["MIN_TOKENS"]]
        cutoff=datetime.now(timezone.utc)-timedelta(hours=CFG["RECENCY_HOURS"])
        df=df[df["fecha_dt"]>=cutoff]
        df["id_noticia"]=df.apply(lambda r:_hash((r["titular"] or "")+(r["url"] or "")),axis=1)
        df["pais"]="US"; df["_texto"]=(df["titular"]+" "+df["resumen"]).str.strip()
    logs["elapsed_sec"]=round(time.time()-started,2)
    return df, logs

# =================== Scoring ===================
def _score_emocion_social(df):
    if df.empty: return df
    emos, recs, rels, srcw=[],[],[],[]
    for _,r in df.iterrows():
        txt=f"{r.get('titular','')} {r.get('resumen','')}"
        emos.append(_emo_heuristics(txt)); recs.append(_recency_factor(r.get("fecha_dt")))
        rels.append(_topic_relevance(txt)); srcw.append(_source_weight(r.get("fuente","")))
    df=df.copy()
    df["_emo"],df["_recency"],df["_rel"],df["_srcw"]=emos,recs,rels,srcw
    df["_score_es"]=0.35*df["_emo"]+0.20*df["_rel"]+0.20*df["_recency"]+0.20*df["_srcw"]+0.05
    return df

# =================== Persistencia ===================
def _ts()->str: return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
def _save_csv(df,path): path.parent.mkdir(parents=True,exist_ok=True); df.to_csv(path,index=False,encoding="utf-8")
def _append_trash(df_rows,reason="manual"):
    if df_rows.empty: return
    f=TRASH_DIR/"trash.csv"; df_rows=df_rows.copy(); df_rows["trash_reason"]=reason; df_rows["trash_ts"]=_now_utc_str()
    if f.exists():
        try: prev=pd.read_csv(f,dtype=str); df_rows=pd.concat([prev,df_rows],ignore_index=True)
        except: pass
    _save_csv(df_rows,f)
def _save_ledger(df_sel,lottery:str):
    folder=LEDGER_DIR/lottery/datetime.now(timezone.utc).strftime("%Y%m%d")
    folder.mkdir(parents=True,exist_ok=True); path=folder/f"bitacora_{_ts()}.csv"; _save_csv(df_sel,path); return path
def _export_buffer(df_rows,kind:str):
    if df_rows.empty: return None
    base={"GEM":BUFF_GEM,"SUB":BUFF_SUB,"T70":BUFF_T70}[kind]; base.mkdir(parents=True,exist_ok=True)
    path=base/f"news_batch_{_ts()}.csv"; _save_csv(df_rows,path); return path

# =================== UI principal ===================
def render_noticias():
    st.subheader("📰 Noticias · Emoción Social (USA)")
    st.caption(f"Última recarga: {_now_utc_str()}")

    # Sidebar
    with st.sidebar:
        if st.button("↻ Reacopiar ahora",use_container_width=True):
            st.cache_data.clear(); st.rerun()
        st.markdown("#### Descargas")
        if RAW_LAST.exists():
            st.download_button("Acopio bruto",RAW_LAST.read_bytes(),"acopio_bruto_ultimo.csv",use_container_width=True)
        if SEL_LAST.exists():
            st.download_button("Selección ES",SEL_LAST.read_bytes(),"seleccion_es_ultima.csv",use_container_width=True)

    @st.cache_data(show_spinner=True)
    def _run():
        df_raw,logs=_fetch_all_sources()
        if df_raw.empty: return df_raw,df_raw,logs
        df=_score_emocion_social(df_raw)
        if CFG["SEMANTIC_ON"]: df=_semantic_dedup(df,CFG["SEMANTIC_THR"])
        if CFG["SOFT_DEDUP_NORM"]: df=_soft_dedup(df)
        df=_limit_per_source(df,CFG["MAX_PER_SOURCE"])
        df=df.sort_values(["_score_es","fecha_dt"],ascending=[False,False]).reset_index(drop=True)
        _save_csv(df_raw,RAW_LAST); _save_csv(df,SEL_LAST)
        return df_raw,df,logs

    df_raw,df_sel,logs=_run()

    st.metric("Fuentes",len(logs.get("sources",[])))
    st.metric("Noticias brutas",len(df_raw))
    st.metric("Seleccionadas",len(df_sel))
    st.metric("Tiempo (s)",logs.get("elapsed_sec",0))

    st.dataframe(df_sel[["id_noticia","fecha_dt","fuente","titular","resumen"]],use_container_width=True,hide_index=True)
