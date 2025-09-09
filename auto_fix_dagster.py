# === Verificación + Corrección + Push automático ===
import os
import subprocess
from pathlib import Path

# 1. Confirmar ruta base del repo
repo = Path(r"C:\Users\DAMILARE\vision_app")   # cambia si tu ruta es otra
os.chdir(repo)

print(f"📂 Revisando repo en: {repo.resolve()}")

# 2. Crear carpeta orchestrator si no existe
orch_dir = repo / "orchestrator"
orch_dir.mkdir(exist_ok=True)
print("✅ Carpeta orchestrator lista")

# 3. Verificar __init__.py
init_file = orch_dir / "__init__.py"
init_content = "from .definitions import defs\n"
if not init_file.exists() or init_content.strip() not in init_file.read_text():
    init_file.write_text(init_content)
    print("🔧 __init__.py corregido con import defs")
else:
    print("✅ __init__.py correcto")

# 4. Verificar definitions.py
defs_file = orch_dir / "definitions.py"
if not defs_file.exists():
    defs_content = """from dagster import Definitions, job, op

@op
def hola_op():
    return "Hola Dagster Cloud!"

@job
def hola_job():
    hola_op()

defs = Definitions(jobs=[hola_job])
"""
    defs_file.write_text(defs_content)
    print("🔧 definitions.py creado con un job de ejemplo")
else:
    text = defs_file.read_text()
    if "defs" not in text:
        text += "\n\n# Añadiendo defs por si faltaba\n"
        text += (
            "from dagster import Definitions\n"
            "defs = Definitions()\n"
        )
        defs_file.write_text(text)
        print("🔧 definitions.py actualizado con defs")
    else:
        print("✅ definitions.py contiene defs")

# 5. Verificar requirements.txt
req_file = repo / "requirements.txt"
base_reqs = ["dagster", "dagster-cloud"]
if not req_file.exists():
    req_file.write_text("\n".join(base_reqs) + "\n")
    print("🔧 requirements.txt creado con dependencias base")
else:
    text = req_file.read_text().splitlines()
    added = False
    for r in base_reqs:
        if not any(line.startswith(r) for line in text):
            text.append(r)
            added = True
    if added:
        req_file.write_text("\n".join(text) + "\n")
        print("🔧 requirements.txt actualizado con dependencias faltantes")
    else:
        print("✅ requirements.txt con dependencias correctas")

# 6. Git add / commit / push automático
print("\n📤 Subiendo cambios al repositorio...")
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "fix estructura dagster serverless"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=True)

print("\n🚀 Todo listo: repo verificado, corregido y sincronizado con GitHub.")
print("👉 Ahora ve a Dagster Cloud y haz 'Redeploy'.")
