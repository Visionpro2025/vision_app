import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Visión", page_icon="🔮", layout="wide")

# ===== Título general
st.title("🔮 Sistema Predictivo Visión")

# ===== Menú lateral
menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    ["Inicio", "Visión", "Tabla T70", "Noticias"]
)

# ===== Inicio
if menu == "Inicio":
    st.write("Bienvenido a la App del sistema Visión 🚀")

# ===== Visión (placeholder por ahora)
elif menu == "Visión":
    st.write("Aquí estará la lógica principal del sistema Visión.")

# ===== Tabla T70
elif menu == "Tabla T70":
    st.subheader("📊 Tabla T70")
    try:
        df_t70 = pd.read_csv("T70.csv", encoding="utf-8")
        st.dataframe(df_t70, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar T70.csv: {e}")
        st.info("Verifica que el archivo **T70.csv** exista en el repositorio (carpeta raíz).")

# ===== Noticias (bitácora)
elif menu == "Noticias":
    st.subheader("🗞️ Noticias — bitácora del sorteo")

    # Opciones básicas
    sorteos_disponibles = ["MegaMillions", "Powerball", "Otro"]

    # Intentar cargar el CSV
    try:
        df_news = pd.read_csv("noticias.csv", encoding="utf-8")
        # Normalizar columnas esperadas
        columnas = ["id_noticia","fecha","sorteo","fuente","titular","resumen","url","etiquetas"]
        faltantes = [c for c in columnas if c not in df_news.columns]
        for c in faltantes:
            df_news[c] = ""
        df_news = df_news[columnas]
    except Exception as e:
        st.warning("No se pudo leer **noticias.csv** (aún no existe o está vacío).")
        st.info("Crea el archivo `noticias.csv` con la línea de encabezados:")
        st.code("id_noticia,fecha,sorteo,fuente,titular,resumen,url,etiquetas", language="csv")
        st.caption(f"Detalle técnico: {e}")
        df_news = pd.DataFrame(columns=["id_noticia","fecha","sorteo","fuente","titular","resumen","url","etiquetas"])

    # ---- Filtros
    with st.expander("🔎 Filtros", expanded=True):
        colF1, colF2 = st.columns([1,1])
        with colF1:
            fecha_min = st.date_input("Desde", value=date.today())
        with colF2:
            fecha_max = st.date_input("Hasta", value=date.today())

        sel_sorteos = st.multiselect("Sorteo(s)", options=sorteos_disponibles, default=sorteos_disponibles)
        texto = st.text_input("Buscar en titular / resumen / etiquetas", "")

    # Aplicar filtros si hay datos
    if not df_news.empty:
        # Convertir fecha a tipo fecha si viene como texto
        try:
            df_news["fecha"] = pd.to_datetime(df_news["fecha"]).dt.date
        except Exception:
            pass

        mask_fecha = True
        if "fecha" in df_news.columns:
            mask_fecha = (df_news["fecha"] >= fecha_min) & (df_news["fecha"] <= fecha_max)

        mask_sorteo = df_news["sorteo"].isin(sel_sorteos) if "sorteo" in df_news.columns else True

        if texto:
            texto_low = texto.lower()
            campos = df_news[["titular","resumen","etiquetas"]].fillna("").astype(str).apply(lambda s: s.str.lower())
            mask_texto = campos.apply(lambda r: (texto_low in r["titular"]) or (texto_low in r["resumen"]) or (texto_low in r["etiquetas"]), axis=1)
        else:
            mask_texto = True

        df_filtrado = df_news[mask_fecha & mask_sorteo & mask_texto].copy()
        st.write(f"Resultados: **{len(df_filtrado)}**")
        st.dataframe(df_filtrado, use_container_width=True)

        # Descargar CSV actual
        csv_bytes = df_news.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar noticias.csv", data=csv_bytes, file_name="noticias.csv", mime="text/csv")
    else:
        st.info("Aún no hay noticias registradas.")

    # ---- Plantilla para registrar una noticia (edición manual en GitHub)
    st.divider()
    st.markdown("### ➕ Plantilla para agregar una fila a `noticias.csv`")

    colP1, colP2 = st.columns([1,1])
    with colP1:
        fecha_new = st.date_input("Fecha de la noticia", value=date.today(), key="fecha_new")
        sorteo_new = st.selectbox("Sorteo", options=sorteos_disponibles, index=0, key="sorteo_new")
        fuente_new = st.text_input("Fuente (medio/sitio)", "Reuters", key="fuente_new")
    with colP2:
        titular_new = st.text_input("Titular", "Ejemplo de titular", key="titular_new")
        resumen_new = st.text_area("Resumen breve", "Descripción breve de la noticia", key="resumen_new")
        url_new = st.text_input("URL", "https://ejemplo.com", key="url_new")

    etiquetas_new = st.text_input("Etiquetas (separadas por `;`)", "politica;economia", key="etiquetas_new")

    # Generar ID simple (puedes cambiar la lógica luego)
    nuevo_id = f"N-{fecha_new.isoformat()}-1"

    linea_csv = f"{nuevo_id},{fecha_new.isoformat()},{sorteo_new},{fuente_new},{titular_new},{resumen_new},{url_new},{etiquetas_new}"
    st.markdown("Copia y pega esta **línea CSV** en `noticias.csv` (debajo del encabezado) usando GitHub → **Add file / Edit file**:")
    st.code(linea_csv, language="csv")

    st.caption("💡 Recuerda: la **interpretación numérica** (gematría/mensaje subliminal) se hace luego en el módulo de *Noticias Numéricas*, usando la T70 como referencia.")