# === TODO-EN-UNO: Verificar paquete, deps, push y redeploy Dagster Cloud ===
import os, sys, subprocess, textwrap, json, pathlib

REPO = pathlib.Path.cwd()  # asume que estás en el repo vision_app
PKG = REPO / "orchestrator"
INIT = PKG / "__init__.py"
DEFS = PKG / "definitions.py"

# 1) Asegura estructura mínima del paquete
PKG.mkdir(exist_ok=True)
if not INIT.exists():
    INIT.write_text("from .definitions import defs\n", encoding="utf-8")
if not DEFS.exists():
    DEFS.write_text(textwrap.dedent("""
    from dagster import Definitions, job, op

    @op
    def hello_op():
        return "hello from serverless"

    @job
    def hello_job():
        hello_op()

    defs = Definitions(jobs=[hello_job])
    """).lstrip(), encoding="utf-8")

# 2) requirements mínimos (ajusta si tienes más libs)
REQ = REPO / "requirements.txt"
if not REQ.exists():
    REQ.write_text("dagster==1.11.9\ndagster-cloud==1.11.9\n", encoding="utf-8")

# 3) Verifica import local
print("🔎 Verificando import local de orchestrator.defs ...")
try:
    sys.path.insert(0, str(REPO))
    m = __import__("orchestrator")
    _ = m.defs  # debe existir
    print("✅ Import OK (orchestrator.defs encontrado)")
except Exception as e:
    print("❌ Import local falló:", e)
    raise SystemExit(1)

# 4) Git add/commit/push
def run(cmd):
    print("→", " ".join(cmd))
    subprocess.run(cmd, check=True)

try:
    run(["git", "add", "orchestrator", "requirements.txt"])
    run(["git", "commit", "-m", "chore: ensure orchestrator package and requirements for serverless"])
except subprocess.CalledProcessError:
    print("ℹ Nada nuevo para commitear (ok)")

run(["git", "push", "origin", "main"])

# 5) Configura CLI de Dagster Cloud (TOKEN + URL)
os.environ["DAGSTER_CLOUD_API_TOKEN"] = "TU_TOKEN_AQUI"   # 👈 PON TU TOKEN AQUÍ
os.environ["DAGSTER_CLOUD_URL"] = "https://vision-protocolo.dagster.cloud"
DEPLOYMENT = "prod"
LOCATION = "vision_app"

# 6) Redeploy y logs
print("\n🚀 Redeploy de la ubicación...")
try:
    run(["dagster-cloud", "deployment", "update-location", LOCATION, "--deployment", DEPLOYMENT, "--verbose"])
except subprocess.CalledProcessError as e:
    print(f"❌ Error en redeploy: {e}")
    print("💡 Asegúrate de configurar tu token de API correctamente")

print("\n📜 Logs (tail, si falla verás el traceback):")
try:
    subprocess.run(["dagster-cloud", "deployment", "list-locations"])
except subprocess.CalledProcessError as e:
    print(f"⚠️ No se pudieron obtener logs: {e}")

print("\n📊 Estado de la ubicación:")
try:
    subprocess.run(["dagster-cloud", "deployment", "list-locations"])
except subprocess.CalledProcessError as e:
    print(f"⚠️ No se pudo verificar estado: {e}")
