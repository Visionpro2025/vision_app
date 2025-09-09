# pages/08_Ensamblaje.py
import streamlit as st
from modules.schemas import SeriesProposal

st.set_page_config(page_title="Ensamblaje", page_icon="⚙")
st.title("⚙ Ensamblaje de series")

props = st.session_state.get("series", [])
if not props:
    st.info("Genera series desde el análisis.")
else:
    for p in props:
        st.write(f"*Serie:* {p.main} • Prob: {p.probability:.2%}")
        with st.expander("Explicación"):
            st.write(p.reasoning)








