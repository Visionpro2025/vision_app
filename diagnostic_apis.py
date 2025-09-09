#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO DE APIS - VISION PREMIUM
Para verificar el estado de las APIs de noticias
"""

import streamlit as st
import requests
import time
from datetime import datetime

def test_api_connection(api_name, base_url, api_key, endpoint="/"):
    """Prueba la conexión a una API específica."""
    try:
        headers = {}
        if api_key and api_key != "tu_api_key_aqui":
            if "newsapi" in api_name.lower():
                headers["X-API-Key"] = api_key
            elif "bing" in api_name.lower():
                headers["Ocp-Apim-Subscription-Key"] = api_key
            elif "gnews" in api_name.lower():
                # GNews usa el API key como parámetro
                pass
        
        # Construir URL de prueba
        if "newsapi" in api_name.lower():
            test_url = f"{base_url}/top-headlines?country=us&apiKey={api_key}"
        elif "gnews" in api_name.lower():
            test_url = f"{base_url}/top-headlines?country=us&token={api_key}"
        elif "bing" in api_name.lower():
            test_url = f"{base_url}/news/search?q=test&count=1"
        else:
            test_url = base_url + endpoint
        
        # Realizar petición de prueba
        start_time = time.time()
        response = requests.get(test_url, headers=headers, timeout=10)
        response_time = time.time() - start_time
        
        return {
            "status": "success",
            "response_code": response.status_code,
            "response_time": round(response_time, 3),
            "message": f"API {api_name} respondiendo correctamente"
        }
        
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "response_code": None,
            "response_time": None,
            "message": f"Timeout en {api_name} - La API no responde"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "response_code": None,
            "response_time": None,
            "message": f"Error de conexión a {api_name} - Verificar conectividad"
        }
    except Exception as e:
        return {
            "status": "error",
            "response_code": None,
            "response_time": None,
            "message": f"Error en {api_name}: {str(e)}"
        }

def main():
    st.set_page_config(
        page_title="Diagnóstico de APIs - VISION Premium",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 DIAGNÓSTICO DE APIS - VISION PREMIUM")
    st.markdown("### Verificación del Estado de las APIs de Noticias")
    
    # Configuración de APIs
    apis_config = {
        "NewsAPI": {
            "base_url": "https://newsapi.org/v2",
            "api_key": st.secrets.get("NEWS_API_KEY", "tu_api_key_aqui"),
            "description": "API principal de noticias internacionales"
        },
        "GNews": {
            "base_url": "https://gnews.io/api/v4",
            "api_key": st.secrets.get("GNEWS_API_KEY", "tu_api_key_aqui"),
            "description": "API de noticias con análisis de sentimientos"
        },
        "Bing News": {
            "base_url": "https://api.bing.microsoft.com/v7.0",
            "api_key": st.secrets.get("BING_API_KEY", "tu_api_key_aqui"),
            "description": "API de Microsoft para búsqueda de noticias"
        }
    }
    
    # Estado general del sistema
    st.markdown("---")
    st.subheader("📊 ESTADO GENERAL DEL SISTEMA")
    
    total_apis = len(apis_config)
    configured_apis = sum(1 for api in apis_config.values() if api["api_key"] != "tu_api_key_aqui")
    working_apis = 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total APIs", total_apis)
    
    with col2:
        st.metric("APIs Configuradas", configured_apis)
    
    with col3:
        st.metric("APIs Funcionando", working_apis)
    
    # Diagnóstico individual de cada API
    st.markdown("---")
    st.subheader("🔍 DIAGNÓSTICO INDIVIDUAL")
    
    for api_name, config in apis_config.items():
        with st.expander(f"🔧 {api_name}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Descripción:** {config['description']}")
                st.write(f"**Base URL:** `{config['base_url']}`")
                
                if config["api_key"] == "tu_api_key_aqui":
                    st.error("❌ API Key no configurada")
                    st.info("Para configurar esta API:")
                    st.write("1. Obtén tu API key del servicio correspondiente")
                    st.write("2. Agrega la key en `.streamlit/secrets.toml`")
                    st.write("3. Reinicia la aplicación")
                else:
                    st.success("✅ API Key configurada")
                    
                    # Botón para probar la API
                    if st.button(f"🧪 Probar {api_name}", key=f"test_{api_name}"):
                        with st.spinner(f"Probando {api_name}..."):
                            result = test_api_connection(
                                api_name, 
                                config["base_url"], 
                                config["api_key"]
                            )
                            
                            if result["status"] == "success":
                                st.success(f"✅ {result['message']}")
                                st.info(f"**Código de respuesta:** {result['response_code']}")
                                st.info(f"**Tiempo de respuesta:** {result['response_time']}s")
                                working_apis += 1
                            else:
                                st.error(f"❌ {result['message']}")
            
            with col2:
                # Estado visual
                if config["api_key"] == "tu_api_key_aqui":
                    st.error("🔴 NO CONFIGURADA")
                else:
                    st.success("🟢 CONFIGURADA")
    
    # Recomendaciones
    st.markdown("---")
    st.subheader("💡 RECOMENDACIONES")
    
    if configured_apis == 0:
        st.warning("⚠️ **No hay APIs configuradas**")
        st.write("El sistema funcionará en modo DEMO con noticias de ejemplo.")
        st.write("Para funcionalidad completa, configura al menos una API.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**NewsAPI**")
            st.write("1. Ve a [newsapi.org](https://newsapi.org/register)")
            st.write("2. Regístrate gratis")
            st.write("3. Obtén tu API key")
            
        with col2:
            st.markdown("**GNews**")
            st.write("1. Ve a [gnews.io](https://gnews.io/)")
            st.write("2. Crea una cuenta")
            st.write("3. Obtén tu API key")
            
        with col3:
            st.markdown("**Bing News**")
            st.write("1. Ve a [Microsoft](https://www.microsoft.com/en-us/bing/apis/bing-news-search-api)")
            st.write("2. Regístrate en Azure")
            st.write("3. Obtén tu API key")
    
    elif working_apis == 0:
        st.error("❌ **APIs configuradas pero no funcionando**")
        st.write("Verifica:")
        st.write("- Conectividad a internet")
        st.write("- Validez de las API keys")
        st.write("- Límites de uso de las APIs")
    
    else:
        st.success(f"✅ **{working_apis} de {total_apis} APIs funcionando**")
        st.write("El sistema está funcionando correctamente con APIs reales.")
    
    # Footer
    st.markdown("---")
    st.caption("Diagnóstico de APIs - VISION Premium")
    st.caption(f"Última verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()







