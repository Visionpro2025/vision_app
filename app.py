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