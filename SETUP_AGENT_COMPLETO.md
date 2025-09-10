# 🚀 SETUP COMPLETO PARA DAGSTER CLOUD HYBRID

## ✅ ESTADO ACTUAL
- **YAML Hybrid:** Configurado correctamente
- **Dockerfile:** Listo para containerización
- **GitHub Actions:** Workflow ejecutándose para construir imagen
- **Imagen objetivo:** `ghcr.io/Visionpro2025/vision_app:latest`

## 🔧 PASOS PARA PONER VERDE LA CODE LOCATION

### 1. VERIFICAR QUE LA IMAGEN SE ESTÉ CONSTRUYENDO
- Ve a GitHub → Actions
- Busca el workflow "build-and-push-image"
- Verifica que esté ejecutándose o haya terminado exitosamente
- La imagen debe estar en GitHub Packages

### 2. OBTENER TOKEN DEL AGENT
- Ve a Dagster Cloud → Settings → Tokens
- Crea un nuevo "Agent Token"
- Copia el token generado (empieza con `dct_`)

### 3. IDENTIFICAR TU ORGANIZACIÓN
- Mira la URL de Dagster Cloud (ej: `https://tuorg.dagster.cloud`)
- El nombre de tu org es la parte antes de `.dagster.cloud`

### 4. EJECUTAR EL AGENT
```bash
docker run -d --restart unless-stopped --name dagster-agent \
  -e DAGSTER_CLOUD_AGENT_TOKEN='TU_TOKEN_AQUI' \
  -e DAGSTER_CLOUD_URL='https://TU_ORG.dagster.cloud' \
  -e DAGSTER_CLOUD_DEPLOYMENT='prod' \
  gcr.io/dagster-cloud/dagster-cloud-agent:1.7.5
```

### 5. VERIFICAR QUE EL AGENT ESTÉ CORRIENDO
```bash
docker ps | grep dagster-agent
```

### 6. EN DAGSTER CLOUD
- Ve a Deployment → Agents
- Verifica que el Agent aparezca como "Online"

### 7. RECARGAR LA CODE LOCATION
- Ve a Code locations → vision_app → Reload
- Debe ponerse verde una vez que el Agent esté online

## 🎯 RESULTADO ESPERADO
- Agent corriendo y visible en Dagster Cloud
- Code location "vision_app" en estado verde
- Assets, Jobs y Schedules visibles en la UI

## 📋 CHECKLIST DE VERIFICACIÓN
- [ ] Imagen construida en GitHub Packages
- [ ] Agent token obtenido
- [ ] Organización identificada
- [ ] Agent ejecutándose localmente
- [ ] Agent visible como "Online" en Dagster Cloud
- [ ] Code location recargada
- [ ] Code location en estado verde
