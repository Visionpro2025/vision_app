from dagster import job, op

@op
def start_protocol():
    return "✅ Protocolo Universal inicializado"

@job
def protocolo_universal():
    start_protocol()
