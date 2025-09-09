# config/news_apis_config.py — Configuración de APIs de Noticias Profesionales

"""
CONFIGURACIÓN DE APIS DE NOTICIAS PROFESIONALES

Este archivo contiene la configuración para las APIs de noticias utilizadas
en el sistema de ingestión profesional de noticias.

REQUISITOS:
1. Obtener API keys de los servicios correspondientes
2. Configurar las keys en el archivo .streamlit/secrets.toml
3. Verificar límites de uso y cuotas de cada API

APIS DISPONIBLES:
- NewsAPI: https://newsapi.org/
- GNews: https://gnews.io/
- Bing News Search: https://www.microsoft.com/en-us/bing/apis/bing-news-search-api
"""

# =================== CONFIGURACIÓN DE APIS ===================

# NewsAPI (https://newsapi.org/)
NEWS_API_CONFIG = {
    "base_url": "https://newsapi.org/v2",
    "endpoints": {
        "everything": "/everything",
        "top_headlines": "/top-headlines",
        "sources": "/sources"
    },
    "rate_limits": {
        "free_tier": "100 requests/day",
        "developer": "1,000 requests/day",
        "business": "10,000 requests/day"
    },
    "features": [
        "Búsqueda en tiempo real",
        "Filtros por fecha, idioma, país",
        "Ordenamiento por relevancia, popularidad, fecha",
        "Detección de idioma automática"
    ]
}

# GNews (https://gnews.io/)
GNEWS_API_CONFIG = {
    "base_url": "https://gnews.io/api/v4",
    "endpoints": {
        "search": "/search",
        "top_headlines": "/top-headlines",
        "topic": "/topic"
    },
    "rate_limits": {
        "free_tier": "100 requests/day",
        "paid_tier": "1,000+ requests/day"
    },
    "features": [
        "Búsqueda en tiempo real",
        "Filtros por país, idioma, tema",
        "Detección de sentimiento",
        "Categorización automática"
    ]
}

# Bing News Search (Microsoft)
BING_NEWS_CONFIG = {
    "base_url": "https://api.bing.microsoft.com/v7.0",
    "endpoints": {
        "news_search": "/news/search",
        "news_trending": "/news/trendingtopics"
    },
    "rate_limits": {
        "free_tier": "1,000 requests/month",
        "paid_tier": "3,000+ requests/month"
    },
    "features": [
        "Búsqueda avanzada con Bing",
        "Filtros por fecha, idioma, región",
        "Detección de entidades",
        "Análisis de sentimiento"
    ]
}

# =================== CONFIGURACIÓN DE FUENTES CONFIABLES ===================

TRUSTED_SOURCES_CONFIG = {
    "tier_1": {
        "description": "Fuentes de máxima confiabilidad",
        "sources": [
            "reuters.com",
            "ap.org",
            "bloomberg.com",
            "wsj.com",
            "nytimes.com"
        ],
        "weight": 1.0
    },
    "tier_2": {
        "description": "Fuentes de alta confiabilidad",
        "sources": [
            "washingtonpost.com",
            "theguardian.com",
            "cnn.com",
            "abcnews.go.com",
            "cbsnews.com"
        ],
        "weight": 0.8
    },
    "tier_3": {
        "description": "Fuentes de confiabilidad media",
        "sources": [
            "nbcnews.com",
            "foxnews.com",
            "usatoday.com",
            "politico.com",
            "npr.org"
        ],
        "weight": 0.6
    }
}

# =================== CONFIGURACIÓN DE TEMAS PRIORITARIOS ===================

PRIORITY_TOPICS_CONFIG = {
    "economia_dinero": {
        "description": "Noticias económicas y financieras de alto impacto",
        "keywords": [
            "inflation", "recession", "unemployment", "wages", "salaries", "crisis",
            "markets", "stocks", "economy", "financial", "banking", "debt",
            "housing", "real estate", "mortgage", "interest rates", "fed", "federal reserve"
        ],
        "weight": 1.0
    },
    "politica_justicia": {
        "description": "Noticias políticas y de justicia social",
        "keywords": [
            "protest", "demonstration", "civil rights", "voting rights", "election",
            "supreme court", "congress", "senate", "house", "legislation", "law",
            "justice", "police", "reform", "policy", "government", "administration"
        ],
        "weight": 0.9
    },
    "seguridad_social": {
        "description": "Noticias de seguridad y orden social",
        "keywords": [
            "crime", "violence", "protest", "migration", "immigration", "border",
            "security", "threat", "attack", "shooting", "riot", "unrest",
            "social unrest", "civil unrest", "disorder", "chaos", "emergency"
        ],
        "weight": 0.8
    }
}

# =================== CONFIGURACIÓN DE ANÁLISIS EMOCIONAL ===================

