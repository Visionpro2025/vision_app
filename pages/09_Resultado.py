# pages/09_Resultado.py
import streamlit as st
from modules.schemas import FinalOutcome

st.set_page_config(page_title="Resultado Final", page_icon="📊")
st.title("📊 Resultado Final del Sorteo")

out: FinalOutcome = st.session_state.get("outcome")
if not out:
    st.info("Aún no hay resultado final. Ejecuta el pipeline completo.")
else:
    st.subheader("Series Finales")
    for p in out.proposals:
        st.write(f"{p.main}**  • Prob: {p.probability:.2%}")
    st.subheader("Resumen")
    st.write(f"Patrón Dominante: {out.dominant_pattern}")
    st.write(f"Categoría Principal: {out.dominant_category}")
    st.write(f"Arquetipo Dominante: {out.dominant_archetype}")
    if out.subliminal_msg:
        st.write(f"Mensaje Subliminal: {out.subliminal_msg}")
    if out.quantum_state:
        st.write(f"Estado Cuántico: {out.quantum_state}")








