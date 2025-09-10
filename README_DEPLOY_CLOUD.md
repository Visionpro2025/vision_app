# 🚀 Despliegue en Dagster Cloud (Serverless)

## Requisitos Previos

- Cuenta de Dagster Cloud (Serverless)
- Repositorio conectable a Dagster Cloud
- API keys para servicios de noticias (opcional, modo demo disponible)

## Estructura del Proyecto

```
vision_app/
├── orchestrator/           # Paquete principal de Dagster
│   ├── __init__.py        # Exporta defs
│   ├── definitions.py     # Definitions con assets/jobs/schedules
│   ├── assets/           # Assets del pipeline
│   ├── job.py            # Jobs definidos
│   └── schedules.py      # Schedules configurados
├── modules/              # Módulos de análisis (no modificados)
├── dagster_cloud.yaml   # Configuración de Cloud
└── requirements.txt     # Dependencias
```

## Pasos de Despliegue

### 1. Conectar Repositorio a Dagster Cloud

1. Ve a tu organización de Dagster Cloud
2. Navega a **Settings** → **Code locations**
3. Haz clic en **Add location**
4. Selecciona **Git** y conecta tu repositorio
5. Configura:
   - **Location name**: `vision_app`
   - **Code source**: `orchestrator` (package_name)
   - **Python version**: 3.11+

### 2. Verificar Importación

Dagster Cloud instalará automáticamente las dependencias de `requirements.txt` e importará el paquete `orchestrator`, cargando `defs`.

### 3. Verificar en la UI

En la UI de Dagster Cloud, deberías ver:

**Assets (10):**
- `news_ingest` → `gematria_transform` → `tabla100_convert` → `subliminal_score` → `analysis_aggregate`
- Assets de metadatos correspondientes

**Jobs (2):**
- `protocolo_universal_job`
- `protocolo_analysis_job`

**Schedules (3):**
- `protocolo_am` (06:31 ET)
- `protocolo_mid` (14:11 ET)
- `protocolo_eve` (22:21 ET)

### 4. Configurar Secretos

1. Ve a **Settings** → **Secrets**
2. Agrega las variables de entorno (ver `SECRETS.md`):
   ```
   NEWS_API_KEY=tu_api_key_aqui
   GNEWS_API_KEY=tu_api_key_aqui
   BING_API_KEY=tu_api_key_aqui
   ```

**Nota**: Sin API keys, el sistema funcionará en modo demo.

### 5. Lanzar Primer Run

#### Opción A: Materializar Asset Final
1. Ve a **Assets**
2. Busca `analysis_aggregate`
3. Haz clic en **Materialize**

#### Opción B: Ejecutar Job Completo
1. Ve a **Jobs**
2. Selecciona `protocolo_analysis_job`
3. Haz clic en **Launch run**

### 6. Activar Schedules (Opcional)

1. Ve a **Schedules**
2. Activa los schedules deseados:
   - `protocolo_am` (mañana)
   - `protocolo_mid` (mediodía)
   - `protocolo_eve` (noche)

## Troubleshooting

### ImportError
- **Problema**: Dependencia faltante
- **Solución**: Verificar `requirements.txt` incluye todas las dependencias necesarias

### KeyError/None en Secretos
- **Problema**: Variable de entorno no definida
- **Solución**: Configurar secretos en Dagster Cloud Settings

### Row count 0 en Ingestión
- **Problema**: Fuente RSS/API no disponible
- **Solución**: Verificar API keys o usar modo demo

### Error de Importación de Módulos
- **Problema**: Módulos en `modules/` no encontrados
- **Solución**: Verificar que `modules/` esté en el repositorio

## Estructura del Pipeline

```
news_ingest (fuente de noticias)
    ↓
gematria_transform (análisis gemátrico)
    ↓
tabla100_convert (conversión a tabla 100)
    ↓
subliminal_score (análisis subliminal)
    ↓
analysis_aggregate (agregación final)
    ↓
analysis_summary (resumen estadístico)
```

## Monitoreo

- **Assets**: Monitorea el estado de materialización
- **Jobs**: Revisa logs de ejecución
- **Schedules**: Verifica ejecuciones automáticas
- **Secrets**: Confirma que las variables estén configuradas

## Soporte

Para problemas específicos:
1. Revisa los logs en la UI de Dagster Cloud
2. Verifica la configuración de secretos
3. Confirma que todas las dependencias estén instaladas
4. Consulta la documentación de Dagster Cloud
