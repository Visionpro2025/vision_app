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
    st.subheader("📚 Biblioteca de gematría")

    b_md  = CORPUS / "bibliography.md"
    b_csv = CORPUS / "bibliography.csv"

    st.caption(f"Corpus: `{CORPUS}`")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Checklist de archivos clave**")
        for name in [
            "bibliography.md",
            "translit_table.csv",
            "lexicon_hebrew.yaml",
            "stopwords_es.txt",
            "stopwords_en.txt",
            "patterns.yaml",
        ]:
            ok = _exists(CORPUS / name)
            st.write(("✅" if ok else "⚠️") + f" {name}")

    with col2:
        st.markdown("**Metadatos estructurados (si existe)**")
        if _exists(b_csv):
            try:
                df = pd.read_csv(b_csv, dtype=str, encoding="utf-8")
                st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"bibliography.csv ilegible: {e}")
        else:
            st.info("No hay `bibliography.csv`. (Opcional pero útil).")

    st.write("---")
    st.markdown("**Contenido de `bibliography.md`**")
    if _exists(b_md):
        try:
            st.markdown(b_md.read_text(encoding="utf-8"))
        except Exception as e:
            st.error(f"No se pudo leer bibliography.md: {e}")
    else:
        st.warning("Falta `bibliography.md`. Crea una con tu lista de fuentes.")
