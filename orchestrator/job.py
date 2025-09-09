from dagster import job, op, Out, Nothing
import os, json, datetime, subprocess, sys, pathlib, glob

REPORT_JSON = "reports/app_audit.json"   # ajusta si tu auditor guarda en otro nombre
STATE_DIR   = ".state"

# ---------- Utilidades ----------
def _ts():
    return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")

def _read_json(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo requerido: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------- OPS ----------
@op(out=Out(str))
def build_order_json():
    """Genera la orden para TU CLI sin tocar tu plan."""
    now = datetime.datetime.now().astimezone().isoformat()
    os.makedirs("orders", exist_ok=True)
    order = {
        "run_id": _ts(),
        "plan": "plans/pick3_pro.json",                # tu plan actual
        "inputs": {
            "now_et": now,
            "config_path": "config/protocolo_universal.yaml"
        }
    }
    path = pathlib.Path("orders/auto.json")
    path.write_text(json.dumps(order, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

@op(out=Out(str))
def run_protocolo(order_path: str):
    """Ejecuta tu FSM/CLI completo: step0..Z (tu app hace los pasos)."""
    cmd = [sys.executable, "-m", "app_vision", "run", "--order", order_path, "--state-dir", STATE_DIR]
    print(">> Ejecutando:", " ".join(cmd))
    res = subprocess.run(cmd, text=True, capture_output=True)
    print("---- STDOUT ----\n", res.stdout[-8000:])
    print("---- STDERR ----\n", res.stderr[-4000:])
    if res.returncode != 0:
        raise RuntimeError(f"Protocolo falló rc={res.returncode}")
    return REPORT_JSON  # devolver ruta esperada del reporte

@op(out=Out(dict))
def cargar_reporte(path_report: str):
    """Carga el reporte JSON de tu auditoría para validaciones."""
    return _read_json(path_report)

@op(out=Out(Nothing))
def validar_guardas(reporte: dict):
    """
    Corta 'OK vacíos'. Ajusta llaves si tu reporte usa otros campos.
    Espera algo como:
      reporte['news']['count'] >= 25
      reporte['candado_actual'] / reporte['candados_ultimos5']
    """
    # ---- Notas:
    # Cambia las rutas de las claves si tu app guarda con otros nombres.
    # Aplica defaults defensivos para no reventar si faltan claves.
    news_count = (
        reporte.get("news", {}).get("count")
        or reporte.get("paso4_news", {}).get("count")
        or reporte.get("stats", {}).get("news_count")
        or 0
    )
    candado_ok = bool(
        reporte.get("candado", {}).get("actual")
        or reporte.get("paso3", {}).get("candado")
        or reporte.get("sorteo_anterior", {}).get("candado")
    )
    ult5 = (
        reporte.get("historia", {}).get("candados_ultimos5")
        or reporte.get("paso6", {}).get("candados_ultimos5")
        or []
    )

    # ---- Reglas duras (ajústalas si tu protocolo las cambió):
    if not candado_ok:
        raise RuntimeError("Guard: candado actual NO disponible en el reporte (Paso 3).")
    if news_count < 25:
        raise RuntimeError(f"Guard: noticias insuficientes ({news_count}<25) (Paso 4).")
    if len(ult5) < 5:
        raise RuntimeError("Guard: faltan 5 candados históricos (Paso 6).")

    print(f"✔ Guardas OK → noticias={news_count}, ult5={len(ult5)}")

@op(out=Out(Nothing))
def publicar_artifacts(_reporte: dict):
    """Deja info útil en logs y confirma existencia de artefactos."""
    # Muestra archivos relevantes para descargar desde Dagster
    matches = []
    for p in ["reports/.json", "reports/.md", f"{STATE_DIR}/state.sqlite"]:
        matches += glob.glob(p)
    if not matches:
        print("Aviso: no se hallaron artifacts en 'reports/' ni .state/")
    else:
        print("Artifacts generados:")
        for m in matches:
            print(" -", m)

@job
def protocolo_universal_job():
    reporte_path = run_protocolo(build_order_json())
    rep = cargar_reporte(reporte_path)
    validar_guardas(rep)
    publicar_artifacts(rep)
