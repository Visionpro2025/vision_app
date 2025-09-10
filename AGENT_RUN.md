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

### 1. **Obtener el Token del Agent:**
   - Ve a Dagster Cloud → Settings → Tokens
   - Crea un nuevo "Agent Token"
   - Copia el token generado

### 2. **Identificar tu organización y deployment:**
   - URL de tu organización: `https://<TU_ORG>.dagster.cloud`
   - Nombre del deployment: `prod` (por defecto) o el que configuraste
   - Para encontrar tu org: mira la URL cuando estés en Dagster Cloud

### 3. **Verificar imagen en GHCR:**
   - Ve a GitHub → Packages → vision_app
   - Verifica que la imagen `ghcr.io/Visionpro2025/vision_app:latest` esté publicada
   - Si es privada, cambia a "Public" o configura credenciales en el Agent

### 4. **Ejecutar el comando:**
   - Sustituye `<TOKEN>`, `<TU_ORG>`, y `<DEPLOYMENT>` con tus valores reales
   - Ejecuta el comando docker run

### 5. **Verificar que el Agent esté corriendo:**
   ```bash
   docker ps | grep dagster-agent
   ```

### 6. **En Dagster Cloud:**
   - Ve a Deployment → Agents
   - Verifica que el Agent aparezca como "Online"

## Ejemplo con valores reales:
```bash
# Reemplaza estos valores con los tuyos:
docker run -d --restart unless-stopped --name dagster-agent \
  -e DAGSTER_CLOUD_AGENT_TOKEN='dct_xxxxxxxxxxxxxxxx' \
  -e DAGSTER_CLOUD_URL='https://tuorg.dagster.cloud' \
  -e DAGSTER_CLOUD_DEPLOYMENT='prod' \
  gcr.io/dagster-cloud/dagster-cloud-agent:1.7.5
```

## Nota importante:
Sin el Agent corriendo, la code location nunca se pondrá verde en un deployment Hybrid.
