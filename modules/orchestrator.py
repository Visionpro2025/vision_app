# modules/orchestrator.py — PRO UI
from __future__ import annotations
from pathlib import Path
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

CHECKS = {
    "noticias.csv": "Noticias cargadas",
    "T70.csv": "Tendencias 70",
}

def render_orchestrator():
    st.subheader("⏱️ Orquestador del sistema")

    # KPIs globales
    ok_count, total = 0, len(CHECKS)
    rows = []
    for file, label in CHECKS.items():
        path = ROOT / file
        if path.exists():
            ok_count += 1
            rows.append({"archivo": file, "estado": "OK ✅", "detalle": label})
        else:
            rows.append({"archivo": file, "estado": "❌ Faltante", "detalle": label})

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Archivos esperados", total)
    with c2:
        st.metric("Disponibles", ok_count)

    st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if ok_count == total:
        st.success("🚀 Todo listo: el sistema está preparado para ejecutar las capas.")
    else:
        st.warning("⚠️ Faltan insumos, revisa antes de lanzar el análisis.")
