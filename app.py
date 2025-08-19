import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st
# ===== Utilidades Gematría (rutas, estado, carga segura) =====

def _gem_base_paths():
    """Resuelve rutas base asumiendo que aplicación.py está en la raíz del repo."""
    try:
        base = Path(__file__).resolve().parent
    except NameError:
        base = Path.cwd()
    corpus = base / "__CORPUS" / "GEMATRIA"
    runs = base / "__RUNS" / "GEMATRIA"
    runs.mkdir(parents=True, exist_ok=True)  # asegura carpeta de salidas
    return base, corpus, runs

def _gem_check_corpus(corpus: Path) -> dict:
    """Verifica que existan los archivos mínimos del corpus."""
    required = [
        "lexicon_hebrew.yaml",
        "translit_table.csv",
        "stopwords_es.txt",
        "stopwords_en.txt",
        "patterns.yaml",
        "bibliography.md",
    ]
    return {name: (corpus / name).exists() for name in required}

def _gem_list_run_files(runs: Path):
    """Lista archivos de salida si existen (no falla si no hay)."""
    tokens = sorted(runs.glob("gematria_tokens_*.csv"))
    news = sorted(runs.glob("gematria_news_*.csv"))
    return tokens, news

def _load_csv_safe(path: Path):
    """Carga CSV en UTF-8 de forma segura."""
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer {path.name}: {e}")
        return None
st.set_page_config(page_title="Visión", page_icon="🔮", layout="wide")

# ===== Título general
st.title("🔮 Sistema Predictivo Visión")

# ===== Menú lateral
menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    ["Inicio", "Visión", "Tabla T70", "Noticias", "Gematría"]  # ← añadida
)

# ===== Inicio
if menu == "Inicio":
    st.write("Bienvenido a la App del sistema Visión 🚀")

# ===== Visión (placeholder por ahora)
elif menu == "Visión":
    st.write("Aquí estará la lógica principal del sistema Visión.")

