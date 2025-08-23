import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Visión · Carga mínima", layout="wide")
st.title("Visión · Carga mínima")
st.info("Base OK. Habilitaremos módulos uno por uno.")

# === Chequeos rápidos del entorno ===
st.write("streamlit:", st.__version__)
st.write("pandas:", pd.__version__)

# === Archivos esperados en la raíz ===
for fname in ["T70.csv", "noticias.csv"]:
    if os.path.exists(fname):
        st.success(f"{fname} encontrado.")
    else:
        st.warning(f"{fname} no está en la raíz. (Ruta esperada: ./{fname})")

# === Placeholder de módulos internos ===
# Activa de a uno cuando esta base funcione.
# from modules.noticias_module import app as noticias_app
# noticias_app()

st.caption("Siguiente: activar módulos (Noticias, Gematría, etc.) de a uno.")