EMOTION_ANALYSIS_CONFIG = {
    "emotions": {
        "ira": {
            "description": "Sentimientos de enojo y frustración",
            "keywords": ["anger", "furious", "outrage", "rage", "fury", "wrath", "hostile"],
            "weight": 0.8
        },
        "miedo": {
            "description": "Sentimientos de temor y ansiedad",
            "keywords": ["fear", "terror", "panic", "horror", "dread", "anxiety", "worry"],
            "weight": 0.9
        },
        "esperanza": {
            "description": "Sentimientos de optimismo y confianza",
            "keywords": ["hope", "optimism", "confidence", "trust", "faith", "belief"],
            "weight": 0.6
        },
        "tristeza": {
            "description": "Sentimientos de pena y desesperación",
            "keywords": ["sadness", "grief", "sorrow", "despair", "melancholy", "depression"],
            "weight": 0.7
        },
        "orgullo": {
            "description": "Sentimientos de dignidad y logro",
            "keywords": ["pride", "dignity", "honor", "respect", "achievement", "success"],
            "weight": 0.5
        }
    },
    "impact_thresholds": {
        "minimum_score": 0.6,
        "high_impact": 0.8,
        "critical_impact": 0.9
    }
}

# =================== CONFIGURACIÓN DE FILTROS ===================

FILTER_CONFIG = {
    "content_requirements": {
        "min_title_length": 10,
        "min_content_length": 50,
        "max_title_length": 200
    },
    "time_filters": {
        "default_hours": 24,
        "max_hours": 72,
        "date_format": "%Y-%m-%d"
    },
    "quality_filters": {
        "exclude_duplicates": True,
        "exclude_spam": True,
        "exclude_low_impact": True,
        "semantic_deduplication": True
    }
}

# =================== INSTRUCCIONES DE CONFIGURACIÓN ===================

SETUP_INSTRUCTIONS = """
INSTRUCCIONES DE CONFIGURACIÓN:

1. OBTENER API KEYS:
   - NewsAPI: https://newsapi.org/register
   - GNews: https://gnews.io/register
   - Bing News: https://www.microsoft.com/en-us/bing/apis/bing-news-search-api

2. CONFIGURAR SECRETS:
   Crear archivo .streamlit/secrets.toml con:
   
   [secrets]
   NEWS_API_KEY = "tu_api_key_aqui"
   GNEWS_API_KEY = "tu_api_key_aqui"
   BING_API_KEY = "tu_api_key_aqui"

3. VERIFICAR LÍMITES:
   - Revisar cuotas de cada API
   - Configurar rate limiting si es necesario
   - Monitorear uso de APIs

4. TESTING:
   - Probar cada API individualmente
   - Verificar respuestas y formatos
   - Validar filtros y procesamiento
"""

# =================== FUNCIONES DE UTILIDAD ===================

def get_api_status():
    """Retorna el estado de configuración de las APIs."""
    import streamlit as st
    
    status = {
        "news_api": bool(st.secrets.get("NEWS_API_KEY", "")),
        "gnews": bool(st.secrets.get("GNEWS_API_KEY", "")),
        "bing_news": bool(st.secrets.get("BING_API_KEY", ""))
    }
    
    return status

def get_available_apis():
    """Retorna las APIs disponibles según la configuración."""
    status = get_api_status()
    available = []
    
    if status["news_api"]:
        available.append("NewsAPI")
    if status["gnews"]:
        available.append("GNews")
    if status["bing_news"]:
        available.append("Bing News")
    
    return available

def validate_configuration():
    """Valida la configuración completa del sistema."""
    import streamlit as st
    
    errors = []
    warnings = []
    
    # Verificar API keys
    if not st.secrets.get("NEWS_API_KEY", ""):
        warnings.append("NewsAPI key no configurada")
    
    if not st.secrets.get("GNEWS_API_KEY", ""):
        warnings.append("GNews API key no configurada")
    
    if not st.secrets.get("BING_API_KEY", ""):
        warnings.append("Bing News API key no configurada")
    
    # Verificar que al menos una API esté configurada
    if not any([st.secrets.get("NEWS_API_KEY", ""), 
                st.secrets.get("GNEWS_API_KEY", ""), 
                st.secrets.get("BING_API_KEY", "")]):
        errors.append("No hay APIs configuradas. El sistema no funcionará.")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

# =================== EJEMPLO DE USO ===================

if __name__ == "__main__":
    print("🔧 CONFIGURACIÓN DE APIS DE NOTICIAS PROFESIONALES")
    print("=" * 60)
    
    # Mostrar estado de configuración
    try:
        status = get_api_status()
        print(f"📊 Estado de APIs:")
        for api, configured in status.items():
            status_icon = "✅" if configured else "❌"
            print(f"   {status_icon} {api}: {'Configurada' if configured else 'No configurada'}")
        
        # Mostrar APIs disponibles
        available = get_available_apis()
        if available:
            print(f"\n🚀 APIs disponibles: {', '.join(available)}")
        else:
            print("\n⚠️ No hay APIs configuradas")
        
        # Validar configuración
        validation = validate_configuration()
        if validation["valid"]:
            print("\n✅ Configuración válida")
        else:
            print(f"\n❌ Errores de configuración:")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        if validation["warnings"]:
            print(f"\n⚠️ Advertencias:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
        
    except Exception as e:
        print(f"\n❌ Error al verificar configuración: {e}")
        print("\n📋 Instrucciones de configuración:")
        print(SETUP_INSTRUCTIONS)








