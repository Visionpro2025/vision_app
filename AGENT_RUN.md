# Agent Run Instructions for Dagster Cloud Hybrid

## Comando Docker para el Agent

```bash
docker run -d --restart unless-stopped --name dagster-agent \
  -e DAGSTER_CLOUD_AGENT_TOKEN='<TOKEN>' \
  -e DAGSTER_CLOUD_URL='https://<ORG>.dagster.cloud' \
  -e DAGSTER_CLOUD_DEPLOYMENT='<DEPLOYMENT>' \
  gcr.io/dagster-cloud/dagster-cloud-agent:1.7.5
```

## Pasos para configurar el Agent:

1. **Obtener el Token del Agent:**
   - Ve a Dagster Cloud → Settings → Agents
   - Copia el token del Agent

2. **Identificar tu organización y deployment:**
   - URL de tu organización: `https://<ORG>.dagster.cloud`
   - Nombre del deployment: `<DEPLOYMENT>`

3. **Hacer la imagen accesible:**
   - Ve a GitHub → Packages → vision_app
   - Cambia la visibilidad a "Public" si es necesario
   - O configura el Agent con credenciales de GHCR

4. **Ejecutar el comando:**
   - Sustituye `<TOKEN>`, `<ORG>`, y `<DEPLOYMENT>` con tus valores reales
   - Ejecuta el comando docker run

5. **Verificar que el Agent esté corriendo:**
   ```bash
   docker ps | grep dagster-agent
   ```

6. **En Dagster Cloud:**
   - Ve a Deployment → Agents
   - Verifica que el Agent aparezca como "Online"

## Nota importante:
Sin el Agent corriendo, la code location nunca se pondrá verde en un deployment Hybrid.
