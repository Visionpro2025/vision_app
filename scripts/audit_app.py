# scripts/audit_app.py
# Auditoría integral de App.Vision (sin dependencias externas)
# Analiza estructura, planes, steps, encadenamiento, locks, y ejecuta runs controlados.
from __future__ import annotations
import os, sys, json, re, subprocess, datetime, hashlib, glob, importlib.util, traceback
from typing import Any, Dict, List, Tuple

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORT_DIR = os.path.join(REPO, "reports")
RAW_DIR = os.path.join(REPORT_DIR, "raw")
STATE_DIR = os.path.join(REPO, ".state_audit")
ORDERS_DIR = os.path.join(REPO, "orders")
PLANS_DIR = os.path.join(REPO, "app_vision", "plans")
STEPS_PKG = "app_vision.steps"
ENGINE_FSM = "app_vision.engine.fsm"

# Agregar el directorio raíz al PYTHONPATH
if REPO not in sys.path:
    sys.path.insert(0, REPO)

def sh(cmd: List[str]) -> Tuple[int,str,str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()

def safe_read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def list_tree(root: str) -> List[Dict[str, Any]]:
    out = []
    for base, _, files in os.walk(root):
        if ".venv" in base or "__pycache__" in base or ".git" in base or ".state" in base:
            continue
        for fn in files:
            p = os.path.join(base, fn)
            try:
                st = os.stat(p)
                out.append({"path": os.path.relpath(p, root), "bytes": st.st_size})
            except Exception:
                pass
    return sorted(out, key=lambda x: x["path"])

def try_import(modname: str) -> Tuple[bool, str]:
    try:
        __import__(modname)
        return True, ""
    except Exception as e:
        return False, f"{e.__class__.__name__}: {e}"

def load_plans() -> List[str]:
    return sorted(glob.glob(os.path.join(PLANS_DIR, "*.json")))

def read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_orders_for_plan(plan_path: str) -> List[str]:
    matches = []
    for p in glob.glob(os.path.join(ORDERS_DIR, "*.json")):
        try:
            j = read_json(p)
            if os.path.abspath(j.get("plan","")).replace("\\","/") == os.path.abspath(plan_path).replace("\\","/"):
                matches.append(p)
        except Exception:
            continue
    return sorted(matches)

CHAIN_RE = re.compile(r"\$\{step\.([a-zA-Z0-9_\-]+)\.([a-zA-Z0-9_\-\.]+)\}")

def scan_chaining(inputs: Any) -> List[Tuple[str,str]]:
    refs = []
    def walk(v):
        if isinstance(v,str):
            for m in CHAIN_RE.finditer(v):
                refs.append((m.group(1), m.group(2)))
        elif isinstance(v,dict):
            for x in v.values(): walk(x)
        elif isinstance(v,list):
            for x in v: walk(x)
    walk(inputs)
    return refs

def make_probe_order(plan_path: str) -> Dict[str, Any]:
    # Orden "segura" para planes típicos (Pick3). Si no aplica, el run fallará con InputError (esperado).
    run_id = os.path.splitext(os.path.basename(plan_path))[0] + "-AUDIT-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return {
        "run_id": run_id,
        "plan": os.path.relpath(plan_path, REPO).replace("\\","/"),
        "inputs": {
            "prev_draw": [4,7,9],
            "label": "AM",
            "game": "Pick3_FL"
        }
    }

