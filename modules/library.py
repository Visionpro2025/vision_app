# modules/library.py — Biblioteca con vista previa multi-formato (blindado)
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

# ============ Placeholders (DOM estable) ============
if "__lib_status_slot" not in st.session_state:
    st.session_state["__lib_status_slot"] = st.empty()     # mensajes/estado
if "__lib_preview_slot" not in st.session_state:
    st.session_state["__lib_preview_slot"] = st.empty()    # vista previa
if "__lib_download_slot" not in st.session_state:
    st.session_state["__lib_download_slot"] = st.empty()   # botón de descarga

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
        expected = ["title", "file_id", "type", "description", "tags"]
        missing = [c for c in expected if c not in df.columns]
        if missing:
            # devolvemos DataFrame con columnas esperadas para no romper UI
            return pd.DataFrame(columns=expected)
        return df
    except Exception:
        return pd.DataFrame(columns=["title", "file_id", "type", "description", "tags"])

def _drive_download_url(file_id: str, tipo: str) -> str:
    """Construye URL de descarga desde Drive según tipo."""
    tipo = (tipo or "").strip().lower()
    if tipo in ("gdoc", "google-doc", "google_docs", "google-docs"):
        return f"https://docs.google.com/document/d/{file_id}/export?format=docx"
    if tipo in ("gsheet", "google-sheet", "google_sheets", "google-sheets"):
        return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv"
    if tipo in ("gslide", "google-slide", "google-slides", "google_slides"):
        return f"https://docs.google.com/presentation/d/{file_id}/export/pdf"
    return f"https://drive.google.com/uc?export=download&id={file_id}"

def _download_from_drive(file_id: str, tipo: str) -> BytesIO | None:
    url = _drive_download_url(file_id, tipo)
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return BytesIO(r.content)
    except requests.HTTPError:
        return None
    except Exception:
        return None

def _b64_pdf(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")

# ============ Renderizadores ============
def _render_txt(buf: BytesIO):
    try:
        text = buf.read().decode("utf-8", errors="ignore")
        st.subheader("📄 Vista previa TXT")
        st.text(text[:10000])
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
        lines = [p.text for p in doc.paragraphs if p.text.strip()]
        preview = "\n".join(lines[:40]).strip()
        if preview:
            st.text(preview)
        else:
            st.info("Documento sin texto visible o solo contiene elementos complejos.")
    except Exception as e:
        st.error(f"No pude mostrar DOCX: {e}")

def _render_pdf(buf: BytesIO):
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

    lib_ok = _exists(LIB_DIR)
    mani_ok = _exists(MANIFEST)

    # Cargamos manifest si existe, sin mutar el layout si falla
    df = _load_manifest(MANIFEST) if (lib_ok and mani_ok) else pd.DataFrame(columns=["title","file_id","type","description","tags"])
    has_rows = not df.empty

    # Selector (siempre visible; se deshabilita si no hay datos)
    cols = st.columns([1, 2])
    with cols[0]:
        options = df["title"].tolist() if has_rows else ["(sin documentos)"]
        sel_title = st.selectbox("Documento", options=options, index=0, key="lib_doc_sel", disabled=not has_rows)
    with cols[1]:
        if has_rows:
            fila = df[df["title"] == sel_title].iloc[0] if sel_title in df["title"].values else df.iloc[0]
            st.markdown(f"**Descripción:** {fila.get('description','')}")
            st.markdown(f"**Tags:** `{fila.get('tags','')}`")
            st.caption(f"**Tipo:** `{(fila.get('type','') or 'desconocido')}` · **file_id:** `{str(fila.get('file_id',''))[:6]}…`")
        else:
            st.markdown("**Descripción:** —")
            st.markdown("**Tags:** —")
            st.caption("**Tipo:** — · **file_id:** —")

    # Mensajes de estado en SLOT fijo
    with st.session_state["__lib_status_slot"].container():
        if not lib_ok:
            st.error(f"No existe la carpeta {LIB_DIR}. Crea `__LIBRARY/` en la raíz del repo.")
        elif not mani_ok:
            st.warning("No encuentro `__LIBRARY/manifest.csv`.")
            st.info("Crea un CSV con columnas: title,file_id,type,description,tags")
        elif not has_rows:
            st.warning("El manifest.csv está vacío o mal formado.")
        else:
            st.caption("Selecciona un documento y usa las acciones de abajo.")

    # Acciones (siempre visibles; se deshabilitan si no hay datos)
    c1, c2 = st.columns(2)
    open_disabled = not has_rows
    link_disabled = not has_rows

    # Acción: Abrir / Previsualizar
    if c1.button("📂 Abrir / Previsualizar", type="primary", use_container_width=True, key="lib_open", disabled=open_disabled):
        # limpiamos slots para render limpio en este mismo ciclo
        with st.session_state["__lib_download_slot"].container():
            st.empty()
        with st.session_state["__lib_preview_slot"].container():
            st.empty()

        fila = df[df["title"] == sel_title].iloc[0] if has_rows else None
        if fila is not None:
            file_id = (fila["file_id"] or "").strip()
            tipo = (fila["type"] or "").strip().lower()
            buf = _download_from_drive(file_id, tipo)

            # Botón de descarga SIEMPRE en su slot
            with st.session_state["__lib_download_slot"].container():
                ext = {
                    "txt": "txt", "csv": "csv", "pdf": "pdf", "docx": "docx",
                    "gdoc": "docx", "gsheet": "csv", "gslide": "pdf",
                }.get(tipo, "bin")
                data_bytes = buf.getvalue() if buf is not None else b""
                st.download_button(
                    "⬇️ Descargar",
                    data=data_bytes,
                    file_name=f"{sel_title}.{ext}",
                    mime=None,
                    use_container_width=True,
                    key="lib_dl_btn",
                    disabled=(buf is None or len(data_bytes) == 0),
                )

            # Vista previa en su slot (según tipo)
            with st.session_state["__lib_preview_slot"].container():
                if buf is None:
                    st.error("No se pudo descargar el archivo desde Drive.")
                else:
                    buf.seek(0)
                    if tipo in ("txt",):
                        _render_txt(buf)
                    elif tipo in ("csv", "gsheet"):
                        _render_csv(buf)
                    elif tipo in ("docx", "gdoc"):
                        _render_docx(buf)
                    elif tipo in ("pdf", "gslide"):
                        _render_pdf(buf)
                    else:
                        st.info("Formato no soportado aún para vista previa. El archivo se puede descargar.")

    # Acción: Copiar enlace de descarga
    if c2.button("🔗 Copiar enlace de descarga", use_container_width=True, key="lib_copy_link", disabled=link_disabled):
        if has_rows:
            fila = df[df["title"] == sel_title].iloc[0] if sel_title in df["title"].values else df.iloc[0]
            file_id = (fila["file_id"] or "").strip()
            tipo = (fila["type"] or "").strip().lower()
            url = _drive_download_url(file_id, tipo)
            # mostramos el enlace siempre en el slot de estado (no creamos nodos nuevos)
            with st.session_state["__lib_status_slot"].container():
                st.code(url, language="text")
                st.success("Enlace listo para compartir.")
