# modules/noticias_module.py — PRO UI
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

@st.cache_data(show_spinner=False)
def _load_csv(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"❌ Error al leer {path.name}: {e}")
        return None

def _kpi(title: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div style="border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:12px 14px;background:rgba(255,255,255,.03)">
          <div style="opacity:.8;font-size:.82rem">{title}</div>
          <div style="font-weight:800;font-size:1.6rem;margin-top:4px">{value}</div>
          <div style="opacity:.7;font-size:.78rem">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_noticias():
    st.subheader("📰 Noticias — bitácora del sorteo")

    news_path = ROOT / "noticias.csv"
    st.caption(f"📄 Ruta: {news_path} | existe={news_path.exists()}")

    if not news_path.exists():
        st.error("No encuentro `noticias.csv` en la raíz del repo.")
        return

    df = _load_csv(news_path)
    if df is None or df.empty:
        st.warning("`noticias.csv` vacío o ilegible.")
        return

    # Normalización de tipos esperados
    for col in ["noticia_relevante"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower().isin(["true", "1", "sí", "si", "y"])

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _kpi("Total noticias", f"{len(df)}")
    with c2:
        relevantes = int(df.get("noticia_relevante", pd.Series([False]*len(df))).sum())
        _kpi("Relevantes", f"{relevantes}", f"{relevantes/len(df)*100:.0f}% del total")
    with c3:
        try:
            em = pd.to_numeric(df.get("nivel_emocional_final", "0"), errors="coerce").fillna(0)
            _kpi("Emoción promedio", f"{em.mean():.0f}/100")
        except Exception:
            _kpi("Emoción promedio", "—")
    with c4:
        fechas = df.get("fecha", pd.Series())
        if not fechas.empty:
            _kpi("Rango fechas", f"{min(fechas)} → {max(fechas)}")
        else:
            _kpi("Rango fechas", "—")

    st.markdown("<hr style='opacity:.15'>", unsafe_allow_html=True)

    # ---------------- Filtros
    with st.expander("🔎 Filtros", expanded=True):
        colf, cols, colk, colr = st.columns([1, 1, 2, 1])

        fechas_opts = ["(todas)"] + sorted([f for f in df["fecha"].dropna().unique() if f])
        fecha_sel = colf.selectbox("Fecha", options=fechas_opts)

        sorteos = sorted(df.get("sorteo", pd.Series()).dropna().unique())
        sorteo_sel = cols.multiselect("Sorteo(s)", options=sorteos, default=[])

        q = colk.text_input("Buscar en titular/resumen/etiquetas", "")

        solo_rel = colr.checkbox("Solo relevantes", value=False)

        df_f = df.copy()
        if fecha_sel != "(todas)":
            df_f = df_f[df_f["fecha"] == fecha_sel]
        if sorteo_sel:
            df_f = df_f[df_f["sorteo"].isin(sorteo_sel)]
        if q.strip():
            qn = q.lower()
            df_f = df_f[
                df_f["titular"].str.lower().str.contains(qn, na=False) |
                df_f["resumen"].str.lower().str.contains(qn, na=False) |
                df_f["etiquetas"].str.lower().str.contains(qn, na=False)
            ]
        if solo_rel and "noticia_relevante" in df_f.columns:
            df_f = df_f[df_f["noticia_relevante"] == True]

        st.info(f"Coincidencias tras filtros: **{len(df_f)}**")

    # ---------------- Tabla
    st.dataframe(df_f, use_container_width=True, hide_index=True)

    # ---------------- Descarga
    fn = f"noticias_filtrado_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv"
    st.download_button(
        "⬇️ Descargar CSV filtrado",
        df_f.to_csv(index=False).encode("utf-8"),
        file_name=fn,
        mime="text/csv",
    )

    # ---------------- Vista rápida por sorteo
    with st.expander("📊 Resumen por sorteo"):
        if "sorteo" in df_f.columns:
            pv = df_f.groupby("sorteo")["id_noticia"].count().sort_values(ascending=False)
            st.bar_chart(pv)
        else:
            st.caption("No hay columna `sorteo`.")


     
