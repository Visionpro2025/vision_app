# modules/library.py — PRO UI
from __future__ import annotations
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "__LIBRARY"

def render_library():
    st.subheader("📚 Biblioteca de referencia")

    if not LIB.exists():
        st.error(f"No existe la carpeta {LIB}")
        return

    files = list(LIB.glob("*"))
    if not files:
        st.info("La biblioteca está vacía.")
        return

    # KPIs
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total archivos", len(files))
    with c2:
        types = {f.suffix for f in files}
        st.metric("Extensiones distintas", len(types))

    st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

    for f in files:
        size_kb = f.stat().st_size // 1024
        st.markdown(
            f"""
            <div style="padding:10px 14px;margin:6px 0;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1)">
              <b>{f.name}</b>  
              <span style="opacity:.7">({size_kb} KB)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
