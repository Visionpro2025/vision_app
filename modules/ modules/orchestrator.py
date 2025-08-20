# modules/orchestrator.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import traceback

import streamlit as st
import pandas as pd

# ====== rutas base
ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS" / "ORCHESTRATOR"
RUNS.mkdir(parents=True, exist_ok=True)

# ====== requisitos conocidos por capa
NEWS_REQUIRED_COLS = [
    "id_noticia","fecha","sorteo","pais","fuente",
    "titular","resumen","etiquetas",
]
GEM_CORPUS_FILES = [
    "lexicon_hebrew.yaml",
    "translit_table.csv",
    "stopwords_es.txt",
    "stopwords_en.txt",
    "patterns.yaml",
    "bibliography.md",
]

# ====== utilidades
def _load_csv_safe(path: Path) -> pd.DataFrame | None:
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception as e:
        st.error(f"Error al leer {path.name}: {e}")
        return None

def _log_event(kind: str, payload: dict):
    payload = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "kind": kind,
        **payload,
    }
    fn = RUNS / f"orchestrator_{datetime.utcnow().strftime('%Y%m%d')}.log.jsonl"
    with fn.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

# ====== chequeos de salud por capa
def check_noticias() -> dict:
    path = ROOT / "noticias.csv"
    ok_path = path.exists()
    cols_ok, rows = False, 0
    details = []
    if ok_path:
        df = _load_csv_safe(path)
        if df is not None:
            rows = len(df)
            missing = [c for c in NEWS_REQUIRED_COLS if c not in df.columns]
            cols_ok = len(missing) == 0
            if not cols_ok:
                details.append(f"Faltan columnas: {', '.join(missing)}")
    return {
        "name": "Noticias",
        "exists": ok_path,
        "schema_ok": cols_ok,
        "rows": rows,
        "details": details,
        "path": str(path),
        "blocking": ok_path and cols_ok,
    }

def check_t70() -> dict:
    path = ROOT / "T70.csv"
    ok = path.exists()
    return {
        "name": "Tabla T70",
        "exists": ok,
        "schema_ok": True,   # por ahora solo exigimos existencia
        "rows": len(_load_csv_safe(path)) if ok else 0,
        "details": [],
        "path": str(path),
        "blocking": ok,
    }

def check_gematria() -> dict:
    corpus = ROOT / "__CORPUS" / "GEMATRIA"
    missing = [f for f in GEM_CORPUS_FILES if not (corpus / f).exists()]
    return {
        "name": "Gematría",
        "exists": corpus.exists(),
        "schema_ok": len(missing) == 0,
        "rows": 0,
        "details": ([] if not missing else [f"Corpus incompleto: faltan {', '.join(missing)}"]),
        "path": str(corpus),
        "blocking": corpus.exists() and len(missing) == 0,
    }

def check_subliminal() -> dict:
    try:
        from modules.subliminal_module import _get_pipelines  # type: ignore
        pipes = _get_pipelines()
        senti = bool(pipes.get("sentiment"))
        zsc = bool(pipes.get("zsc"))
        return {
            "name": "Subliminal",
            "exists": True,
            "schema_ok": True,
            "rows": 0,
            "details": [f"sentiment={'OK' if senti else 'no'} | zsc={'OK' if zsc else 'no'}"],
            "path": "modules/subliminal_module.py",
            "blocking": True,  # no bloqueamos por falta de modelos; hay plan B
        }
    except Exception as e:
        return {
            "name": "Subliminal",
            "exists": False,
            "schema_ok": False,
            "rows": 0,
            "details": [f"Error importando módulo: {e}"],
            "path": "modules/subliminal_module.py",
            "blocking": False,
        }

CHECKS = {
    "Noticias": check_noticias,
    "Gematría": check_gematria,
    "Subliminal": check_subliminal,
    "Tabla T70": check_t70,
}

