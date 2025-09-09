from dagster import schedule
from .jobs import protocolo_universal_job

# Horarios ET; Dagster Cloud interpreta cron en UTC: ajusta si te conviene
# Ejemplo: 06:31 ET ≈ 10:31 UTC (según DST)
@schedule(cron_schedule="31 10 * * *", job=protocolo_universal_job)  # AM
def protocolo_am(_): return {}

@schedule(cron_schedule="11 18 * * *", job=protocolo_universal_job)  # MID
def protocolo_mid(_): return {}

@schedule(cron_schedule="21 02 * * *", job=protocolo_universal_job)  # EVE
def protocolo_eve(_): return {}
