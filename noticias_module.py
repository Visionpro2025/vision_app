# modules/noticias_module.py — Noticias PRO (crudas → filtradas) + DEDUP SEMÁNTICA
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone, timedelta
import re
import pandas as pd
import streamlit as st

# === Semántica (TF-IDF cosine) ===
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# Rutas y constantes base
# =========================
ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "noticias.csv"                # crudas en la raíz del repo
OUT_DIR = ROOT / "__RUNS" / "NEWS"             # salidas filtradas/export
OUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Config por defecto (menos restrictiva)
# =========================
CFG_DEFAULT = {
    "RECENCY_DAYS": 5,          # ventana temporal
    "SENTIMENT_THRESHOLD": 0.48, # emoción mínima
    "DEDUP_SIMILARITY": 0.85,    # para dedup suave (titular normalizado)
    "MAX_PER_SOURCE": 4,         # diversidad por fuente
    "MIN_TOKENS": 20,            # longitud mínima
    # Semántica:
    "SEMANTIC_ON": True,         # activar deduplicación semántica
    "SEMANTIC_THRESHOLD": 0.82,  # umbral de similitud cosine TF-IDF
}

# Campos esperados mínimamente (ajusta si tu CSV usa otros nombres)
EXPECTED_COLS = [
    "id_noticia", "fecha", "sorteo", "pais", "fuente", "titular", "resumen",
    "etiquetas", "nivel_emocional_diccionario", "nivel_emocional_modelo",
    "nivel_emocional_final", "noticia_relevante", "categorias_t70_ref", "url"
]

# =========================
# Helpers
# =========================
@st.cache_data(show_spinner=False)
def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

