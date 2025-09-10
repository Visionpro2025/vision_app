from dagster import schedule
from .job import protocolo_universal_job

# Los cron en Dagster Cloud son UTC.
# Ajusta por DST según te convenga (ET≈UTC-4/5).
@schedule(cron_schedule="31 10 * * *", job=protocolo_universal_job, execution_timezone="America/Chicago")  # 06:31 CT
def protocolo_am(_): return {}

@schedule(cron_schedule="11 18 * * *", job=protocolo_universal_job, execution_timezone="America/Chicago")  # 14:11 CT
def protocolo_mid(_): return {}

@schedule(cron_schedule="21 02 * * *", job=protocolo_universal_job, execution_timezone="America/Chicago")  # 22:21 CT
def protocolo_eve(_): return {}
