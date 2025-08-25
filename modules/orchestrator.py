# modules/orchestrator.py — PRO UI (blindado)
from __future__ import annotations
from pathlib import Path
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

CHECKS = {
    "noticias.csv": "Noticias cargadas",
    "T70.csv": "Tendencias 70",
}

# ---- Placeholders para mantener el DOM estable ----
if "__orch_table_slot" not in st.session_state:
    st.session_state["__orch_table_slot"] = st.empty()
if "__orch_status_slot" not in st.session_state:
    st.session_state["__orch_status_slot"] = st.empty()

def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

def render_orchestrator():
    st.subheader("⏱️ Orquestador del sistema")

    # ===== KPIs globales =====
    ok_count, total = 0, len(CHECKS)
    rows = []
    for file, label in CHECKS.items():
        path = ROOT / file
        if _exists(path):
            ok_count += 1
            rows.append({"archivo": file, "estado": "OK ✅", "detalle": label})
        else:
            rows.append({"archivo": file, "estado": "❌ Faltante", "detalle": label})

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Archivos esperados", total, help="Elementos que el sistema necesita para correr.")
    with c2:
        st.metric("Disponibles", ok_count, help="Cuántos están presentes en la raíz del repo.")

    st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

    # ===== Tabla en slot fijo =====
    with st.session_state["__orch_table_slot"].container():
        df_rows = pd.DataFrame(rows, columns=["archivo", "estado", "detalle"])
        st.dataframe(df_rows, use_container_width=True, hide_index=True, key="orch_table")

    # ===== Mensaje en slot fijo =====
    with st.session_state["__orch_status_slot"].container():
        if ok_count == total:
            st.success("🚀 Todo listo: el sistema está preparado para ejecutar las capas.")
        else:
            faltan = [r["archivo"] for r in rows if r["estado"].startswith("❌")]
            st.warning("⚠️ Faltan insumos, revisa antes de lanzar el análisis.")
            if faltan:
                st.caption("Pendientes: " + ", ".join(faltan))
