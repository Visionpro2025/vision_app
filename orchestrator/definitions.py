from dagster import Definitions
from .jobs import protocolo_universal_job
from .schedules import protocolo_am, protocolo_mid, protocolo_eve

# Aquí puedes añadir recursos/config si luego quieres secretos, etc.
defs = Definitions(
    jobs=[protocolo_universal_job],
    schedules=[protocolo_am, protocolo_mid, protocolo_eve],
)
