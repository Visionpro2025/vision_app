from dagster import Definitions

# Importa tu job y schedules desde los módulos locales
from .job import protocolo_universal_job
from .schedules import protocolo_am, protocolo_mid, protocolo_eve

# DEFINITIONS: este objeto es lo que Dagster Cloud carga
defs = Definitions(
    jobs=[protocolo_universal_job],
    schedules=[protocolo_am, protocolo_mid, protocolo_eve],
)

# === DEBUG / RESUMEN LOCAL ===
if __name__ == "__main__":
    print("🔮 Resumen de Definitions cargado")
    try:
        jobs = [j.name for j in defs.jobs]
        print("Jobs encontrados:", jobs if jobs else "Ninguno")
        schedules = [s.name for s in defs.schedules]
        print("Schedules encontrados:", schedules if schedules else "Ninguno")
        print("✅ Definitions OK")
    except Exception as e:
        print("⚠ Error al inspeccionar defs:", e)
