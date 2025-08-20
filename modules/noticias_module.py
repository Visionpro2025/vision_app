from pathlib import Path
import streamlit as st
import pandas as pd

NEWS_COLUMNS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen","etiquetas",
    "nivel_emocional_diccionario","nivel_emocional_modelo","nivel_emocional_final",
    "noticia_relevante","categorias_t70_ref"
]

def render_noticias():
    st.subheader("📰 Noticias — bitácora del sorteo")

    # --- Diagnóstico explícito de rutas
    try:
        mod_path = Path(__file__).resolve()
    except Exception:
        mod_path = Path.cwd()
    repo_root = mod_path.parent.parent
    ruta_a = repo_root / "noticias.csv"           # opción 1 (recomendada)
    ruta_b = Path.cwd() / "noticias.csv"          # opción 2 (por si el cwd difiere)

    st.caption(f"📁 módulo: {mod_path}")
    st.caption(f"🔎 intento A: {ruta_a} | existe={ruta_a.exists()}")
    st.caption(f"🔎 intento B: {ruta_b} | existe={ruta_b.exists()}")

    # --- Elegir la que exista
    if ruta_a.exists():
        ruta = ruta_a
    elif ruta_b.exists():
        ruta = ruta_b
    else:
        st.error("No encuentro `noticias.csv` ni en la raíz del repo ni en el directorio actual.")
        st.info("Colócalo junto a `app.py` con el nombre exacto: noticias.csv (minúsculas).")
        return

    # --- Carga robusta con mensajes claros
    try:
        df = pd.read_csv(ruta, dtype=str, encoding="utf-8")
        st.success(f"✅ Cargado: {ruta.name} | filas={len(df)} | columnas={list(df.columns)}")
    except Exception as e:
        st.error(f"❌ Error leyendo {ruta}: {e}")
        return

    # Asegurar columnas fijas para no romper la UI
    for c in NEWS_COLUMNS:
        if c not in df.columns:
            df[c] = ""

    # ---- Filtros básicos (si llega aquí, ya debería verse todo)
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