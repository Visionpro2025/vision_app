# pages/07_Correlacion.py
import streamlit as st
from modules.schemas import CorrelationReport

st.set_page_config(page_title="Correlación", page_icon="🔗")
st.title("🔗 Correlación entre capas")

# corr debe llegar por session_state o cache
corr: CorrelationReport = st.session_state.get("corr")
if not corr:
    st.warning("Ejecuta el análisis para ver correlaciones.")
else:
    st.metric("Correlación Global", f"{corr.global_score:.2%}")
    for p in corr.pairs:
        st.progress(min(1.0,p.score), text=f"{p.a} ↔ {p.b}: {p.score:.2%}")







