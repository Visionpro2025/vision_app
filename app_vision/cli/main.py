from __future__ import annotations
import argparse, json, os, sys, importlib
from app_vision.engine.fsm import run_plan
from app_vision.cli.status import status_cmd

def main(argv=None):
    parser = argparse.ArgumentParser(prog="app_vision", description="Protocol Engine Pro CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Ejecuta un plan con una orden JSON")
    p_run.add_argument("--order", required=True, help="Ruta a la orden JSON")
    p_run.add_argument("--state-dir", default=".state", help="Directorio de estado")

    p_status = sub.add_parser("status", help="Muestra el estado de una ejecución")
    p_status.add_argument("--run-id", required=True, help="ID de la ejecución")
    p_status.add_argument("--state-dir", default=".state", help="Directorio de estado")

    args = parser.parse_args(argv)
    importlib.import_module("app_vision.steps")

    if args.cmd == "run":
        with open(args.order, "r", encoding="utf-8") as f:
            order = json.load(f)
        if "plan" not in order:
            print("La orden debe incluir 'plan' (.json).", file=sys.stderr); return 2
        return run_plan(order["plan"], order, state_dir=args.state_dir)
    elif args.cmd == "status":
        return status_cmd(args.state_dir, args.run_id) or 0

if __name__ == "__main__":
    raise SystemExit(main())
