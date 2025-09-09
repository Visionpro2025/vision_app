from dagster import job, op
import json, subprocess, datetime, os, sys, pathlib

@op
def build_order_json():
    """Genera la orden para tu CLI, sin tocar tu plan/orden actuales."""
    now = datetime.datetime.now().astimezone().isoformat()
    os.makedirs("orders", exist_ok=True)
    order = {
        "run_id": datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S"),
        "plan": "plans/pick3_pro.json",
        "inputs": {
            "now_et": now,
            "config_path": "config/protocolo_universal.yaml"
        }
    }
    path = pathlib.Path("orders/auto.json")
    path.write_text(json.dumps(order, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)

@op
def run_protocolo(order_path: str):
    """Ejecuta tu Protocolo Universal tal cual, usando tu CLI."""
    cmd = [sys.executable, "-m", "app_vision", "run", "--order", order_path, "--state-dir", ".state"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"[Protocolo FAIL] rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    # Opcional: imprime una línea clave al log de Dagster
    print(proc.stdout[-4000:])
    return "OK"

@job
def protocolo_universal_job():
    run_protocolo(build_order_json())
