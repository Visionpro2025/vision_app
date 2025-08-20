# modules/gematria.py — PRO UI
from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "__CORPUS" / "GEMATRIA"
RUNS = ROOT / "__RUNS" / "GEMATRIA"
RUNS.mkdir(parents=True, exist_ok=True)

def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

@st.cache_data(show_spinner=False)
def _load(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer {path.name}: {e}")
        return None

def show_gematria():
    st.subheader("🔡 Gematría — resultados y corpus")

    # Estado de corpus
    files = [
        "lexicon_hebrew.yaml", "translit_table.csv",
        "stopwords_es.txt", "stopwords_en.txt",
        "patterns.yaml", "bibliography.md",
    ]
    ok = sum(1 for f in files if _exists(CORPUS / f))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Archivos del corpus", f"{ok}/{len(files)}")
    with c2:
        st.metric("Tokens CSV", len(list(RUNS.glob("gematria_tokens_*.csv"))))
    with c3:
        st.metric("Consolidados CSV", len(list(RUNS.glob("gematria_news_*.csv"))))

    st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

    # Tabs de resultados
    tab1, tab2 = st.tabs(["Consolidado por noticia", "Detalle por token"])

    with tab1:
        news_files = sorted(RUNS.glob("gematria_news_*.csv"))
        if not news_files:
            st.info("No hay `gematria_news_*.csv` en `__RUNS/GEMATRIA/`.")
        else:
            sel = st.selectbox("Archivo", options=[f.name for f in news_files])
            df = _load(RUNS / sel)
            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ Descargar",
                    df.to_csv(index=False).encode("utf-8"),
                    file_name=sel,
                    mime="text/csv",
                )

    with tab2:
        tok_files = sorted(RUNS.glob("gematria_tokens_*.csv"))
        if not tok_files:
            st.info("No hay `gematria_tokens_*.csv`.")
        else:
            sel2 = st.selectbox("Archivo", options=[f.name for f in tok_files], key="tok_sel")
            df2 = _load(RUNS / sel2)
            if df2 is not None and not df2.empty:
                st.dataframe(df2, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ Descargar",
                    df2.to_csv(index=False).encode("utf-8"),
                    file_name=sel2,
                    mime="text/csv",
                )
