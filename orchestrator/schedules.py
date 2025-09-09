from dagster import schedule
from .job import protocolo_universal_job

# Los cron en Dagster Cloud son UTC.
# Ajusta por DST según te convenga (ET≈UTC-4/5).
@schedule(cron_schedule="31 10 * * *", job=protocolo_universal_job)  # 06:31 ET
def protocolo_am(_): return {}

@schedule(cron_schedule="11 18 * * *", job=protocolo_universal_job)  # 14:11 ET
def protocolo_mid(_): return {}

@schedule(cron_schedule="21 02 * * *", job=protocolo_universal_job)  # 22:21 ET
def protocolo_eve(_): return {}
