from dagster import job, op, define_asset_job

@op
def start_protocol():
    return "✅ Protocolo Universal inicializado"

@job(tags={"env": "cloud", "pipeline": "vision_app"})
def protocolo_universal_job():
    start_protocol()

# === Asset job for the complete analysis pipeline ===
protocolo_analysis_job = define_asset_job(
    name="protocolo_analysis_job",
    description="Complete analysis pipeline: news ingestion -> gematria -> tabla100 -> subliminal -> aggregation",
    selection=["analysis_aggregate", "analysis_summary"],
    tags={"env": "cloud", "pipeline": "vision_app"}
)