# ====== ejecución (placeholder que llama a cada vista si se desea)
def _run_step(step: str):
    if step == "Noticias":
        import importlib, modules.noticias_module as mod
        importlib.reload(mod)
        with st.expander("📄 Noticias (vista)", expanded=False):
            mod.render_noticias()
    elif step == "Gematría":
        from modules.gematria import show_gematria
        with st.expander("🔠 Gematría (vista)", expanded=False):
            show_gematria()
    elif step == "Subliminal":
        from modules.subliminal_module import render_subliminal
        with st.expander("🌀 Subliminal (vista)", expanded=False):
            render_subliminal()
    elif step == "Tabla T70":
        path = ROOT / "T70.csv"
        with st.expander("📊 T70 (vista)", expanded=False):
            if path.exists():
                df = _load_csv_safe(path)
                if df is not None:
                    st.dataframe(df, use_container_width=True)
            else:
                st.warning("No se encontró T70.csv")

# ====== UI principal
def render_orchestrator():
    st.subheader("🧭 Orquestador de capas")

    # ---- estado actual / health
    st.markdown("### Estado actual de las capas")
    results = []
    cols = st.columns(4)
    for i, name in enumerate(["Noticias", "Gematría", "Subliminal", "Tabla T70"]):
        res = CHECKS[name]()
        results.append(res)
        with cols[i]:
            ok = res["exists"] and res["schema_ok"]
            st.metric(
                label=name,
                value="OK ✅" if ok else "Revisar ⚠️",
                delta=f"rows={res['rows']}" if res['rows'] else ""
            )
            if res["details"]:
                for d in res["details"]:
                    st.caption(d)

    # ---- orden de ejecución
    st.markdown("### Orden de ejecución")
    default_order = ["Noticias", "Gematría", "Subliminal"]
    order = st.multiselect(
        "Selecciona y ordena (usa el orden mostrado):",
        options=["Noticias", "Gematría", "Subliminal", "Tabla T70"],
        default=default_order
    )
    # mantener el orden como aparece en 'order'
    st.caption(f"Orden propuesto: {' → '.join(order) if order else '(ninguno)'}")

    # ---- política de bloqueos
    stop_on_warning = st.checkbox(
        "Detener si una capa crítica falla (recomendado)", value=True
    )

    # ---- ejecutar
    if st.button("▶️ Ejecutar pipeline en este orden"):
        _log_event("start", {"order": order, "stop_on_warning": stop_on_warning})
        stopped = False
        for step in order:
            res = CHECKS[step]()
            # notificación previa
            if not (res["exists"] and res["schema_ok"]):
                st.error(f"❌ {step}: requisito no cumplido.")
                for d in res["details"]:
                    st.write("•", d)
                _log_event("warn", {"step": step, "details": res["details"]})
                if stop_on_warning and res.get("blocking", True):
                    st.warning(f"⛔ Pipeline detenido en **{step}** por política de bloqueos.")
                    _log_event("stopped", {"step": step})
                    stopped = True
                    break
                else:
                    st.info("Se continúa por política de tolerancia…")

            try:
                _run_step(step)
                _log_event("run", {"step": step, "status": "ok"})
            except Exception as e:
                st.exception(e)
                _log_event("run_error", {"step": step, "error": str(e), "tb": traceback.format_exc()})
                if stop_on_warning:
                    st.warning(f"⛔ Pipeline detenido por error en **{step}**.")
                    stopped = True
                    break

        if not stopped:
            st.success("✅ Pipeline finalizado.")

    # ---- utilidades
    with st.expander("🗒️ Bitácora del orquestador", expanded=False):
        logs = sorted(RUNS.glob("orchestrator_*.log.jsonl"))
        if logs:
            sel = st.selectbox("Archivo", [x.name for x in logs])
            data = [json.loads(l) for l in (RUNS / sel).read_text(encoding="utf-8").splitlines() if l.strip()]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.caption("Sin registros aún.")