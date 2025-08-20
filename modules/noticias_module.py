from pathlib import Path
import streamlit as st
import pandas as pd

# Columnas esperadas para noticias.csv
NEWS_COLUMNS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen","etiquetas",
    "nivel_emocional_diccionario","nivel_emocional_modelo","nivel_emocional_final",
    "noticia_relevante","categorias_t70_ref"
]

def _repo_root() -> Path:
    # modules/noticias_module.py → modules → repo_root
    return Path(__file__).resolve().parent.parent

def _load_csv_safe(path: Path):
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer {path.name}: {e}")
        return None

def render_noticias():
    st.subheader("📰 Noticias — bitácora del sorteo")

    repo_root = _repo_root()
    ruta = repo_root / "noticias.csv"
    st.caption(f"🔎 Ruta esperada: `{ruta}`")

    if not ruta.exists():
        st.error("No encuentro `noticias.csv` en la raíz del repositorio.")
        st.info("Súbelo al mismo nivel que `app.py` o ajusta la ruta aquí.")
        return

    df = _load_csv_safe(ruta)
    if df is None:
        return

    # Asegurar columnas fijas
    for c in NEWS_COLUMNS:
        if c not in df.columns:
            df[c] = ""

    # Normalizaciones
    df["noticia_relevante"] = df["noticia_relevante"].astype(str)

    st.success(f"Total noticias: {len(df)}")

    # ---- Filtros
    col1, col2, col3, col4 = st.columns([1,1,2,1])

    with col1:
        fechas = sorted([f for f in df["fecha"].dropna().unique() if f])
        fecha_sel = st.selectbox("Fecha", options=["(todas)"] + fechas, key="news_fecha")

    with col2:
        sorteos = sorted([s for s in df["sorteo"].dropna().unique() if s])
        sorteos_sel = st.multiselect("Sorteo(s)", options=sorteos, default=[], key="news_sorteo")

    with col3:
        q = st.text_input("Buscar en titular/resumen/etiquetas", value="", key="news_q").strip().lower()

    with col4:
        solo_relev = st.checkbox("Solo relevantes", value=False, key="news_relev")

    df_fil = df.copy()

    if fecha_sel != "(todas)":
        df_fil = df_fil[df_fil["fecha"] == fecha_sel]

    if sorteos_sel:
        df_fil = df_fil[df_fil["sorteo"].isin(sorteos_sel)]

    if q:
        mask = (
            df_fil["titular"].str.lower().str.contains(q, na=False) |
            df_fil["resumen"].str.lower().str.contains(q, na=False) |
            df_fil["etiquetas"].str.lower().str.contains(q, na=False)
        )
        df_fil = df_fil[mask]

    if solo_relev:
        df_fil = df_fil[df_fil["noticia_relevante"].str.lower().isin(["true","1","sí","si"])]

    st.info(f"Coincidencias tras filtros: {len(df_fil)}")
    st.dataframe(df_fil, use_container_width=True, hide_index=True)

    st.download_button(
        "⬇️ Descargar vista filtrada (CSV)",
        df_fil.to_csv(index=False).encode("utf-8"),
        file_name="noticias_filtrado.csv",
        mime="text/csv"
      )
