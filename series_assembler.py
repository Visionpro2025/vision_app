# modules/series_assembler.py — Ensamblador por sorteo
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS"; RUNS.mkdir(parents=True, exist_ok=True)
OUT = RUNS / "SERIES"; OUT.mkdir(parents=True, exist_ok=True)

def _load_optional_csv(p: Path) -> pd.DataFrame:
    try: return pd.read_csv(p, dtype=str, encoding="utf-8")
    except: return pd.DataFrame()

def render_series_assembler(current_lottery: str):
    st.caption(f"Lotería activa: **{current_lottery}**")
    st.subheader("Parámetros de ensamblado")

    c1, c2, c3 = st.columns(3)
    with c1:
        n_series = st.number_input("Cantidad de series", min_value=1, max_value=50, value=5, step=1)
    with c2:
        len_series = st.number_input("Longitud de cada serie", min_value=1, max_value=10, value=6, step=1)
    with c3:
        seed = st.text_input("Semilla (opcional)", value="")

    st.markdown("**Insumos** (cuando existan): Gematría consolidada, Subliminal, Números visibles, Noticias filtradas.")
    # Cargar insumos (si están)
    g_news = sorted((ROOT / "__RUNS" / "GEMATRIA").glob("gematria_news_*.csv"))
    s_news = sorted((ROOT / "__RUNS" / "SUBLIMINAL").glob("subliminal_news_*.csv"))

    st.caption(f"Gematría: {len(g_news)} archivos · Subliminal: {len(s_news)} archivos")

    if st.button("⚙️ Ensamblar ahora", type="primary", use_container_width=True):
        # TODO: conectar lógica real; por ahora simulado
        rows = []
        from random import Random
        R = Random(seed or datetime.utcnow().isoformat())

        for i in range(int(n_series)):
            serie = sorted(R.sample(range(1, 71), int(len_series)))  # ejemplo 1..70
            rows.append({
                "loteria": current_lottery,
                "serie_id": f"{current_lottery.upper()}-{datetime.utcnow().strftime('%Y%m%d')}-{i+1:02d}",
                "numeros": " ".join(map(str, serie)),
                "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "fuente": "simulado_v0 (pendiente integrar Gematría/Subliminal)",
            })

        df_out = pd.DataFrame(rows)
        st.dataframe(df_out, use_container_width=True, hide_index=True)

        fn = f"series_{current_lottery}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv"
        outp = OUT / fn
        df_out.to_csv(outp, index=False, encoding="utf-8")
        st.success(f"✅ Guardado: {outp}")
        st.download_button("⬇️ Descargar series", df_out.to_csv(index=False).encode("utf-8"), file_name=fn, mime="text/csv", use_container_width=True)
