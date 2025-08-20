# modules/noticias_module.py — Vista doble (Cruda vs Filtrada) + motivos + descargas
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
NEWS_CSV = ROOT / "noticias.csv"

# --------- Utilidades básicas ---------
REQUIRED_COLS = [
    "id_noticia","fecha","sorteo","pais","fuente","titular","resumen",
    "etiquetas","nivel_emocional_diccionario","nivel_emocional_modelo",
    "nivel_emocional_final","noticia_relevante","categorias_t70_ref","url"
]

@st.cache_data(show_spinner=False)
def _load_news(path: Path) -> pd.DataFrame:
    try:
        df = pd.read_csv(path, dtype=str, encoding="utf-8").fillna("")
    except Exception:
        return pd.DataFrame(columns=REQUIRED_COLS)
    # normaliza columnas faltantes
    for c in REQUIRED_COLS:
        if c not in df.columns:
            df[c] = ""
    return df[REQUIRED_COLS]

def _to_int_safe(x, default=0):
    try:
        return int(str(x).strip())
    except Exception:
        return default

def _motivo_filtro(row: pd.Series, umbral: int, palabras_alto_impacto: list[str]) -> str:
    texto = f"{row.get('titular','')} {row.get('resumen','')}".lower()
    alto_imp = any(w in texto for w in palabras_alto_impacto)
    em_fin = _to_int_safe(row.get("nivel_emocional_final", 0), 0)

    if em_fin >= umbral and alto_imp:
        return f"Incluida: emoción={em_fin}≥{umbral} + alto impacto"
    if em_fin >= umbral:
        return f"Incluida: emoción={em_fin}≥{umbral}"
    if alto_imp:
        return f"Incluida: alto impacto en texto (emocion={em_fin}<{umbral})"
    return f"Excluida: emoción={em_fin}<{umbral} y sin alto impacto"

# --------- Vista principal ---------
def render_noticias():
    st.subheader("📰 Noticias — Vista doble (Cruda vs Filtrada)")
    st.caption("Entrada oficial: `noticias.csv` en la raíz del repositorio.")

    if not NEWS_CSV.exists():
        st.error("No se encontró `noticias.csv` en la raíz del repo.")
        with st.expander("Estructura esperada"):
            st.code(",".join(REQUIRED_COLS), language="text")
        return

    df = _load_news(NEWS_CSV)
    if df.empty:
        st.warning("`noticias.csv` está vacío o no legible.")
        return

    # --------- Filtros superiores ---------
    with st.container():
        c1, c2, c3, c4 = st.columns([1,1,1,2])
        fechas = ["(todas)"] + sorted([f for f in df["fecha"].unique() if f])
        fsel = c1.selectbox("Fecha", options=fechas, index=0)

        sorteos = ["(todos)"] + sorted([s for s in df["sorteo"].unique() if s])
        ssel = c2.selectbox("Sorteo", options=sorteos, index=0)

        umbral = c3.slider("Umbral emoción final", 0, 100, 60)

        q = c4.text_input("Buscar en titular/resumen/etiquetas", "")

    dff = df.copy()
    if fsel != "(todas)":
        dff = dff[dff["fecha"] == fsel]
    if ssel != "(todos)":
        dff = dff[dff["sorteo"] == ssel]
    if q.strip():
        qn = q.lower().strip()
        dff = dff[
            dff["titular"].str.lower().str.contains(qn, na=False) |
            dff["resumen"].str.lower().str.contains(qn, na=False) |
            dff["etiquetas"].str.lower().str.contains(qn, na=False)
        ]

    st.info(f"Coincidencias tras filtros: **{len(dff)}**")
    st.markdown("---")

    # --------- Parámetros de filtrado ---------
    palabras_alto_impacto = st.multiselect(
        "Palabras de alto impacto (añade/ajusta)",
        options=["récord","fraude","escándalo","crisis","millones","histórico","emergencia","colapso","tragedia"],
        default=["récord","fraude","escándalo","crisis","millones","histórico"]
    )

    # Construye motivos y máscara
    if not dff.empty:
        reasons = []
        mask = []
        for _, r in dff.iterrows():
            m = _motivo_filtro(r, umbral=umbral, palabras_alto_impacto=palabras_alto_impacto)
            reasons.append(m)
            mask.append(m.startswith("Incluida"))
        dff = dff.copy()
        dff["__motivo"] = reasons
        df_ok = dff[mask].copy()
    else:
        df_ok = dff.copy()

    # --------- Doble ventana ---------
    colL, colR = st.columns(2)

    # Cruda
    with colL:
        st.subheader("🗞️ Cruda (primaria)")
        st.caption("Noticias tal cual llegaron (sin filtro).")
        if dff.empty:
            st.info("Sin resultados en la vista cruda.")
        else:
            for _, r in dff.head(60).iterrows():
                titulo = (r["titular"] or "—").strip()
                with st.expander(f"📰 {titulo[:100]}"):
                    st.write(r["resumen"] or "—")
                    st.write(f"**Fecha:** {r['fecha']} · **Sorteo:** {r['sorteo'] or '—'} · **Fuente:** {r['fuente'] or '—'}")
                    st.caption(f"Etiquetas: `{r['etiquetas']}` • Emoción (dic/mod/fin): {r['nivel_emocional_diccionario']}/{r['nivel_emocional_modelo']}/{r['nivel_emocional_final']}")
                    if r.get("url"):
                        st.markdown(f"[🔗 Abrir fuente]({r['url']})")

    # Filtrada
    with colR:
        st.subheader("✅ Filtrada (alta relevancia)")
        st.caption("Noticias que superan el umbral y/o contienen palabras de alto impacto.")
        st.text(f"Seleccionadas: {len(df_ok)} / {len(dff)}")
        if df_ok.empty:
            st.info("No hay noticias que cumplan el criterio actual.")
        else:
            for _, r in df_ok.head(60).iterrows():
                titulo = (r["titular"] or "—").strip()
                with st.expander(f"🔥 {titulo[:100]}"):
                    st.write(r["resumen"] or "—")
                    st.write(f"**Motivo:** {r['__motivo']}")
                    st.write(f"**Fecha:** {r['fecha']} · **Sorteo:** {r['sorteo'] or '—'} · **Fuente:** {r['fuente'] or '—'}")
                    st.caption(f"Etiquetas: `{r['etiquetas']}` • Emoción (dic/mod/fin): {r['nivel_emocional_diccionario']}/{r['nivel_emocional_modelo']}/{r['nivel_emocional_final']}")
                    if r.get("url"):
                        st.markdown(f"[🔗 Abrir fuente]({r['url']})")

    st.markdown("---")

    # --------- Descargas ---------
    cdl, cdr = st.columns(2)
    with cdl:
        st.download_button(
            "⬇️ Descargar vista cruda (CSV)",
            dff.drop(columns=["__motivo"], errors="ignore").to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_cruda_{datetime.utcnow().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with cdr:
        st.download_button(
            "⬇️ Descargar vista filtrada (CSV)",
            df_ok.drop(columns=["__motivo"], errors="ignore").to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_filtrada_{datetime.utcnow().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # --------- Ayuda / estructura ---------
    with st.expander("📎 Estructura esperada de noticias.csv"):
        st.code(",".join(REQUIRED_COLS), language="text")         
