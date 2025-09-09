from dagster import job, op

@op
def start_protocol():
    return "✅ Protocolo Universal inicializado"

@job
def protocolo_universal_job():
    start_protocol()
