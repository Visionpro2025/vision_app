# modules/gematria.py — PRO UI (blindado)
from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st
import json
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "__CORPUS" / "GEMATRIA"
RUNS = ROOT / "__RUNS" / "GEMATRIA"
RUNS.mkdir(parents=True, exist_ok=True)

# ---- Placeholders globales para mantener DOM estable ----
if "__gem_news_slot" not in st.session_state:
    st.session_state["__gem_news_slot"] = st.empty()     # tabla consolidado por noticia
if "__gem_tok_slot" not in st.session_state:
    st.session_state["__gem_tok_slot"] = st.empty()       # tabla detalle por token

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
        # No usamos widgets aquí para no mutar estructura; el que llama decide qué renderizar
        return None

def show_gematria():
    st.subheader("🔡 Gematría — resultados y corpus")

    # ===== Estado de corpus / métricas =====
    files = [
        "lexicon_hebrew.yaml", "translit_table.csv",
        "stopwords_es.txt", "stopwords_en.txt",
        "patterns.yaml", "bibliography.md",
    ]
    ok = sum(1 for f in files if _exists(CORPUS / f))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Archivos del corpus", f"{ok}/{len(files)}", help="Checa __CORPUS/GEMATRIA")
    with c2:
        st.metric("Tokens CSV", len(list(RUNS.glob("gematria_tokens_*.csv"))))
    with c3:
        st.metric("Consolidados CSV", len(list(RUNS.glob("gematria_news_*.csv"))))

    st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

    # ===== Tabs (cantidad fija) =====
    tab1, tab2 = st.tabs(["Consolidado por noticia", "Detalle por token"])

    # ---------- TAB 1: Consolidado por noticia ----------
    with tab1:
        news_files = sorted(RUNS.glob("gematria_news_*.csv"))
        news_names = [f.name for f in news_files]
        has_news = len(news_files) > 0

        # Select SIEMPRE presente (deshabilitado si no hay archivos)
        sel_name = st.selectbox(
            "Archivo",
            options=news_names if has_news else ["—"],
            index=0,
            key="gem_news_file",
            disabled=not has_news,
        )

        # Botón de descarga SIEMPRE presente (data vacía si no hay archivo)
        if has_news:
            df = _load(RUNS / sel_name)
            dl_bytes = df.to_csv(index=False).encode("utf-8") if (df is not None and not df.empty) else b""
        else:
            df = None
            dl_bytes = b""

        st.download_button(
            "⬇️ Descargar",
            dl_bytes,
            file_name=sel_name if has_news else "gematria_news.csv",
            mime="text/csv",
            use_container_width=True,
            key="gem_news_dl",
            disabled=(not has_news) or (len(dl_bytes) == 0),
        )

        # Tabla en SLOT FIJO (no desaparece el contenedor)
        with st.session_state["__gem_news_slot"].container():
            if not has_news:
                st.info("No hay `gematria_news_*.csv` en `__RUNS/GEMATRIA/`.")
            else:
                if df is None or df.empty:
                    st.warning("El archivo está vacío o no se pudo leer.")
                else:
                    st.dataframe(df, use_container_width=True, hide_index=True)

def analyze(df_news: pd.DataFrame) -> pd.DataFrame:
    """Analiza noticias con gematría y retorna DataFrame con resultados."""
    if df_news.empty:
        return pd.DataFrame()
    
    results = []
    
    for _, row in df_news.iterrows():
        titular = str(row.get("titular", ""))
        resumen = str(row.get("resumen", ""))
        fuente = str(row.get("fuente", ""))
        fecha = str(row.get("fecha", ""))
        
        # Análisis básico de gematría (simulado)
        texto_completo = f"{titular} {resumen}"
        
        # Extraer números del texto
        import re
        numeros = re.findall(r'\d+', texto_completo)
        numeros = [int(n) for n in numeros if 1 <= int(n) <= 70]
        
        # Calcular valor gemátrico básico (suma de caracteres ASCII)
        valor_gematrico = sum(ord(c) for c in texto_completo if c.isalpha())
        
        # Determinar categoría
        categoria = "general"
        if any(palabra in texto_completo.lower() for palabra in ["protesta", "huelga", "disturbios"]):
            categoria = "protestas_sociales"
        elif any(palabra in texto_completo.lower() for palabra in ["tiroteo", "violencia", "homicidio"]):
            categoria = "violencia_seguridad"
        elif any(palabra in texto_completo.lower() for palabra in ["inflación", "desempleo", "crisis"]):
            categoria = "crisis_economica"
        
        results.append({
            "id_noticia": row.get("id_noticia", ""),
            "titular": titular,
            "fuente": fuente,
            "fecha": fecha,
            "numeros_extraidos": ", ".join(map(str, numeros)),
            "valor_gematrico": valor_gematrico,
            "categoria": categoria,
            "longitud_texto": len(texto_completo),
            "palabras_clave": ", ".join([w for w in texto_completo.split() if len(w) > 5])
        })
    
    return pd.DataFrame(results)

def previous_draw_message() -> Dict:
    """Retorna mensaje gemátrico del sorteo anterior."""
    try:
        # Simular mensaje del sorteo anterior
        return {
            "fecha_sorteo": "2025-01-25",
            "numeros_ganadores": [7, 14, 21, 28, 35],
            "mensaje_gematrico": "Los números del cambio social se manifiestan en la secuencia de la transformación",
            "equivalencias_t70": [7, 14, 21, 28, 35],
            "interpretacion": "Fuerte presencia de números relacionados con protestas y cambios sociales"
        }
    except Exception:
        return {}

    # ---------- TAB 2: Detalle por token ----------
    with tab2:
        tok_files = sorted(RUNS.glob("gematria_tokens_*.csv"))
        tok_names = [f.name for f in tok_files]
        has_tok = len(tok_files) > 0

        sel2_name = st.selectbox(
            "Archivo",
            options=tok_names if has_tok else ["—"],
            index=0,
            key="gem_tok_file",
            disabled=not has_tok,
        )

        if has_tok:
            df2 = _load(RUNS / sel2_name)
            dl2_bytes = df2.to_csv(index=False).encode("utf-8") if (df2 is not None and not df2.empty) else b""
        else:
            df2 = None
            dl2_bytes = b""

        st.download_button(
            "⬇️ Descargar",
            dl2_bytes,
            file_name=sel2_name if has_tok else "gematria_tokens.csv",
            mime="text/csv",
            use_container_width=True,
            key="gem_tok_dl",
            disabled=(not has_tok) or (len(dl2_bytes) == 0),
        )

        with st.session_state["__gem_tok_slot"].container():
            if not has_tok:
                st.info("No hay `gematria_tokens_*.csv`.")
            else:
                if df2 is None or df2.empty:
                    st.warning("El archivo está vacío o no se pudo leer.")
                else:
                    st.dataframe(df2, use_container_width=True, hide_index=True)
