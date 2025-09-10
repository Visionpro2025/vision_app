# SECRETS - Dagster Cloud Configuration

## Variables de Entorno Detectadas

Las siguientes variables de entorno son utilizadas por el sistema de noticias:

### Variables Requeridas

- **NEWS_API_KEY**: API key para News API (https://newsapi.org/)
- **GNEWS_API_KEY**: API key para GNews API (https://gnews.io/)
- **BING_API_KEY**: API key para Bing News Search API

### Configuración de Zona Horaria

Los schedules están configurados para ejecutarse en **America/Chicago** (CT/CST).

### Configuración en Dagster Cloud

1. Ve a **Settings** → **Secrets** en tu organización de Dagster Cloud
2. Agrega cada variable con su valor correspondiente:
   ```
   NEWS_API_KEY=tu_api_key_aqui
   GNEWS_API_KEY=tu_api_key_aqui
   BING_API_KEY=tu_api_key_aqui
   ```

### Configuración Local

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
NEWS_API_KEY=tu_api_key_aqui
GNEWS_API_KEY=tu_api_key_aqui
BING_API_KEY=tu_api_key_aqui
```

### Uso en el Código

Las variables se acceden mediante `st.secrets.get()` en los módulos de noticias:

```python
# En modules/noticias_module.py
self.news_api_key = st.secrets.get("NEWS_API_KEY", "")
self.gnews_api_key = st.secrets.get("GNEWS_API_KEY", "")
self.bing_api_key = st.secrets.get("BING_API_KEY", "")
```

### Modo Demo

Si no se proporcionan las API keys, el sistema funciona en modo demo con noticias de ejemplo.

### Notas de Seguridad

- **NUNCA** subas las API keys al repositorio
- Usa el archivo `.env` solo para desarrollo local
- Configura las variables en Dagster Cloud para producción