# ===== Tabla T70
elif menu == "Tabla T70":
    st.subheader("📊 Tabla T70")
    try:
        df_t70 = pd.read_csv("T70.csv", encoding="utf-8")
        st.dataframe(df_t70, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar T70.csv: {e}")
        st.info("Verifica que el archivo **T70.csv** exista en el repositorio (carpeta raíz).")

# ===== Noticias (bitácora)
elif menu == "Noticias":
    st.subheader("🗞️ Noticias — bitácora del sorteo")
elif menu == "Gematría":
    st.title("🔡 Capa Gematría")

    # --- utilidades mínimas (si ya las pegaste arriba, omite esta sección) ---
    from pathlib import Path
    import pandas as pd

    def _gem_base_paths():
        try:
            base = Path(__file__).resolve().parent
        except NameError:
            base = Path.cwd()
        corpus = base / "__CORPUS" / "GEMATRIA"
        runs = base / "__RUNS" / "GEMATRIA"
        runs.mkdir(parents=True, exist_ok=True)
        return base, corpus, runs

    def _gem_check_corpus(corpus: Path) -> dict:
        required = [
            "lexicon_hebrew.yaml",
            "translit_table.csv",
            "stopwords_es.txt",
            "stopwords_en.txt",
            "patterns.yaml",
            "bibliography.md",
        ]
        return {name: (corpus / name).exists() for name in required}

    def _gem_list_run_files(runs: Path):
        tokens = sorted(runs.glob("gematria_tokens_*.csv"))
        news = sorted(runs.glob("gematria_news_*.csv"))
        return tokens, news

    def _load_csv_safe(path: Path):
        try:
            return pd.read_csv(path, dtype=str, encoding="utf-8")
        except Exception as e:
            st.error(f"Error al leer {path.name}: {e}")
            return None
    # -------------------------------------------------------------------------

    base, corpus, runs = _gem_base_paths()
    st.caption(f"📁 Base del proyecto: {base}")
    st.write("---")

    # Estado del corpus
    st.subheader("Estado del corpus de Gematría")
    status = _gem_check_corpus(corpus)
    cols = st.columns(3)
    for i, (fname, ok) in enumerate(status.items()):
        with cols[i % 3]:
            st.success(f"✅ {fname}") if ok else st.warning(f"⚠️ Falta {fname}")

    if not all(status.values()):
        st.info("Sube todos los archivos faltantes a `__CORPUS/GEMATRIA/`.")
    st.write("---")

    # Resultados disponibles
    st.subheader("Resultados disponibles")
    tokens_files, news_files = _gem_list_run_files(runs)

    colL, colR = st.columns(2)

    with colL:
        st.markdown("**Consolidado por noticia** (`gematria_news_YYYYMMDD.csv`)")
        if news_files:
            selected_news = st.selectbox(
                "Selecciona un archivo de consolidado:",
                options=[f.name for f in news_files],
                key="news_select"
            )
            df_news = _load_csv_safe(runs / selected_news)
            if df_news is not None and not df_news.empty:
                st.dataframe(df_news, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ Descargar consolidado",
                    df_news.to_csv(index=False).encode("utf-8"),
                    file_name=selected_news,
                    mime="text/csv"
                )
            else:
                st.info("El archivo está vacío o no pudo cargarse.")
        else:
            st.info("Aún no hay `gematria_news_*.csv` en `__RUNS/GEMATRIA/`.")

    with colR:
        st.markdown("**Detalle por token** (`gematria_tokens_YYYYMMDD.csv`)")
        if tokens_files:
            selected_tokens = st.selectbox(
                "Selecciona un archivo de tokens:",
                options=[f.name for f in tokens_files],
                key="tokens_select"
            )
            df_tokens = _load_csv_safe(runs / selected_tokens)
            if df_tokens is not None and not df_tokens.empty:
                st.dataframe(df_tokens, use_container_width=True, hide_index=True)
                st.download_button(
                    "⬇️ Descargar detalle",
                    df_tokens.to_csv(index=False).encode("utf-8"),
                    file_name=selected_tokens,
                    mime="text/csv"
                )
            else:
                st.info("El archivo está vacío o no pudo cargarse.")
        else:
            st.info("Aún no hay `gematria_tokens_*.csv` en `__RUNS/GEMATRIA/`.")

    st.write("---")
    st.caption("Cuando se generen resultados, aparecerán aquí automáticamente.")
    # Opciones básicas
    sorteos_disponibles = ["MegaMillions", "Powerball", "Otro"]

    # Intentar cargar el CSV
    try:
        df_news = pd.read_csv("noticias.csv", encoding="utf-8")
        # Normalizar columnas esperadas
        columnas = ["id_noticia","fecha","sorteo","fuente","titular","resumen","url","etiquetas"]
        faltantes = [c for c in columnas if c not in df_news.columns]
        for c in faltantes:
            df_news[c] = ""
        df_news = df_news[columnas]
    except Exception as e:
        st.warning("No se pudo leer **noticias.csv** (aún no existe o está vacío).")
        st.info("Crea el archivo `noticias.csv` con la línea de encabezados:")
        st.code("id_noticia,fecha,sorteo,fuente,titular,resumen,url,etiquetas", language="csv")
        st.caption(f"Detalle técnico: {e}")
        df_news = pd.DataFrame(columns=["id_noticia","fecha","sorteo","fuente","titular","resumen","url","etiquetas"])

    # ---- Filtros
    with st.expander("🔎 Filtros", expanded=True):
        colF1, colF2 = st.columns([1,1])
        with colF1:
            fecha_min = st.date_input("Desde", value=date.today())
        with colF2:
            fecha_max = st.date_input("Hasta", value=date.today())

        sel_sorteos = st.multiselect("Sorteo(s)", options=sorteos_disponibles, default=sorteos_disponibles)
        texto = st.text_input("Buscar en titular / resumen / etiquetas", "")

    # Aplicar filtros si hay datos
    if not df_news.empty:
        # Convertir fecha a tipo fecha si viene como texto
        try:
            df_news["fecha"] = pd.to_datetime(df_news["fecha"]).dt.date
        except Exception:
            pass

        mask_fecha = True
        if "fecha" in df_news.columns:
            mask_fecha = (df_news["fecha"] >= fecha_min) & (df_news["fecha"] <= fecha_max)

        mask_sorteo = df_news["sorteo"].isin(sel_sorteos) if "sorteo" in df_news.columns else True

        if texto:
            texto_low = texto.lower()
            campos = df_news[["titular","resumen","etiquetas"]].fillna("").astype(str).apply(lambda s: s.str.lower())
            mask_texto = campos.apply(lambda r: (texto_low in r["titular"]) or (texto_low in r["resumen"]) or (texto_low in r["etiquetas"]), axis=1)
        else:
            mask_texto = True

        df_filtrado = df_news[mask_fecha & mask_sorteo & mask_texto].copy()
        st.write(f"Resultados: **{len(df_filtrado)}**")
        st.dataframe(df_filtrado, use_container_width=True)

        # Descargar CSV actual
        csv_bytes = df_news.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Descargar noticias.csv", data=csv_bytes, file_name="noticias.csv", mime="text/csv")
    else:
        st.info("Aún no hay noticias registradas.")

    # ---- Plantilla para registrar una noticia (edición manual en GitHub)
    st.divider()
    st.markdown("### ➕ Plantilla para agregar una fila a `noticias.csv`")

    colP1, colP2 = st.columns([1,1])
    with colP1:
        fecha_new = st.date_input("Fecha de la noticia", value=date.today(), key="fecha_new")
        sorteo_new = st.selectbox("Sorteo", options=sorteos_disponibles, index=0, key="sorteo_new")
        fuente_new = st.text_input("Fuente (medio/sitio)", "Reuters", key="fuente_new")
    with colP2:
        titular_new = st.text_input("Titular", "Ejemplo de titular", key="titular_new")
        resumen_new = st.text_area("Resumen breve", "Descripción breve de la noticia", key="resumen_new")
        url_new = st.text_input("URL", "https://ejemplo.com", key="url_new")

    etiquetas_new = st.text_input("Etiquetas (separadas por `;`)", "politica;economia", key="etiquetas_new")

    # Generar ID simple (puedes cambiar la lógica luego)
    nuevo_id = f"N-{fecha_new.isoformat()}-1"

    linea_csv = f"{nuevo_id},{fecha_new.isoformat()},{sorteo_new},{fuente_new},{titular_new},{resumen_new},{url_new},{etiquetas_new}"
    st.markdown("Copia y pega esta **línea CSV** en `noticias.csv` (debajo del encabezado) usando GitHub → **Add file / Edit file**:")
    st.code(linea_csv, language="csv")

    st.caption("💡 Recuerda: la **interpretación numérica** (gematría/mensaje subliminal) se hace luego en el módulo de *Noticias Numéricas*, usando la T70 como referencia.")
