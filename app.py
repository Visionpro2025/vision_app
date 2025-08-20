from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Visión", page_icon="🔮", layout="wide")

# ===== Título
st.title("🔮 Sistema Predictivo Visión")

# ===== Menú lateral (único)
menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    ["Inicio", "Visión", "Tabla T70", "Noticias", "Gematría", "Análisis del mensaje subliminal"]
)

# ===== Ruteo por módulo
if menu == "Inicio":
    st.write("Bienvenido a la App del sistema Visión 🚀")

elif menu == "Visión":
    st.write("Aquí estará la lógica principal del sistema Visión.")

elif menu == "Tabla T70":
    st.subheader("📊 Tabla T70")
    try:
        df_t70 = pd.read_csv("T70.csv", encoding="utf-8")
        st.dataframe(df_t70, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar T70.csv: {e}")
        st.info("Verifica que el archivo **T70.csv** exista en la raíz del repositorio.")

elif menu == "Noticias":
    import importlib
    import modules.noticias_module as noticias_module
    importlib.reload(noticias_module)   # recarga por si actualizas el módulo
    noticias_module.render_noticias()

elif menu == "Gematría":
    from modules.gematria import show_gematria
    show_gematria()

elif menu == "Análisis del mensaje subliminal":
    from modules.subliminal_module import render_subliminal
    render_subliminal()  

