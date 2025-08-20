# modules/library.py
from __future__ import annotations
from pathlib import Path
import streamlit as st
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "__CORPUS" / "GEMATRIA"

def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

def render_library():
    st.subheader("📚 Biblioteca de gematría y referencias")

    b_md = CORPUS / "bibliography.md"
    b_csv = CORPUS / "bibliography.csv"

    if _exists(b_md):
        st.markdown("### 📖 Texto")
        try:
            st.markdown(b_md.read_text(encoding="utf-8"))
        except Exception as e:
            st.error(f"No se pudo leer el markdown: {e}")
    else:
        st.info("No se encontró **bibliography.md** en la carpeta de corpus.")

    if _exists(b_csv):
        st.markdown("### 📊 Tabla")
        try:
            df = pd.read_csv(b_csv, dtype=str)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"No se pudo leer el CSV: {e}")
    else:
        st.info("No se encontró **bibliography.csv** en la carpeta de corpus.")