def main():
    os.makedirs(REPORT_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(STATE_DIR, exist_ok=True)
    os.makedirs(ORDERS_DIR, exist_ok=True)

    report: Dict[str, Any] = {
        "meta": {
            "timestamp": datetime.datetime.now().isoformat(),
            "repo": REPO,
            "python": sys.version,
        },
        "structure": list_tree(REPO),
        "imports": {},
        "engine": {},
        "plans": [],
        "runs": [],
        "findings": [],
        "recommendations": []
    }

    # 1) Import sanity
    ok_steps, err_steps = try_import(STEPS_PKG)
    ok_engine, err_engine = try_import(ENGINE_FSM)
    report["imports"]["steps"] = {"ok": ok_steps, "error": err_steps}
    report["imports"]["engine_fsm"] = {"ok": ok_engine, "error": err_engine}

    # 2) Engine features (Pro)
    if ok_engine:
        import app_vision.engine.fsm as fsm
        features = {
            "has_register_step": hasattr(fsm, "register_step"),
            "has_run_plan": hasattr(fsm, "run_plan"),
            "has_interpolation": hasattr(fsm, "INTERP_RE"),
        }
        report["engine"]["features"] = features
        # Save raw registry if accessible
        reg = getattr(fsm, "STEP_REGISTRY", {})
        report["engine"]["step_registry_count"] = len(reg)
        with open(os.path.join(RAW_DIR, "step_registry.json"), "w", encoding="utf-8") as f:
            json.dump(sorted(list(reg.keys())), f, ensure_ascii=False, indent=2)

    # 3) Plans audit
    plan_paths = load_plans()
    if not plan_paths:
        report["findings"].append({"level":"error","msg":"No se encontraron planes en app_vision/plans/*.json"})
    for plan_path in plan_paths:
        item = {"plan": os.path.relpath(plan_path, REPO).replace("\\","/")}
        try:
            plan = read_json(plan_path)
            item["name"] = plan.get("name")
            item["config"] = plan.get("config", {})
            item["defaults"] = plan.get("defaults", {})
            steps = plan.get("steps", [])
            item["step_count"] = len(steps)
            # lock
            if not item["config"].get("_lock_hash"):
                report["findings"].append({"level":"warn","plan":item["plan"],"msg":"Plan sin config._lock_hash"})
            # step existence & chaining
            seq_names = []
            chain_ok = True
            for s in steps:
                sname, sclass = s.get("name"), s.get("class")
                seq_names.append(sname)
                if ok_engine:
                    import app_vision.engine.fsm as fsm
                    reg = getattr(fsm, "STEP_REGISTRY", {})
                    if sclass not in reg:
                        report["findings"].append({"level":"error","plan":item["plan"],"msg":f"Clase de paso no registrada: {sclass} (step={sname})"})
                refs = scan_chaining(s.get("inputs", {}))
                for ref_step, _ in refs:
                    if ref_step not in seq_names:
                        chain_ok = False
                        report["findings"].append({"level":"error","plan":item["plan"],"msg":f"Referencia a paso futuro/no definido: ${{step.{ref_step}.…}} en {sname}"})
            item["chaining_ok"] = chain_ok
        except Exception as e:
            item["error"] = f"{e.__class__.__name__}: {e}"
            report["findings"].append({"level":"error","plan":os.path.relpath(plan_path, REPO),"msg":f"Error leyendo plan: {e}"})
        report["plans"].append(item)

    # 4) Probe runs por plan (si existe order para ese plan, úsala; sino, generamos una orden segura)
    for plan_path in plan_paths:
        orders = find_orders_for_plan(plan_path)
        order_json = None
        if orders:
            order_json = orders[0]
            order = read_json(order_json)
        else:
            order = make_probe_order(plan_path)
            order_json = os.path.join(ORDERS_DIR, f"_audit_-{os.path.basename(order['run_id'])}.json")
            with open(order_json, "w", encoding="utf-8") as f:
                json.dump(order, f, ensure_ascii=False, indent=2)

        code, out, err = sh([sys.executable, "-m", "app_vision", "run", "--order", order_json, "--state-dir", STATE_DIR])
        run_item = {
            "plan": os.path.relpath(plan_path, REPO).replace("\\","/"),
            "order": os.path.relpath(order_json, REPO).replace("\\","/"),
            "return_code": code,
            "stdout_tail": "\n".join(out.splitlines()[-20:]),
            "stderr_tail": "\n".join(err.splitlines()[-20:]),
        }
        # Status CLI (si existe)
        code_s, out_s, err_s = sh([sys.executable, "-m", "app_vision", "status", "--run-id", order["run_id"], "--state-dir", STATE_DIR])
        run_item["status_cli"] = {"code": code_s, "stdout": out_s, "stderr": err_s}
        report["runs"].append(run_item)

    # 5) Recomendaciones rápidas
    if not ok_engine:
        report["recommendations"].append("No se puede importar el motor (engine.fsm). Verifica rutas y __init__.py.")
    if ok_engine and report["engine"].get("step_registry_count",0) == 0:
        report["recommendations"].append("El registro de pasos está vacío. Asegúrate de importar app_vision.steps en el CLI antes de run.")
    for p in report["plans"]:
        if p.get("step_count",0) == 0:
            report["recommendations"].append(f"Plan {p.get('plan')} sin pasos. Revisa la definición.")
        if p.get("chaining_ok") is False:
            report["recommendations"].append(f"Corrige referencias ${{step…}} en {p.get('plan')}: deben apuntar a pasos previos en el plan.")
        cfg = (p.get("config") or {})
        if not cfg.get("_lock_hash"):
            report["recommendations"].append(f"Agrega config._lock_hash al plan {p.get('plan')} para congelar versiones.")

    # 6) Guardar reportes
    os.makedirs(REPORT_DIR, exist_ok=True)
    with open(os.path.join(REPORT_DIR, "app_audit.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Markdown compacto
    md = []
    md.append(f"# App.Vision · Auditoría\n\nFecha: {report['meta']['timestamp']}\nRepo: {report['meta']['repo']}\n")
    md.append("## Importación\n")
    for k,v in report["imports"].items():
        md.append(f"- {k}: {'OK' if v['ok'] else 'ERROR'} {'' if v['ok'] else '('+v['error']+')'}")
    if "features" in report.get("engine", {}):
        feats = report["engine"]["features"]
        md.append("\n## Motor\n- register_step: {0}\n- run_plan: {1}\n- interpolación: {2}\n- pasos registrados: {3}".format(
            feats.get("has_register_step"), feats.get("has_run_plan"), feats.get("has_interpolation"),
            report["engine"].get("step_registry_count",0)
        ))
    md.append("\n## Planes\n")
    for p in report["plans"]:
        md.append(f"- *{p.get('plan')}* — pasos: {p.get('step_count')} | chaining_ok: {p.get('chaining_ok')} | lock: {bool((p.get('config') or {}).get('_lock_hash'))}")
        if p.get("error"):
            md.append(f"  - Error: {p['error']}")
    md.append("\n## Runs de prueba\n")
    for r in report["runs"]:
        md.append(f"- Plan {r['plan']} → Orden {r['order']} → código: {r['return_code']}")
        if r["status_cli"]["code"] == 0:
            md.append("  - status:\n\n" + r["status_cli"]["stdout"] + "\n")
        else:
            md.append("  - sin status CLI (no implementado o error)")
    if report["findings"]:
        md.append("\n## Hallazgos\n")
        for fnd in report["findings"]:
            plan = fnd.get("plan","")
            md.append(f"- [{fnd['level'].upper()}] {plan} {fnd['msg']}")
    if report["recommendations"]:
        md.append("\n## Recomendaciones\n")
        for rec in report["recommendations"]:
            md.append(f"- {rec}")
    with open(os.path.join(REPORT_DIR, "app_audit.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"OK: reporte generado en {os.path.join(REPORT_DIR, 'app_audit.md')}")
    print(f"JSON: {os.path.join(REPORT_DIR, 'app_audit.json')}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit as se:
        raise
    except Exception as e:
        print("ERROR inesperado:", e)
        traceback.print_exc()
        sys.exit(99)
