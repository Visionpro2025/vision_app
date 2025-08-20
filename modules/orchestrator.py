# modules/orchestrator.py
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd

# ===== Rutas base
ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS" / "ORCHESTRATOR"
RUNS.mkdir(parents=True, exist_ok=True)

# ===== Utilidades mínimas
def _load_csv_safe(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer {path.name}: {e}")
        return None

# ===== Chequeos de salud muy básicos
def _check_noticias() -> tuple[bool, str]:
    path = ROOT / "noticias.csv"
    if not path.exists():
        return False, "No se encontró noticias.csv en la raíz."
    df = _load_csv_safe(path)
    if df is None or df.empty:
        return False, "noticias.csv está vacío o ilegible."
    return True, f"OK ({len(df)} filas)."

def _check_t70() -> tuple[bool, str]:
    path = ROOT / "T70.csv"
    if not path.exists():
        return False, "No se encontró T70.csv en la raíz."
    df = _load_csv_safe(path)
    if df is None or df.empty:
        return False, "T70.csv está vacío o ilegible."
    return True, f"OK ({len(df)} filas)."

def _check_gematria() -> tuple[bool, str]:
    # Chequeo simple: que el módulo exista y se pueda importar
    try:
        from modules.gematria import show_gematria  # noqa: F401
        return True, "OK (módulo importado)."
    except Exception as e:
        return False, f"No se pudo importar modules/gematria.py: {e}"

def _check_subliminal() -> tuple[bool, str]:
    try:
        from modules.subliminal_module import render_subliminal  # noqa: F401
        return True, "OK (módulo importado)."
    except Exception as e:
        return False, f"No se pudo importar modules/subliminal_module.py: {e}"

# ===== Ejecutores (llaman a cada vista en un expander)
def _run_noticias():
    from modules.noticias_module import render_noticias
    with st.expander("📰 Noticias (vista)", expanded=False):
        render_noticias()

def _run_gematria():
    from modules.gematria import show_gematria
    with st.expander("🔤 Gematría (vista)", expanded=False):
        show_gematria()

def _run_subliminal():
    from modules.subliminal_module import render_subliminal
    with st.expander("🌀 Análisis del mensaje subliminal (vista)", expanded=False):
        render_subliminal()

def _run_t70():
    path = ROOT / "T70.csv"
    with st.expander("📊 Tabla T70 (vista)", expanded=False):
        if path.exists():
            df = _load_csv_safe(path)
            if df is not None:
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("No se encontró T70.csv")

# ===== Vista principal del orquestador
def render_orchestrator():
    st.subheader("🧭 Orquestador de capas (esqueleto)")

    # Estado rápido
    c1, c2, c3, c4 = st.columns(4)
    ok_news, msg_news = _check_noticias()
    ok_t70, msg_t70 = _check_t70()
    ok_gem, msg_gem = _check_gematria()
    ok_sub, msg_sub = _check_subliminal()

    with c1:
        st.metric("📰 Noticias", "OK ✅" if ok_news else "Revisar ⚠️")
        st.caption(msg_news)
    with c2:
        st.metric("📊 T70", "OK ✅" if ok_t70 else "Revisar ⚠️")
        st.caption(msg_t70)
    with c3:
        st.metric("🔤 Gematría", "OK ✅" if ok_gem else "Revisar ⚠️")
        st.caption(msg_gem)
    with c4:
        st.metric("🌀 Subliminal", "OK ✅" if ok_sub else "Revisar ⚠️")
        st.caption(msg_sub)

    st.divider()

    # Orden de ejecución
    st.markdown("### Orden de ejecución")
    opciones = ["📰 Noticias", "🔤 Gematría", "🌀 Subliminal", "📊 T70"]
    order = st.multiselect(
        "Selecciona y ordena (usa el orden visual):",
        options=opciones,
        default=["📰 Noticias", "🔤 Gematría", "🌀 Subliminal"]
    )
    st.caption("Orden propuesto: " + (" → ".join(order) if order else "(ninguno)"))

    detener_en_fallo = st.checkbox("Detener si una capa clave falla", value=True)

    if st.button("▶️ Ejecutar"):
        st.info(f"Iniciando pipeline a las {datetime.utcnow().strftime('%H:%M:%SZ')}…")
        for step in order:
            # Chequeo previo por paso
            if step == "📰 Noticias":
                ok, msg = ok_news, msg_news
            elif step == "🔤 Gematría":
                ok, msg = ok_gem, msg_gem
            elif step == "🌀 Subliminal":
                ok, msg = ok_sub, msg_sub
            elif step == "📊 T70":
                ok, msg = ok_t70, msg_t70
            else:
                ok, msg = False, "Paso desconocido."

            if not ok:
                st.error(f"❌ {step}: {msg}")
                if detener_en_fallo:
                    st.warning(f"⛔ Pipeline detenido en **{step}** por política de bloqueo.")
                    return
                else:
                    st.info("Se continúa por tolerancia…")

            # Ejecución de la vista correspondiente
            try:
                if step == "📰 Noticias":
                    _run_noticias()
                elif step == "🔤 Gematría":
                    _run_gematria()
                elif step == "🌀 Subliminal":
                    _run_subliminal()
                elif step == "📊 T70":
                    _run_t70()
            except Exception as e:
                st.exception(e)
                if detener_en_fallo:
                    st.warning(f"⛔ Pipeline detenido por error en **{step}**.")
                    return

        st.success("✅ Pipeline finalizado.")
