# ✅ Checklist de Verificación — Dagster Cloud (Serverless)

## Code Location
- [ ] Code Location vision_app creada y en verde
- [ ] dagster_cloud.yaml detectado y válido (package_name: orchestrator)

## Defs / Import
- [ ] from orchestrator import defs importable en Cloud
- [ ] Assets listados (incluye analysis_aggregate)
- [ ] Jobs listados (protocolo_universal_job, protocolo_analysis_job si existe)
- [ ] Schedules listados (protocolo_am, protocolo_mid, protocolo_eve)

## Timezone y Tags
- [ ] execution_timezone="America/Chicago" en todos los schedules
- [ ] Tags estándar en jobs {"env":"cloud","pipeline":"vision_app"}

## Secretos (Dagster Cloud → Settings → Secrets)
- [ ] NEWS_API_KEY
- [ ] GNEWS_API_KEY
- [ ] BING_API_KEY

## Runs
- [ ] Asset healthcheck materializado con status OK
- [ ] analysis_aggregate materializado con metadatos (row_count, columns, shape)

## Observabilidad
- [ ] Notificaciones de Run Failure configuradas (Email/Slack)
- [ ] Tags adicionales (opcional) version=<commit>

## Troubleshooting rápido
- ImportError → dependencia faltante en requirements.txt / pyproject.toml
- ValueError de env_check → secreto no definido en Cloud
- row_count=0 → fuente vacía o API sin datos; validar claves / fuente

## Secretos — estado

### Detectadas (en código)
- NEWS_API_KEY
- GNEWS_API_KEY
- BING_API_KEY

### Objetivo (las tres)
- NEWS_API_KEY
- GNEWS_API_KEY
- BING_API_KEY

### Pendientes
- [ ] NEWS_API_KEY (por confirmar en Cloud)
- [ ] GNEWS_API_KEY (por confirmar en Cloud)
- [ ] BING_API_KEY (por confirmar en Cloud)

## Comandos de Verificación Local

```bash
# Verificar importabilidad
python -c "from orchestrator import defs; print('OK defs')"

# Smoke test completo
python orchestrator/_smoke_cloud_import.py
```

## Notas Importantes

- **Timezone**: Todos los schedules configurados para America/Chicago (CT/CST)
- **Tags**: Jobs etiquetados con {"env":"cloud","pipeline":"vision_app"}
- **Validación**: Env_check integrado en news_ingest para validación temprana de secretos
- **Health Check**: Asset healthcheck disponible para monitoreo del sistema
