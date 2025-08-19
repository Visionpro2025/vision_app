import streamlit as st
import pandas as pd

# Título general
st.title("🔮 Sistema Predictivo Visión")

# Menú lateral
menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    ["Inicio", "Visión", "Tabla T70"]
)

# Secciones
if menu == "Inicio":
    st.write("Bienvenido a la App del sistema Visión 🚀")

elif menu == "Visión":
    st.write("Aquí estará la lógica principal del sistema Visión.")

elif menu == "Tabla T70":
    st.subheader("📊 Tabla T70")
    try:
        df = pd.read_csv("T70.csv")
        st.dataframe(df)
    except Exception as e:
        st.error(f"No se pudo cargar T70.csv: {e}")