# 🛠 Scripts de Verificación - Dagster Cloud

## Scripts Disponibles

### 1. `check_deps.py` - Verificación de Dependencias
Verifica que todas las dependencias necesarias estén instaladas localmente.

```bash
python scripts/check_deps.py
```

**Qué verifica:**
- dagster, dagster_cloud, pandas, requests
- feedparser, beautifulsoup4, numpy, openai, python-dotenv

**Uso recomendado:**
- Antes de hacer push a GitHub
- Antes de desplegar en Dagster Cloud
- En CI/CD pipelines

### 2. `verify_cloud_deployment.py` - Verificación de Cloud
Guía para verificar que el despliegue en Dagster Cloud esté funcionando correctamente.

```bash
python scripts/verify_cloud_deployment.py
```

**Qué verifica:**
- Code location en verde
- Assets materializados correctamente
- Schedules activos con timezone correcto

**Uso recomendado:**
- Después de conectar el repo a Dagster Cloud
- Después de configurar secretos
- Después de activar schedules

## Flujo de Trabajo Recomendado

### Antes del Despliegue
```bash
# 1. Verificar dependencias
python scripts/check_deps.py

# 2. Smoke test local
python -c "from orchestrator import defs; print('OK defs')"
python orchestrator/_smoke_cloud_import.py

# 3. Hacer push
git add .
git commit -m "feat: new feature"
git push origin main
```

### Después del Despliegue
```bash
# 1. Verificar despliegue en Cloud
python scripts/verify_cloud_deployment.py

# 2. Seguir las instrucciones del script
# 3. Verificar en la UI de Dagster Cloud
```

## Troubleshooting

### Dependencias Faltantes
Si `check_deps.py` marca dependencias faltantes:
1. Instala la dependencia: `pip install <nombre>`
2. Agrega a `requirements.txt` si no está
3. Ejecuta el script nuevamente

### Verificación de Cloud Falla
Si `verify_cloud_deployment.py` indica problemas:
1. Revisa la UI de Dagster Cloud
2. Verifica que los secretos estén configurados
3. Revisa los logs de los runs
4. Consulta `ROLLBACK_PLAN.md` si es necesario

## Notas Importantes

- Los scripts son **solo de verificación**, no modifican nada
- Siempre ejecuta `check_deps.py` antes de hacer push
- Usa `verify_cloud_deployment.py` después de cada despliegue
- Mantén los scripts actualizados cuando agregues nuevas dependencias
