# modules/library.py — Biblioteca con vista previa multi-formato
from __future__ import annotations
from pathlib import Path
from io import BytesIO
import base64
import requests
import streamlit as st
import pandas as pd

# ============ Config ============
ROOT = Path(__file__).resolve().parent.parent
LIB_DIR = ROOT / "__LIBRARY"
MANIFEST = LIB_DIR / "manifest.csv"

# ============ Utilidades ============
def _exists(p: Path) -> bool:
    try:
        return p.exists()
    except Exception:
        return False

@st.cache_data(show_spinner=False)
def _load_manifest(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8").fillna("")
        # Validación básica de columnas
        expected = ["title", "file_id", "type", "description", "tags"]
        missing = [c for c in expected if c not in df.columns]
        if missing:
            st.error(f"El manifest no tiene columnas requeridas: {missing}")
            return pd.DataFrame(columns=expected)
        return df
    except Exception as e:
        st.error(f"No se pudo leer manifest.csv: {e}")
        return pd.DataFrame(columns=["title", "file_id", "type", "description", "tags"])

def _drive_download_url(file_id: str, tipo: str) -> str:
    """
    Construye URL de descarga desde Drive:
    - Archivos subidos normales: uc?export=download
    - Google Docs/Sheets/Slides: export específicos
    """
    tipo = (tipo or "").strip().lower()

    # Google Docs
    if tipo in ("gdoc", "google-doc", "google_docs", "google-docs"):
        # exportar como DOCX
        return f"https://docs.google.com/document/d/{file_id}/export?format=docx"
    # Google Sheets
    if tipo in ("gsheet", "google-sheet", "google_sheets", "google-sheets"):
        # exportar como CSV
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
    # Google Slides (opcional: export PDF)
    if tipo in ("gslide", "google-slide", "google-slides", "google_slides"):
        return f"https://docs.google.com/presentation/d/{file_id}/export/pdf"

    # Genérico: archivo normal en Drive
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def _download_from_drive(file_id: str, tipo: str) -> BytesIO | None:
    url = _drive_download_url(file_id, tipo)
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return BytesIO(r.content)
    except requests.HTTPError as e:
        st.error(f"Error HTTP al descargar desde Drive: {e}")
    except Exception as e:
        st.error(f"No se pudo descargar el archivo: {e}")
    return None

def _b64_pdf(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

# ============ Renderizadores ============
def _render_txt(buf: BytesIO):
    try:
        text = buf.read().decode("utf-8", errors="ignore")
        st.subheader("📄 Vista previa TXT")
        st.text(text[:10000])  # primeras 10k chars
    except Exception as e:
        st.error(f"No pude mostrar TXT: {e}")

def _render_csv(buf: BytesIO):
    try:
        df = pd.read_csv(buf, dtype=str, encoding="utf-8", on_bad_lines="skip")
        st.subheader("📊 Vista previa CSV")
        st.dataframe(df.head(100), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"No pude mostrar CSV: {e}")

def _render_docx(buf: BytesIO):
    try:
        from docx import Document  # requiere python-docx
        doc = Document(buf)
        st.subheader("📄 Vista previa DOCX")
        # mostrar primeras ~40 líneas
        lines = [p.text for p in doc.paragraphs if p.text.strip()]
        preview = "\n".join(lines[:40]).strip()
        if preview:
            st.text(preview)
        else:
            st.info("Documento sin texto visible o solo contiene elementos complejos.")
    except Exception as e:
        st.error(f"No pude mostrar DOCX: {e}")

def _render_pdf(buf: BytesIO):
    """
    Opción 1 (simple): incrustar el PDF en un iframe (visual).
    Opción 2 (texto): usar pdfplumber para extraer texto y previsualizar.
    Aquí usamos el iframe (mejor UX y sin parseo).
    """
    try:
        data = buf.getvalue()
        b64 = _b64_pdf(data)
        st.subheader("📕 Vista previa PDF")
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="600px" type="application/pdf"></iframe>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"No pude mostrar PDF: {e}")
        st.info("Si prefieres extraer texto, instala `pdfplumber` y puedo mostrar el contenido textual.")

# ============ UI principal ============
def render_library():
    st.subheader("📚 Biblioteca de referencia (Drive)")

    if not _exists(LIB_DIR):
        st.error(f"No existe la carpeta {LIB_DIR}. Crea `__LIBRARY/` en la raíz del repo.")
        return

    if not _exists(MANIFEST):
        st.warning("No encuentro `__LIBRARY/manifest.csv`.")
        st.info("Crea un CSV con columnas: title,file_id,type,description,tags")
        return

    df = _load_manifest(MANIFEST)
    if df.empty:
        st.warning("El manifest.csv está vacío o mal formado.")
        return

    # Selector de documento
    cols = st.columns([1, 2])
    with cols[0]:
        sel_title = st.selectbox("Documento", options=df["title"].tolist())
    fila = df[df["title"] == sel_title].iloc[0]
    file_id = fila["file_id"].strip()
    tipo = (fila["type"] or "").strip().lower()

    # Info
    with cols[1]:
        st.markdown(f"**Descripción:** {fila.get('description','')}")
        st.markdown(f"**Tags:** `{fila.get('tags','')}`")
        st.caption(f"**Tipo:** `{tipo or 'desconocido'}` · **file_id:** `{file_id[:6]}…`")

    # Acciones
    c1, c2 = st.columns(2)
    if c1.button("📂 Abrir / Previsualizar", type="primary", use_container_width=True):
        buf = _download_from_drive(file_id, tipo)
        if buf is None:
            return

        # Descarga directa
        # Nombre de archivo sugerido por tipo
        ext = {
            "txt": "txt",
            "csv": "csv",
            "pdf": "pdf",
            "docx": "docx",
            "gdoc": "docx",
            "gsheet": "csv",
            "gslide": "pdf",
        }.get(tipo, "bin")

        st.download_button(
            "⬇️ Descargar",
            data=buf.getvalue(),
            file_name=f"{sel_title}.{ext}",
            mime=None,
            use_container_width=True,
        )

        # Render según tipo
        if tipo in ("txt",):
            buf.seek(0); _render_txt(buf)
        elif tipo in ("csv", "gsheet"):
            buf.seek(0); _render_csv(buf)
        elif tipo in ("docx", "gdoc"):
            buf.seek(0); _render_docx(buf)
        elif tipo in ("pdf", "gslide"):
            buf.seek(0); _render_pdf(buf)
        else:
            st.info("Formato no soportado aún para vista previa. El archivo se puede descargar.")

    if c2.button("🔗 Copiar enlace de descarga", use_container_width=True):
        url = _drive_download_url(file_id, tipo)
        st.code(url, language="text")
        st.success("Enlace listo para compartir.")
