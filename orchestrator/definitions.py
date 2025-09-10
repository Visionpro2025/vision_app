from dagster import Definitions

# Importa tu job y schedules desde los módulos locales
from .job import protocolo_universal_job, protocolo_analysis_job
from .schedules import protocolo_am, protocolo_mid, protocolo_eve

# === assets: vision_app pipeline ===
# Import assets from the assets directory
from .assets.news_ingest import news_ingest, news_ingest_metadata
from .assets.gematria_transform import gematria_transform, gematria_metadata
from .assets.tabla100_convert import tabla100_convert, tabla100_metadata
from .assets.subliminal_score import subliminal_score, subliminal_metadata
from .assets.analysis_aggregate import analysis_aggregate, analysis_summary
from .assets.healthcheck import healthcheck

# DEFINITIONS: este objeto es lo que Dagster Cloud carga
defs = Definitions(
    jobs=[protocolo_universal_job, protocolo_analysis_job],
    schedules=[protocolo_am, protocolo_mid, protocolo_eve],
    assets=[
        # News ingestion pipeline
        news_ingest,
        news_ingest_metadata,
        
        # Analysis pipeline
        gematria_transform,
        gematria_metadata,
        tabla100_convert,
        tabla100_metadata,
        subliminal_score,
        subliminal_metadata,
        
        # Final aggregation
        analysis_aggregate,
        analysis_summary,
        
        # Health check
        healthcheck,
    ],
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
