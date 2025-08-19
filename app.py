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
# ===== Noticias
elif menu == "Noticias":
    st.subheader("🗞️ Bitácora de Noticias")

    # 1) Cargar noticias.csv si existe
    df_n = None
    try:
        df_n = pd.read_csv("noticias.csv", encoding="utf-8")
    except FileNotFoundError:
        st.warning("Aún no existe **noticias.csv**. Crea el archivo en el repositorio con el encabezado:")
        st.code(
            "id_noticia,fecha,sorteo,fuente,titular,resumen,url,etiquetas",
            language="text",
        )
    except Exception as e:
        st.error(f"No se pudo leer **noticias.csv**: {e}")

    # 2) Filtros y tabla (si se cargó)
    if df_n is not None and not df_n.empty:
        # Normalizar columnas esperadas
        expected_cols = ["id_noticia", "fecha", "sorteo", "fuente", "titular", "resumen", "url", "etiquetas"]
        faltantes = [c for c in expected_cols if c not in df_n.columns]
        if faltantes:
            st.error(f"Faltan columnas en noticias.csv: {faltantes}")
        else:
            # Convertir fecha a tipo fecha (si viene como texto)
            try:
                df_n["fecha"] = pd.to_datetime(df_n["fecha"]).dt.date
            except Exception:
                pass

            col1, col2, col3 = st.columns([1,1,2])
            with col1:
                sorteos = ["(Todos)"] + sorted([s for s in df_n["sorteo"].dropna().unique()])
                filtro_sorteo = st.selectbox("Sorteo", sorteos)
            with col2:
                # Rango simple por fecha (opcional)
                min_f = df_n["fecha"].min() if "fecha" in df_n else None
                max_f = df_n["fecha"].max() if "fecha" in df_n else None
                usar_fecha = st.checkbox("Filtrar por fecha", value=False)
                if usar_fecha and min_f and max_f:
                    f_desde = st.date_input("Desde", value=min_f, min_value=min_f, max_value=max_f)
                    f_hasta = st.date_input("Hasta", value=max_f, min_value=min_f, max_value=max_f)
                else:
                    f_desde, f_hasta = None, None
            with col3:
                buscar = st.text_input("Buscar en titular/resumen/etiquetas", "")

            # Aplicar filtros
            df_fil = df_n.copy()
            if filtro_sorteo != "(Todos)":
                df_fil = df_fil[df_fil["sorteo"] == filtro_sorteo]
            if f_desde and f_hasta and "fecha" in df_fil:
                df_fil = df_fil[(df_fil["fecha"] >= f_desde) & (df_fil["fecha"] <= f_hasta)]
            if buscar.strip():
                q = buscar.strip().lower()
                df_fil = df_fil[df_fil[["titular","resumen","etiquetas"]].astype(str).apply(
                    lambda r: any(q in x.lower() for x in r), axis=1
                )]

            st.caption(f"Mostrando {len(df_fil)} de {len(df_n)} noticias")
            st.dataframe(df_fil, use_container_width=True)

    st.divider()

    # 3) Plantilla para añadir nueva fila (edición se hace en GitHub)
    st.markdown("### ➕ Añadir nueva noticia (plantilla)")
    st.write(
        "Para **agregar** noticias, edita el archivo **noticias.csv** en GitHub y pega una nueva línea. "
        "Aquí tienes una plantilla lista:"
    )
    hoy = date.today().isoformat()
    # ID sugerido: N-YYYY-MM-DD-hhmmss
    id_sugerido = f"N-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    ejemplo_linea = (
        f"{id_sugerido},{hoy},MegaMillions,FuenteEjemplo,"
        f"Título de ejemplo,Descripción breve,https://ejemplo.com,politica;economia"
    )
    st.code(
        "id_noticia,fecha,sorteo,fuente,titular,resumen,url,etiquetas\n" + ejemplo_linea,
        language="text"
    )
    st.info(
        "💾 **Cómo guardarlo:** En GitHub → entra a **noticias.csv** → **Editar archivo** → "
        "pega la nueva línea al final → **Commit changes**. La app se actualizará con la próxima recarga."
    )