@st.cache_data(show_spinner=False)
def _load_csv_safe(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8")
        return df
    except Exception:
        return pd.DataFrame()

def _coerce_datetime(s: pd.Series) -> pd.Series:
    try:
        return pd.to_datetime(s, errors="coerce", utc=True)
    except Exception:
        return pd.to_datetime(pd.Series([], dtype=str))

def _len_tokens(text: str) -> int:
    if not isinstance(text, str):
        return 0
    # conteo rápido por palabras/alfanuméricos
    return len(re.findall(r"\w+", text))

def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    # Garantiza columnas y tipado básico
    for c in EXPECTED_COLS:
        if c not in df.columns:
            df[c] = ""
    # fecha → datetime UTC
    df["fecha_dt"] = _coerce_datetime(df["fecha"])
    # tokens en titular+resumen
    df["tokens"] = (df["titular"].fillna("") + " " + df["resumen"].fillna("")).map(_len_tokens)
    # emoción final como float si existe (fallback a modelo/diccionario)
    def _emo(row) -> float:
        for key in ["nivel_emocional_final", "nivel_emocional_modelo", "nivel_emocional_diccionario"]:
            try:
                v = float(str(row.get(key, "")).replace(",", "."))
                if pd.notna(v):
                    return float(v)
            except Exception:
                continue
        return 0.0
    df["emo"] = df.apply(_emo, axis=1)
    # fuente limpia
    df["fuente"] = df["fuente"].fillna("").str.strip()
    # texto combinado para semántica
    df["_texto"] = (df["titular"].fillna("") + " " + df["resumen"].fillna("")).str.strip()
    return df

def _dedup_soft(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicación rápida por titular normalizado (barata y robusta).
    """
    if df.empty:
        return df
    base = df.copy()
    norm = base["titular"].fillna("").str.lower().str.replace(r"[\W_]+", " ", regex=True).str.strip()
    base["_tit_norm"] = norm
    base = base.drop_duplicates(subset=["_tit_norm"], keep="first")
    base = base.drop(columns=["_tit_norm"], errors="ignore")
    return base

@st.cache_data(show_spinner=False)
def _dedup_semantic(df: pd.DataFrame, sim_thr: float) -> pd.DataFrame:
    """
    Deduplicación semántica usando TF-IDF + cosine.
    Mantiene el PRIMER ítem de cada grupo de alta similitud y descarta near-duplicates.
    sim_thr recomendado: 0.80–0.90 (más alto = más agresivo).
    """
    if df.empty:
        return df

    texts = df["_texto"].fillna("").tolist()
    if len(texts) <= 1:
        return df

    # Vectorización ligera en español/inglés sin stopwords específicas (general)
    vec = TfidfVectorizer(
        max_features=20000,
        ngram_range=(1, 2),
        lowercase=True,
        strip_accents="unicode"
    )
    X = vec.fit_transform(texts)
    # Similaridad por filas (podría ser costoso con miles; aquí asumimos tamaño razonable)
    sim = cosine_similarity(X, dense_output=False)

    keep = []
    removed = set()
    n = len(df)
    for i in range(n):
        if i in removed:
            continue
        keep.append(i)
        # descartar j similares al i por encima del umbral
        # usamos sim[i, j] pero cuidando i!=j
        row = sim[i].toarray().ravel()  # fila densa
        similar_idxs = [j for j in range(n) if j != i and row[j] >= sim_thr]
        for j in similar_idxs:
            removed.add(j)

    out = df.iloc[keep].copy()
    return out

def _apply_filters(
    df: pd.DataFrame,
    days: int,
    emo_thr: float,
    min_tokens: int,
    max_per_source: int
) -> pd.DataFrame:
    if df.empty:
        return df
    now = datetime.now(timezone.utc)
    recent_cut = now - timedelta(days=days)

    # recencia
    m_recent = df["fecha_dt"].fillna(pd.Timestamp("1970-01-01", tz="UTC")) >= recent_cut

    # emoción mínima (>= umbral)
    m_emo = df["emo"].fillna(0.0) >= float(emo_thr)

    # tamaño mínimo (tokens)
    m_tokens = df["tokens"].fillna(0) >= int(min_tokens)

    out = df[m_recent & m_emo & m_tokens].copy()

    if out.empty:
        return out

    # limitar por fuente para diversidad
    if max_per_source > 0:
        out["_rank"] = out.groupby("fuente")["fecha_dt"].rank(ascending=False, method="first")
        out = out[out["_rank"] <= max_per_source].drop(columns=["_rank"])

    # ordenar por fecha desc y emoción desc
    out = out.sort_values(by=["fecha_dt", "emo"], ascending=[False, False])

    return out

def _export_df(df: pd.DataFrame, name_prefix: str) -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = OUT_DIR / f"{name_prefix}_{ts}.csv"
    df.to_csv(out_path, index=False, encoding="utf-8")
    return out_path

# =========================
# UI principal
# =========================
def render_noticias():
    st.subheader("📰 Noticias · Crudas y Filtro PRO")
    st.caption(f"Última recarga: {_utc_now_str()}")

    # --------- Carga de crudas ---------
    col_u1, col_u2 = st.columns([0.62, 0.38])
    with col_u1:
        st.markdown("**Crudas de entrada**")
        if RAW_CSV.exists():
            st.success(f"`noticias.csv` encontrado en raíz ({RAW_CSV})")
        else:
            st.error("Falta `noticias.csv` en la raíz del proyecto.")

        with st.expander("Subir/Actualizar `noticias.csv`", expanded=not RAW_CSV.exists()):
            upl = st.file_uploader("Selecciona un CSV con noticias crudas", type=["csv"])
            if upl is not None:
                RAW_CSV.write_bytes(upl.getvalue())
                st.success("`noticias.csv` actualizado en la raíz.")
                st.cache_data.clear()
                st.rerun()
    with col_u2:
        st.markdown("**Acciones rápidas**")
        if RAW_CSV.exists():
            st.download_button(
                "Descargar copia de `noticias.csv`",
                data=RAW_CSV.read_bytes(),
                file_name="noticias.csv",
                use_container_width=True,
            )

    # --------- Lectura + normalización ---------
    df_raw = _load_csv_safe(RAW_CSV)
    df_raw = _normalize_df(df_raw) if not df_raw.empty else df_raw

    # --------- Tabs de trabajo ---------
    tabs = st.tabs([
        "📥 Crudas (preview)",
        "🧪 Filtrado",
        "💾 Exportaciones",
        "🧰 Diagnóstico",
    ])

    # ===== Tab 0: crudas =====
    with tabs[0]:
        st.markdown("**Vista rápida de las crudas (con tipado y métricas básicas):**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Filas", f"{len(df_raw)}")
        c2.metric("Fuentes únicas", f"{df_raw['fuente'].nunique() if not df_raw.empty else 0}")
        c3.metric("Con fecha válida", f"{df_raw['fecha_dt'].notna().sum() if not df_raw.empty else 0}")
        c4.metric("Con tokens ≥ 1", f"{(df_raw['tokens']>0).sum() if not df_raw.empty else 0}")

        q = st.text_input("🔎 Buscar (titular/resumen/etiquetas)", value="")
        df_view = df_raw.copy()
        if q.strip():
            ql = q.strip().lower()
            mask = (
                df_view["titular"].fillna("").str.lower().str.contains(ql) |
                df_view["resumen"].fillna("").str.lower().str.contains(ql) |
                df_view["etiquetas"].fillna("").str.lower().str.contains(ql)
            )
            df_view = df_view[mask]
        st.dataframe(df_view, use_container_width=True, height=420)

    # ===== Tab 1: filtrado =====
    with tabs[1]:
        st.markdown("**Configurar filtro (menos restrictivo por defecto)**")
        # Ajustes avanzados en expander
        with st.expander("⚙️ Ajustes avanzados", expanded=False):
            colA, colB = st.columns(2)
            with colA:
                recency_days = st.slider("Días recientes", 1, 14, CFG_DEFAULT["RECENCY_DAYS"])
                emo_thr = st.slider("Umbral de emoción mínima", 0.0, 1.0, CFG_DEFAULT["SENTIMENT_THRESHOLD"], 0.01)
                min_tokens = st.slider("Mínimo de tokens (titular+resumen)", 0, 80, CFG_DEFAULT["MIN_TOKENS"], 1)
            with colB:
                # Switch semántico + umbral
                use_sem = st.toggle("Deduplicación semántica (TF-IDF cosine)", value=CFG_DEFAULT["SEMANTIC_ON"])
                sem_thr = st.slider("Umbral semántico (0.80–0.90 ≈ fuerte)", 0.70, 0.98, CFG_DEFAULT["SEMANTIC_THRESHOLD"], 0.01)
                max_per_source = st.slider("Máximo por fuente", 0, 10, CFG_DEFAULT["MAX_PER_SOURCE"], 1)
                top_n = st.number_input("Top N tras ordenar por fecha/emoción (0 = sin límite)", 0, 2000, 0, 1)

        # Deduplicación (elige pipeline)
        if use_sem:
            df_dedup = _dedup_semantic(df_raw, sim_thr=float(sem_thr))
        else:
            df_dedup = _dedup_soft(df_raw)

        # Filtros principales
        df_f = _apply_filters(
            df_dedup,
            days=int(recency_days),
            emo_thr=float(emo_thr),
            min_tokens=int(min_tokens),
            max_per_source=int(max_per_source)
        )

        if top_n and top_n > 0:
            df_f = df_f.head(int(top_n))

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Crudas", f"{len(df_raw)}")
        c2.metric("Post-dedup", f"{len(df_dedup)}")
        c3.metric("Filtradas", f"{len(df_f)}")
        c4.metric("Fuentes en filtradas", f"{df_f['fuente'].nunique() if not df_f.empty else 0}")

        st.dataframe(df_f, use_container_width=True, height=440)

        # Export
        colE1, colE2, colE3 = st.columns(3)
        with colE1:
            if not df_f.empty and st.button("💾 Exportar filtradas", use_container_width=True):
                out = _export_df(df_f, "NOTICIAS_FILTRADAS")
                st.success(f"Exportado: {out.relative_to(ROOT)}")
        with colE2:
            if not df_dedup.empty and st.button("💾 Exportar deduplicadas", use_container_width=True):
                out = _export_df(df_dedup, "NOTICIAS_DEDUP")
                st.success(f"Exportado: {out.relative_to(ROOT)}")
        with colE3:
            if not df_raw.empty and st.button("💾 Exportar crudas (snapshot)", use_container_width=True):
                out = _export_df(df_raw, "NOTICIAS_CRUDAS_SNAPSHOT")
                st.success(f"Exportado: {out.relative_to(ROOT)}")

    # ===== Tab 2: exportaciones =====
    with tabs[2]:
        st.markdown("**Histórico de exportaciones (archivos en `__RUNS/NEWS`)**")
        files = sorted(OUT_DIR.glob("*.csv"))
        if not files:
            st.info("Aún no hay exportaciones.")
        else:
            for f in files:
                st.markdown(f"- `{f.name}` — {datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')}")
            st.caption("Exporta desde la pestaña **🧪 Filtrado**.")

    # ===== Tab 3: diagnóstico =====
    with tabs[3]:
        st.markdown("**Revisión de estructura y columnas**")
        if df_raw.empty:
            st.warning("No hay datos en `noticias.csv` para diagnosticar.")
        else:
            missing = [c for c in EXPECTED_COLS if c not in df_raw.columns]
            if missing:
                st.error(f"Faltan columnas: {missing}")
            else:
                st.success("Estructura OK — se detectaron todas las columnas esperadas.")
            st.caption("Consejo: si cambiaste nombres de columnas en tu pipeline, ajusta EXPECTED_COLS.")
