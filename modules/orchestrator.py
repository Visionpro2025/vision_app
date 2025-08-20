 # modules/orchestrator.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import traceback

import streamlit as st
import pandas as pd

from .logger_setup import get_logger

# ===== Rutas base y carpetas de trabajo
ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS" / "ORCHESTRATOR"
RUNS.mkdir(parents=True, exist_ok=True)

LOG = get_logger("orchestrator")

# ====== utilidades cacheadas
@st.cache_data(show_spinner=False)
def _load_csv(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        LOG.exception("Error leyendo %s", path)
        st.error(f"Error al leer {path.name}: {e}")
        return None

def _save_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ====== chequeos de salud por capa
def _check_bibliography():
    corpus = ROOT / "__CORPUS" / "GEMATRIA"
    needed = ["bibliography.md"]
    missing = [f for f in needed if not (corpus / f).exists()]
    if missing:
        return False, f"Falta: {', '.join(missing)}"
    return True, "OK (bibliografía base presente)."
def _check_noticias():
    p = ROOT / "noticias.csv"
    if not p.exists():
        return False, "No se encontró noticias.csv"
    df = _load_csv(p)
    if df is None or df.empty:
        return False, "noticias.csv vacío o ilegible"
    cols_req = {
        "id_noticia","fecha","sorteo","pais","fuente",
        "titular","resumen","etiquetas",
    }
    if not cols_req.issubset(set(df.columns)):
        faltan = cols_req - set(df.columns)
        return False, f"Columnas faltantes en noticias.csv: {', '.join(sorted(faltan))}"
    return True, f"OK ({len(df)} filas)."

def _check_t70():
    p = ROOT / "T70.csv"
    if not p.exists():
        return False, "No se encontró T70.csv"
    df = _load_csv(p)
    if df is None or df.empty:
        return False, "T70.csv vacío o ilegible"
    return True, f"OK ({len(df)} filas)."

def _check_gematria():
    try:
        from . import gematria  # solo prueba de import
        return True, "OK (módulo importado)."
    except Exception as e:
        LOG.exception("Error importando gematria")
        return False, f"Fallo import gematria: {e}"

def _check_subliminal():
    try:
        from .subliminal_module import extraer_mensaje_subliminal  # noqa
        return True, "OK (módulo importado)."
    except Exception as e:
        LOG.exception("Error importando subliminal_module")
        return False, f"Fallo import subliminal: {e}"

# ====== pasos de pipeline
def step_noticias():
    ok, msg = _check_noticias()
    if not ok:
        raise RuntimeError(msg)
    LOG.info("Noticias listas: %s", msg)
    return msg

def step_gematria(dry_run: bool = True):
    """
    Placeholder: valida módulo. Si en el futuro agregas un batch,
    aquí leerá noticias y generará __RUNS/GEMATRIA/*.csv
    """
    ok, msg = _check_gematria()
    if not ok:
        raise RuntimeError(msg)
    if dry_run:
        LOG.info("Gematría (dry-run): %s", msg)
        return "Gematría verificada (dry-run)."
    # Aquí iría la ejecución real cuando exista función batch
    return "Gematría ejecutada."

def step_subliminal():
    ok, msg = _check_subliminal()
    if not ok:
        raise RuntimeError(msg)

    from .subliminal_module import extraer_mensaje_subliminal  # usa tu backend real
    df = _load_csv(ROOT / "noticias.csv")
    assert df is not None
    out_rows = []
    for _, r in df.iterrows():
        text = " ".join([
            str(r.get("titular", "")),
            str(r.get("resumen", "")),
            str(r.get("etiquetas", "")),
        ])
        res = extraer_mensaje_subliminal(text)
        out_rows.append({
            "id_noticia": r.get("id_noticia", ""),
            "emocion": res["emocion"],
            "intensidad": res["intensidad"],
            "arquetipo": res["arquetipo"],
            "mensaje": res["mensaje"],
            "timestamp": datetime.utcnow().isoformat(timespec="seconds")+"Z",
        })
    df_out = pd.DataFrame(out_rows)
    out_path = RUNS / f"subliminal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    df_out.to_csv(out_path, index=False, encoding="utf-8")
    LOG.info("Subliminal exportado: %s", out_path.name)
    return f"Subliminal exportado: {out_path.name}"

def step_consolidar():
    """
    Placeholder: ejemplo para consolidar salidas de capas en un único reporte.
    """
    # Por ahora solo indica que el paso existe
    return "Consolidación (placeholder)."

# ====== UI
def render_orchestrator():
    st.header("⏱️ Orquestador de capas (pipeline)")
    st.caption(f"Base: `{ROOT}`  ·  Runs: `__RUNS/ORCHESTRATOR`")

    # Estado rápido de salud
    with st.expander("✅ Chequeos rápidos (salud de capas)", expanded=True):
        for name, fn in [
            ("📰 Noticias", _check_noticias),
            ("📊 T70", _check_t70),
            ("🔤 Gematría", _check_gematria),
            ("🌀 Subliminal", _check_subliminal),
        ]:
            ok, msg = fn()
            icon = "✅" if ok else "⚠️"
            st.write(f"**{name}** — {icon} {msg}")

    st.write("---")
    st.subheader("▶️ Ejecutar pipeline")

    colA, colB, colC, colD = st.columns(4)
    with colA:
        run_news = st.checkbox("Noticias", value=True)
    with colB:
        run_gem = st.checkbox("Gematría (dry-run)", value=True)
    with colC:
        run_sub = st.checkbox("Subliminal", value=True)
    with colD:
        run_cons = st.checkbox("Consolidar", value=False)

    run_btn = st.button("🚀 Ejecutar ahora", use_container_width=True)

    if not run_btn:
        return

    # Bitácora de la corrida
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_log = {
        "run_id": run_id,
        "started_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "steps": [],
        "status": "running",
    }
    log_path = RUNS / f"run_{run_id}.json"
    _save_json(run_log, log_path)

    steps = []
    if run_news: steps.append(("Noticias", step_noticias))
    if run_gem:  steps.append(("Gematría", step_gematria))
    if run_sub:  steps.append(("Subliminal", step_subliminal))
    if run_cons: steps.append(("Consolidación", step_consolidar))

    prog = st.progress(0, text="Iniciando…")
    status_box = st.empty()

    try:
        for i, (label, fn) in enumerate(steps, start=1):
            status_box.info(f"Ejecutando **{label}** …")
            LOG.info("Paso: %s", label)
            result_msg = fn()
            run_log["steps"].append({"step": label, "ok": True, "msg": result_msg})
            _save_json(run_log, log_path)
            prog.progress(int(i / max(len(steps),1) * 100), text=f"{label} ✓")

        run_log["status"] = "success"
        run_log["finished_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        _save_json(run_log, log_path)
        st.success("Pipeline finalizado correctamente ✅")
        st.code(json.dumps(run_log, ensure_ascii=False, indent=2))

    except Exception as e:
        LOG.exception("Pipeline: error en ejecución")
        run_log["status"] = "error"
        run_log["error"] = f"{type(e).__name__}: {e}"
        run_log["traceback"] = traceback.format_exc()
        run_log["finished_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        _save_json(run_log, log_path)
        st.error(f"❌ Error: {e}")
        st.exception(e)
