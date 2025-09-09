from dagster import Definitions
from .job import protocolo_universal_job
from .schedules import protocolo_am, protocolo_mid, protocolo_eve

defs = Definitions(
    jobs=[protocolo_universal_job],
    schedules=[protocolo_am, protocolo_mid, protocolo_eve],
)
