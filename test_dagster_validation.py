# === CELDA DE VALIDACIÓN DAGSTER ===
import importlib

try:
    defs = importlib.import_module("orchestrator.definitions").defs

    print("🔮 Resumen de Definitions cargado")

    # Jobs definidos
    jobs = [j.name for j in defs.jobs]
    print("✅ Jobs encontrados:", jobs if jobs else "Ninguno")

    # Schedules definidos
    schedules = [s.name for s in defs.schedules]
    print("✅ Schedules encontrados:", schedules if schedules else "Ninguno")

    # Sensors definidos
    if hasattr(defs, "sensors"):
        sensors = [s.name for s in defs.sensors]
        print("✅ Sensors encontrados:", sensors if sensors else "Ninguno")

    print("🎯 Validación completada sin errores")

except Exception as e:
    print("⚠ Error al validar defs:", e)
