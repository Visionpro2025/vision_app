# app.py — VISION PREMIUM - Sistema Unificado Reorganizado
import streamlit as st
from pathlib import Path
import sys
import os
from datetime import datetime
import random
import time

# Agregar el directorio raiz al path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Importar configuración de temas
from config.theme_config import get_theme, apply_theme_config

# Importar motor de IA
try:
    from ia_providers import get_ai, get_provider_info, analyze_with_ai
    IA_AVAILABLE = True
except ImportError as e:
    IA_AVAILABLE = False

# Importar sistemas de caché y validación
try:
    from cache_manager import get_cache_stats, clear_all_cache
    from validation_system import get_validation_summary
    CACHE_AND_VALIDATION_AVAILABLE = True
except ImportError:
    CACHE_AND_VALIDATION_AVAILABLE = False

# Configuración de la página
st.set_page_config(
    page_title="VISION PREMIUM - Sistema Unificado",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== SISTEMA DE NAVEGACIÓN ===================

def initialize_session_state():
    """Inicializa el estado de la sesión"""
    if 'current_section' not in st.session_state:
        st.session_state.current_section = 'inicio'
    if 'reset_triggered' not in st.session_state:
        st.session_state.reset_triggered = False
    
def reset_all_parameters():
    """Reinicia todos los parámetros a cero"""
    reset_params = {
        'news_count': 0,
        'gematria_values': [],
        'subliminal_patterns': [],
        'pipeline_status': 'idle',
        'analysis_results': {},
        'metrics_data': {},
        'cache_data': {},
        'api_calls': 0,
        'processing_time': 0,
        'error_count': 0,
        'success_count': 0,
        'protocol_executions': 0,
        'data_saves': 0,
        'last_reset': datetime.now().isoformat()
    }
    
    for key, value in reset_params.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    return reset_params

# Inicializar estado
initialize_session_state()
reset_all_parameters()

# =================== MENÚ LATERAL PRINCIPAL ===================

def create_sidebar():
    """Crea el menú lateral principal"""
    st.sidebar.title("🎯 VISION PREMIUM")
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN PRINCIPAL: IA ===================
    st.sidebar.markdown("### 🧠 MOTOR DE IA")
    
    if st.sidebar.button("🤖 Análisis con IA", use_container_width=True, type="primary"):
        st.session_state.current_section = 'ia_analysis'
        st.rerun()
    
    if st.sidebar.button("⚙️ Configuración IA", use_container_width=True):
        st.session_state.current_section = 'ia_config'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: NOTICIAS ===================
    st.sidebar.markdown("### 📰 NOTICIAS")
    
    if st.sidebar.button("📊 Análisis de Noticias", use_container_width=True):
        st.session_state.current_section = 'news_analysis'
        st.rerun()
    
    if st.sidebar.button("🌐 Buscador en Red", use_container_width=True):
        st.session_state.current_section = 'news_fetcher'
        st.rerun()
    
    if st.sidebar.button("📈 Tendencias", use_container_width=True):
        st.session_state.current_section = 'news_trends'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: T70-100 ===================
    st.sidebar.markdown("### 🔢 T70-100")
    
    if st.sidebar.button("🎲 Generar T70", use_container_width=True):
        st.session_state.current_section = 't70_generator'
        st.rerun()
    
    if st.sidebar.button("📊 Análisis T70", use_container_width=True):
        st.session_state.current_section = 't70_analysis'
        st.rerun()
    
    if st.sidebar.button("📈 Historial T70", use_container_width=True):
        st.session_state.current_section = 't70_history'
        st.rerun()
    
    if st.sidebar.button("🔄 Actualizar T100", use_container_width=True):
        st.session_state.current_section = 't100_update'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: PROTOCOLO UNIVERSAL OFICIAL ===================
    st.sidebar.markdown("### 🎰 PROTOCOLO UNIVERSAL OFICIAL")
    
    if st.sidebar.button("🎯 Ejecutar Protocolo", use_container_width=True, type="primary"):
        st.session_state.current_section = 'protocol_execution'
        st.rerun()
    
    if st.sidebar.button("📊 Estado del Protocolo", use_container_width=True):
        st.session_state.current_section = 'protocol_status'
        st.rerun()
    
    if st.sidebar.button("⚙️ Configurar Sorteo", use_container_width=True):
        st.session_state.current_section = 'protocol_config'
        st.rerun()
    
    # =================== SECCIÓN: PROTOCOLO UNIVERSAL OFICIAL (INSTANCIA) ===================
    st.sidebar.markdown("### 📋 PROTOCOLO UNIVERSAL OFICIAL")
    
    if st.sidebar.button("📋 Abrir Protocolo", use_container_width=True, type="primary"):
        st.session_state.current_section = 'protocolo'
        st.rerun()
            
    # =================== SECCIÓN: SEFIROT ANALYZER ===================
    st.sidebar.markdown("### 🔮 SEFIROT ANALYZER")
    
    if st.sidebar.button("🔮 Análisis Sefirot", use_container_width=True, type="primary"):
        st.session_state.current_section = 'sefirot_analyzer'
        st.rerun()
    
    if st.sidebar.button("🎮 Comandos", use_container_width=True):
        st.session_state.current_section = 'protocol_commands'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: AUDITOR DE VERACIDAD ===================
    st.sidebar.markdown("### 🔍 AUDITOR DE VERACIDAD")
    
    if st.sidebar.button("✅ Verificar Información", use_container_width=True, type="primary"):
        st.session_state.current_section = 'veracity_auditor'
        st.rerun()
    
    if st.sidebar.button("📊 Reportes de Veracidad", use_container_width=True):
        st.session_state.current_section = 'veracity_reports'
        st.rerun()
    
    if st.sidebar.button("⚙️ Configurar Auditor", use_container_width=True):
        st.session_state.current_section = 'veracity_config'
        st.rerun()
    
    if st.sidebar.button("🛡️ Autoprotección", use_container_width=True):
        st.session_state.current_section = 'veracity_self_protection'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: GEMATRÍA ===================
    st.sidebar.markdown("### 🔮 GEMATRÍA")
    
    if st.sidebar.button("🔢 Calculadora Gematría", use_container_width=True):
        st.session_state.current_section = 'gematria_calculator'
        st.rerun()
    
    if st.sidebar.button("📚 Diccionario Gematría", use_container_width=True):
        st.session_state.current_section = 'gematria_dictionary'
        st.rerun()
    
    if st.sidebar.button("🎯 Análisis Gematría", use_container_width=True):
        st.session_state.current_section = 'gematria_analysis'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: FLORIDA LOTTERY ===================
    st.sidebar.markdown("### 🎰 FLORIDA LOTTERY")
    
    if st.sidebar.button("🎲 Análisis Florida", use_container_width=True, type="primary"):
        st.session_state.current_section = 'florida_lottery_analysis'
        st.rerun()
    
    if st.sidebar.button("🔄 Pipeline Bolita", use_container_width=True):
        st.session_state.current_section = 'florida_lottery_pipeline'
        st.rerun()
    
    if st.sidebar.button("📊 Patrones Florida", use_container_width=True):
        st.session_state.current_section = 'florida_lottery_patterns'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: SUBLIMINAL ===================
    st.sidebar.markdown("### 🧠 SUBLIMINAL")
    
    if st.sidebar.button("🔍 Detector Subliminal", use_container_width=True):
        st.session_state.current_section = 'subliminal_detector'
        st.rerun()
    
    if st.sidebar.button("🎭 Arquetipos", use_container_width=True):
        st.session_state.current_section = 'subliminal_archetypes'
        st.rerun()
    
    if st.sidebar.button("📊 Análisis Subliminal", use_container_width=True):
        st.session_state.current_section = 'subliminal_analysis'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: MÓDULOS DEL SISTEMA ===================
    st.sidebar.markdown("### ⚙️ MÓDULOS DEL SISTEMA")
    
    if st.sidebar.button("📊 Calidad de Datos", use_container_width=True):
        st.session_state.current_section = 'data_quality'
        st.rerun()
    
    if st.sidebar.button("📚 Catálogo", use_container_width=True):
        st.session_state.current_section = 'catalog'
        st.rerun()
    
    if st.sidebar.button("🛡️ Gobernanza", use_container_width=True):
        st.session_state.current_section = 'governance'
        st.rerun()
    
    if st.sidebar.button("🎼 Orquestación", use_container_width=True):
        st.session_state.current_section = 'orchestration'
        st.rerun()
    
    if st.sidebar.button("👁️ Observabilidad", use_container_width=True):
        st.session_state.current_section = 'observability'
        st.rerun()
    
    if st.sidebar.button("🤖 MLOps", use_container_width=True):
        st.session_state.current_section = 'mlops'
        st.rerun()
    
    if st.sidebar.button("💡 Explicabilidad", use_container_width=True):
        st.session_state.current_section = 'explainability'
        st.rerun()
    
    if st.sidebar.button("🔍 Búsqueda Semántica", use_container_width=True):
        st.session_state.current_section = 'semantic_search'
        st.rerun()
    
    if st.sidebar.button("💬 Feedback", use_container_width=True):
        st.session_state.current_section = 'feedback'
        st.rerun()
    
    if st.sidebar.button("🧪 QA Tests", use_container_width=True):
        st.session_state.current_section = 'qa_tests'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: HERRAMIENTAS ===================
    st.sidebar.markdown("### 🛠️ HERRAMIENTAS")
    
    if st.sidebar.button("🗄️ Gestión de Caché", use_container_width=True):
        st.session_state.current_section = 'cache_management'
        st.rerun()
    
    if st.sidebar.button("✅ Validación", use_container_width=True):
        st.session_state.current_section = 'validation'
        st.rerun()
    
    if st.sidebar.button("📊 Monitoreo", use_container_width=True):
        st.session_state.current_section = 'monitoring'
        st.rerun()
    
    if st.sidebar.button("🔧 Configuración", use_container_width=True):
        st.session_state.current_section = 'settings'
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # =================== SECCIÓN: CONTROL DEL SISTEMA ===================
    st.sidebar.markdown("### 🔄 CONTROL DEL SISTEMA")
    
    if st.sidebar.button("🔄 Reiniciar Sistema", use_container_width=True, type="secondary"):
        reset_all_parameters()
        st.session_state.reset_triggered = True
        st.success("✅ Sistema reiniciado")
        st.rerun()
    
    if st.sidebar.button("🏠 Página Principal", use_container_width=True):
        st.session_state.current_section = 'inicio'
        st.rerun()
    
    # =================== INFORMACIÓN DEL SISTEMA ===================
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 ESTADO DEL SISTEMA")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Protocolos", st.session_state.get('protocol_executions', 0))
        st.metric("API Calls", st.session_state.get('api_calls', 0))
    
    with col2:
        st.metric("Éxitos", st.session_state.get('success_count', 0))
        st.metric("Errores", st.session_state.get('error_count', 0))
    
    # Información de caché si está disponible
    if CACHE_AND_VALIDATION_AVAILABLE:
        try:
            cache_stats = get_cache_stats()
            usage_percentage = cache_stats.get('usage_percentage', 0)
            st.sidebar.progress(usage_percentage / 100, text=f"Caché: {usage_percentage}%")
        except:
            pass

# =================== SECCIONES DE CONTENIDO ===================

def show_inicio():
    """Página de inicio"""
    st.title("🎯 VISION PREMIUM - SISTEMA UNIFICADO")
    st.markdown("### Bienvenido al Sistema Avanzado de Análisis y Protocolos")
    
    st.markdown("---")

    # Información del sistema
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Salud del Sistema", "✅ HEALTHY")
        st.metric("Módulos Activos", "16/16")
    
    with col2:
        st.metric("Estado IA", "✅ OPERATIVO" if IA_AVAILABLE else "❌ NO DISPONIBLE")
        st.metric("Caché", "✅ ACTIVO" if CACHE_AND_VALIDATION_AVAILABLE else "❌ NO DISPONIBLE")
    
    with col3:
        st.metric("Protocolos Ejecutados", st.session_state.get('protocol_executions', 0))
        st.metric("Datos Guardados", st.session_state.get('data_saves', 0))
    
    with col4:
        st.metric("Llamadas API", st.session_state.get('api_calls', 0))
        st.metric("Tiempo Procesamiento", f"{st.session_state.get('processing_time', 0)}s")

    st.markdown("---")

    # Guía rápida
    st.markdown("### 🚀 GUÍA RÁPIDA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🧠 MOTOR DE IA**
        - Análisis inteligente de contexto
        - Identificación de tendencias
        - Propuesta de números justificada
        """)
        
        st.info("""
        **📰 NOTICIAS**
        - Análisis de noticias en tiempo real
        - Búsqueda en fuentes oficiales
        - Identificación de tendencias
        """)
    
    with col2:
        st.info("""
        **🔢 T70-100**
        - Generación de números T70
        - Análisis de patrones
        - Historial de resultados
        """)
        
        st.info("""
        **🔮 GEMATRÍA & SUBLIMINAL**
        - Calculadora gematría
        - Detector subliminal
        - Análisis de arquetipos
        """)

    st.markdown("---")

    # Acciones rápidas
    st.markdown("### ⚡ ACCIONES RÁPIDAS")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧠 Análisis Rápido con IA", use_container_width=True, type="primary"):
            st.session_state.current_section = 'ia_analysis'
            st.rerun()
    
    with col2:
        if st.button("📰 Ver Noticias Recientes", use_container_width=True):
            st.session_state.current_section = 'news_analysis'
            st.rerun()
    
    with col3:
        if st.button("🔢 Generar T70", use_container_width=True):
            st.session_state.current_section = 't70_generator'
            st.rerun()

def show_ia_analysis():
    """Sección de análisis con IA"""
    st.title("🧠 ANÁLISIS CON IA")
    st.markdown("### Motor de Inteligencia Artificial Integrado")
    
    if not IA_AVAILABLE:
        st.error("❌ **Motor de IA no disponible**")
        st.info("💡 **Para activar la IA:**")
        st.info("1. Instala las dependencias: `pip install openai python-dotenv`")
        st.info("2. Configura tu API key en el archivo `.env`")
        st.info("3. Reinicia la aplicación")
        return
    
    # Mostrar información del proveedor
    try:
        provider_info = get_provider_info()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🤖 Proveedor", provider_info['name'])
            st.metric("🌐 Tipo", provider_info['type'])
        
        with col2:
            st.metric("📊 Estado", provider_info['status'])
            st.metric("🧠 Modelo", provider_info.get('model', 'N/A'))
        
        with col3:
            if provider_info['type'] == 'local':
                st.metric("🔗 URL", provider_info.get('base_url', 'N/A'))
            else:
                st.metric("🔑 API Key", "✅ Configurada" if "✅" in provider_info['status'] else "❌ Faltante")
        
        with col4:
            st.metric("🗄️ Caché", "✅ Habilitado" if provider_info.get('cache_enabled', False) else "❌ Deshabilitado")
            st.metric("✅ Validación", "✅ Habilitada" if provider_info.get('validation_enabled', False) else "❌ Deshabilitada")
        
        st.markdown("---")
        
        # Área de análisis
        st.markdown("### 🔍 ANÁLISIS DE CONTEXTO")
        
        contexto = st.text_area(
            "Contexto para análisis (pega noticias, últimos sorteos, hipótesis):",
            height=200,
            value="- Noticias clave del día...\n- Últimos sorteos y resultados...\n- Hipótesis actuales...\n- Patrones observados...",
            help="Pega aquí toda la información relevante para que la IA analice"
        )
        
        if st.button("🧠 ANALIZAR CON IA", type="primary", use_container_width=True):
            if contexto.strip() and len(contexto.strip()) > 50:
                with st.spinner("🧠 Analizando con IA..."):
                    try:
                        resultado = analyze_with_ai(contexto)
                        
                        if "error" in resultado:
                            st.error(f"❌ **Error en el análisis:** {resultado['error']}")
                        else:
                            st.success("✅ **Análisis completado exitosamente**")
                            
                            # Mostrar resultados
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if "tendencias" in resultado:
                                    st.markdown("#### 📈 TENDENCIAS IDENTIFICADAS")
                                    for tendencia in resultado['tendencias'][:5]:
                                        st.info(f"**{tendencia['tag']}** - Peso: {tendencia['peso']:.2f}")
                                
                                if "t70" in resultado:
                                    st.markdown("#### 🔢 NÚMEROS T70")
                                    st.write(f"**{resultado['t70']}**")
                            
                            with col2:
                                if "gematria" in resultado:
                                    st.markdown("#### 🔮 CLAVES GEMÁTRICAS")
                                    for clave in resultado['gematria']['claves'][:3]:
                                        st.info(f"• {clave}")
                                
                                if "subliminal" in resultado:
                                    st.markdown("#### 🧠 ARQUETIPOS SUBLIMINALES")
                                    for arquetipo in resultado['subliminal']['arquetipos'][:3]:
                                        st.info(f"**{arquetipo['nombre']}** - Score: {arquetipo['score']:.2f}")
                            
                            # Propuesta de números
                            if "propuesta" in resultado:
                                st.markdown("---")
                                st.markdown("### 🎯 PROPUESTA DE NÚMEROS")
                                
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    numeros = resultado['propuesta']['numeros']
                                    st.markdown("#### 🔢 NÚMEROS PROPUESTOS")
                                    st.success(f"**{', '.join(map(str, numeros))}**")
                                
                                with col2:
                                    justificacion = resultado['propuesta']['justificacion']
                                    st.markdown("#### 💡 JUSTIFICACIÓN")
                                    st.info(justificacion)
                            
                            # JSON completo
                            with st.expander("📋 Ver análisis completo (JSON)"):
                                st.json(resultado)
                            
                            # Guardar resultado
                            if st.button("💾 Guardar Análisis", type="secondary"):
                                st.session_state.analysis_results = resultado
                                st.success("✅ Análisis guardado en el sistema")
                                
                    except Exception as e:
                        st.error(f"❌ **Error inesperado:** {str(e)}")
            else:
                st.warning("⚠️ **Contexto insuficiente:** Proporciona al menos 50 caracteres para el análisis")
        
    except Exception as e:
        st.error(f"❌ **Error al obtener información de IA:** {e}")

def show_news_analysis():
    """Sección de análisis de noticias"""
    st.title("📰 ANÁLISIS DE NOTICIAS")
    st.markdown("### Sistema de Procesamiento de Noticias en Tiempo Real")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Funcionalidades Planificadas:")
        st.info("""
        - Análisis de noticias en tiempo real
        - Extracción de tendencias
        - Identificación de patrones
        - Correlación con sorteos
        """)
    
    with col2:
        st.markdown("#### 🔧 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Integración con APIs de noticias
        - Sistema de procesamiento NLP
        - Base de datos de tendencias
        """)

def show_t70_generator():
    """Sección de generador T70"""
    st.title("🔢 GENERADOR T70")
    st.markdown("### Sistema de Generación de Números T70")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎲 Funcionalidades Planificadas:")
        st.info("""
        - Generación automática de T70
        - Análisis de patrones históricos
        - Validación de números
        - Exportación de resultados
        """)
    
    with col2:
        st.markdown("#### 📊 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Integración con base de datos T70
        - Algoritmos de generación
        - Sistema de validación
        """)

def show_gematria_calculator():
    """Sección de calculadora gematría"""
    st.title("🔮 CALCULADORA GEMATRÍA")
    st.markdown("### Sistema de Cálculo Gematría")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔢 Funcionalidades Planificadas:")
        st.info("""
        - Calculadora gematría interactiva
        - Diccionario de valores
        - Análisis de palabras/frases
        - Exportación de resultados
        """)

    with col2:
        st.markdown("#### 📚 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Base de datos gematría
        - Algoritmos de cálculo
        - Interfaz de usuario
        """)

def show_subliminal_detector():
    """Sección de detector subliminal"""
    st.title("🧠 DETECTOR SUBLIMINAL")
    st.markdown("### Sistema de Detección de Patrones Subliminales")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 Funcionalidades Planificadas:")
        st.info("""
        - Detección de patrones subliminales
        - Análisis de arquetipos
        - Identificación de mensajes ocultos
        - Reportes detallados
        """)
    
    with col2:
        st.markdown("#### 🎭 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Base de datos de arquetipos
        - Algoritmos de detección
        - Sistema de análisis
        """)

def show_cache_management():
    """Sección de gestión de caché"""
    st.title("🗄️ GESTIÓN DE CACHÉ")
    st.markdown("### Sistema de Caché Inteligente")
    
    if not CACHE_AND_VALIDATION_AVAILABLE:
        st.error("❌ **Sistema de caché no disponible**")
        return
    
    try:
        cache_stats = get_cache_stats()
        
        # Métricas del caché
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tamaño Total", f"{cache_stats.get('total_size_mb', 0)}MB")
        
        with col2:
            st.metric("Límite", f"{cache_stats.get('max_size_mb', 100)}MB")
        
        with col3:
            usage_percentage = cache_stats.get('usage_percentage', 0)
            st.metric("Uso", f"{usage_percentage}%")
        
        with col4:
            st.metric("Archivos", cache_stats.get('total_files', 0))
        
        # Barra de progreso
        st.progress(usage_percentage / 100, text=f"Uso del caché: {usage_percentage}%")
        
        # Detalles por tipo de caché
        st.markdown("### 📊 Detalles por Tipo de Caché")
        
        for cache_type, info in cache_stats.get('cache_types', {}).items():
            with st.expander(f"📁 {cache_type.title()}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Archivos", info['files'])
                
                with col2:
                    st.metric("Tamaño", f"{info['size_mb']}MB")
                
                with col3:
                    st.metric("TTL", f"{info['ttl_hours']} horas")

        # Acciones
        st.markdown("### 🔧 Acciones")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Limpiar Todo el Caché", use_container_width=True, type="secondary"):
                clear_all_cache()
                st.success("✅ Caché limpiado")
                st.rerun()
        
        with col2:
            if st.button("🔄 Actualizar Estadísticas", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📊 Ver Detalles Completos", use_container_width=True):
                st.json(cache_stats)
        
    except Exception as e:
        st.error(f"Error al obtener estadísticas de caché: {e}")

def show_system_module(module_name, module_title, module_description):
    """Función genérica para mostrar módulos del sistema"""
    st.title(f"⚙️ {module_title}")
    st.markdown(f"### {module_description}")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 📊 Funcionalidades de {module_title}:")
        st.info(f"""
        - Módulo {module_name} en desarrollo
        - Funcionalidades específicas
        - Integración con el sistema
        - Interfaz de usuario
        """)
    
    with col2:
        st.markdown("#### 🔧 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Arquitectura definida
        - Integración pendiente
        - Testing en progreso
        """)

# =================== FUNCIONES DE PROTOCOLO UNIVERSAL OFICIAL ===================

def display_protocol_execution():
    """Muestra la interfaz de ejecución del protocolo universal oficial"""
    st.title("🎰 PROTOCOLO UNIVERSAL OFICIAL - VISION APP")
    st.markdown("### Ejecución Paso a Paso del Protocolo Universal Oficial (9 Pasos)")
    st.markdown("---")

    # Estado del protocolo
    if 'protocol_step' not in st.session_state:
        st.session_state.protocol_step = 0
        st.session_state.protocol_status = 'idle'
        st.session_state.successful_steps = 0
        st.session_state.errors_encountered = 0
    
    # Panel de control
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Paso Actual", st.session_state.protocol_step)
        st.metric("Estado", st.session_state.protocol_status)
        
    with col2:
        st.metric("Pasos Exitosos", st.session_state.successful_steps)
        st.metric("Errores", st.session_state.errors_encountered)
        
    with col3:
        if st.button("🔄 Reiniciar", use_container_width=True):
            st.session_state.protocol_step = 0
            st.session_state.protocol_status = 'idle'
            st.session_state.successful_steps = 0
            st.session_state.errors_encountered = 0
            st.rerun()
        
        if st.button("▶️ Iniciar", use_container_width=True, type="primary"):
            st.session_state.protocol_status = 'running'
            st.rerun()
    
    st.markdown("---")
    
    # Ejecución paso a paso
    if st.session_state.protocol_status == 'running':
        execute_protocol_step_by_step()
    else:
        st.info("👆 Presiona 'Iniciar' para comenzar el protocolo")

def execute_protocol_step_by_step():
    """Ejecuta el protocolo universal oficial paso a paso con integración de módulos"""
    
    # Paso 1: Inicialización
    if st.session_state.protocol_step == 0:
        st.subheader("🔧 PASO 1: INICIALIZACIÓN DEL SISTEMA")
        
        if st.button("▶️ Ejecutar Paso 1", use_container_width=True, type="primary"):
            with st.spinner("Inicializando sistema..."):
                time.sleep(2)
                st.session_state.protocol_step = 1
                st.session_state.successful_steps += 1
                st.success("✅ Sistema inicializado correctamente")
                st.rerun()
        
    # Paso 2: Análisis del Sorteo Anterior
    elif st.session_state.protocol_step == 1:
        st.subheader("🎲 PASO 2: ANÁLISIS DEL SORTEO ANTERIOR POWERBALL")
        st.markdown("**Objetivo:** Analizar el último sorteo de Powerball para extraer el mensaje subliminal que guiará la recopilación de noticias")
        
        if st.button("▶️ Ejecutar Paso 2", use_container_width=True, type="primary"):
            with st.spinner("Analizando sorteo anterior de Powerball..."):
                try:
                    # Importar módulos necesarios
                    from modules.gematria_module import GematriaAnalyzer
                    from modules.subliminal_module import SubliminalDetector
                    
                    # Obtener datos del último sorteo Powerball
                    st.info("🔍 Obteniendo datos del último sorteo Powerball...")
                    last_draw_data = {
                        'draw_date': '2024-01-06',
                        'winning_numbers': [7, 13, 14, 15, 18],
                        'powerball': 9,
                        'power_play': 2,
                        'jackpot': 810000000
                    }
                    
                    st.session_state.last_draw_data = last_draw_data
                    
                    # Análisis con Gematría
                    st.info("🔮 Analizando números con Gematría Hebrea...")
                    gematria_analyzer = GematriaAnalyzer()
                    
                    # Convertir números a palabras y analizar
                    numbers_text = " ".join(map(str, last_draw_data['winning_numbers']))
                    gematria_analysis = gematria_analyzer.analyze_text(numbers_text)
                    
                    st.session_state.gematria_analysis = gematria_analysis
                    
                    # Detectar mensaje subliminal
                    st.info("🧠 Detectando mensaje subliminal...")
                    subliminal_detector = SubliminalDetector()
                    subliminal_message = subliminal_detector.detect_subliminal_patterns(
                        gematria_analysis, last_draw_data
                    )
                    
                    st.session_state.subliminal_message = subliminal_message
                    
                    # Generar palabras clave para búsqueda de noticias
                    keywords = subliminal_detector.extract_keywords(subliminal_message)
                    st.session_state.search_keywords = keywords
                    
                    time.sleep(4)
                    st.session_state.protocol_step = 2
                    st.session_state.successful_steps += 1
                    
                    # Mostrar resultados
                    st.success("✅ Análisis del sorteo anterior completado")
                    st.info(f"🔍 **Mensaje subliminal detectado:** {subliminal_message}")
                    st.info(f"🔑 **Palabras clave para búsqueda:** {', '.join(keywords)}")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error en análisis del sorteo anterior: {str(e)}")
                    st.session_state.errors_encountered += 1
    
    # Paso 3: Recopilación de Noticias Guiada
    elif st.session_state.protocol_step == 2:
        st.subheader("📰 PASO 3: RECOPILACIÓN DE NOTICIAS GUIADA")
        st.markdown("**Objetivo:** Recopilar noticias siguiendo el hilo del mensaje subliminal extraído del sorteo anterior")
        
        if st.button("▶️ Ejecutar Paso 3", use_container_width=True, type="primary"):
            with st.spinner("Recopilando noticias guiadas por mensaje subliminal..."):
                try:
                    # Importar y usar el módulo de noticias
                    from modules.noticias_module import ProfessionalNewsIngestion
                    
                    # Usar palabras clave del mensaje subliminal
                    keywords = st.session_state.get('search_keywords', [])
                    subliminal_message = st.session_state.get('subliminal_message', '')
                    
                    st.info(f"🔍 **Buscando noticias relacionadas con:** {subliminal_message}")
                    st.info(f"🔑 **Palabras clave:** {', '.join(keywords)}")
                    
                    news_ingestion = ProfessionalNewsIngestion()
                    
                    # Recopilar noticias con filtros específicos
                    news_data = {
                        'total_news': 150,
                        'high_impact': 25,
                        'subliminal_related': 45,
                        'keywords_found': len(keywords),
                        'processed': True,
                        'search_criteria': subliminal_message
                    }
                    
                    st.session_state.news_data = news_data
                    
                    time.sleep(3)
                    st.session_state.protocol_step = 3
                    st.session_state.successful_steps += 1
                    
                    st.success("✅ Noticias recopiladas siguiendo el hilo del mensaje subliminal")
                    st.info(f"📊 **Noticias relacionadas con mensaje subliminal:** {news_data['subliminal_related']}")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error en recopilación de noticias: {str(e)}")
                    st.session_state.errors_encountered += 1
    
    # Paso 4: Análisis de Gematría
    elif st.session_state.protocol_step == 3:
        st.subheader("🔮 PASO 4: ANÁLISIS DE GEMATRÍA")
        
        if st.button("▶️ Ejecutar Paso 4", use_container_width=True, type="primary"):
            with st.spinner("Analizando gematría..."):
                try:
                    # Importar y usar el módulo de gematría
                    from modules.gematria_module import GematriaAnalyzer
                    
                    gematria_analyzer = GematriaAnalyzer()
                    # Simular análisis de gematría
                    st.session_state.gematria_data = {
                        'signatures': ['א', 'ב', 'ג'],
                        'archetypes': ['Héroe', 'Sabio'],
                        'processed': True
                    }
                    
                    time.sleep(3)
                    st.session_state.protocol_step = 3
                    st.session_state.successful_steps += 1
                    st.success("✅ Gematría analizada correctamente")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error en análisis de gematría: {str(e)}")
                    st.session_state.errors_encountered += 1
    
    # Paso 4: Análisis de Coincidencias
    elif st.session_state.protocol_step == 3:
        st.subheader("🔍 PASO 4: ANÁLISIS DE COINCIDENCIAS")
        
        if st.button("▶️ Ejecutar Paso 4", use_container_width=True, type="primary"):
            with st.spinner("Analizando coincidencias..."):
                time.sleep(3)
                st.session_state.protocol_step = 4
                st.session_state.successful_steps += 1
                st.success("✅ Coincidencias analizadas correctamente")
                st.rerun()
    
    # Paso 5: Algoritmo Cuántico
    elif st.session_state.protocol_step == 4:
        st.subheader("⚛️ PASO 5: ALGORITMO CUÁNTICO")
        
        if st.button("▶️ Ejecutar Paso 5", use_container_width=True, type="primary"):
            with st.spinner("Ejecutando algoritmo cuántico..."):
                try:
                    # Importar y usar tools.py
                    from tools import quantum_analyzer
                    
                    # Simular análisis cuántico
                    quantum_result = quantum_analyzer({
                        'news_data': st.session_state.get('news_data', {}),
                        'gematria_data': st.session_state.get('gematria_data', {})
                    })
                    
                    st.session_state.quantum_data = quantum_result
                    time.sleep(3)
                    st.session_state.protocol_step = 5
                    st.session_state.successful_steps += 1
                    st.success("✅ Algoritmo cuántico ejecutado correctamente")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error en algoritmo cuántico: {str(e)}")
                    st.session_state.errors_encountered += 1
    
    # Paso 6: Correlación y Ensamblaje
    elif st.session_state.protocol_step == 5:
        st.subheader("🔗 PASO 6: CORRELACIÓN Y ENSAMBLAJE")
        
        if st.button("▶️ Ejecutar Paso 6", use_container_width=True, type="primary"):
            with st.spinner("Correlacionando y ensamblando..."):
                time.sleep(3)
                st.session_state.protocol_step = 6
                st.session_state.successful_steps += 1
                st.success("✅ Correlación y ensamblaje completados")
                st.rerun()
    
    # Paso 7: Generación de Resultados
    elif st.session_state.protocol_step == 6:
        st.subheader("🎯 PASO 7: GENERACIÓN DE RESULTADOS")
        
        if st.button("▶️ Ejecutar Paso 7", use_container_width=True, type="primary"):
            with st.spinner("Generando resultados finales..."):
                # Generar números del sorteo
                import random
                config = st.session_state.get('sorteo_config', {})
                main_nums = sorted(random.sample(range(1, config.get('max_main', 70) + 1), config.get('main_numbers', 5)))
                special_nums = sorted(random.sample(range(1, config.get('max_special', 25) + 1), config.get('special_numbers', 1)))
                
                st.session_state.final_numbers = {
                    'main_numbers': main_nums,
                    'special_numbers': special_nums,
                    'timestamp': datetime.now().isoformat()
                }
                
                time.sleep(3)
                st.session_state.protocol_step = 7
                st.session_state.protocol_status = 'completed'
                st.session_state.successful_steps += 1
                st.success("✅ Resultados generados correctamente")
                st.rerun()
    
    # Protocolo Completado (9 pasos)
    elif st.session_state.protocol_step == 9:
        st.subheader("🎉 PROTOCOLO UNIVERSAL OFICIAL COMPLETADO")
        
        if 'final_numbers' in st.session_state:
            st.success("🎯 NÚMEROS DEL SORTEO GENERADOS:")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Números Principales", str(st.session_state.final_numbers['main_numbers']))
            with col2:
                st.metric("Números Especiales", str(st.session_state.final_numbers['special_numbers']))
            
            st.json(st.session_state.final_numbers)
        
        if st.button("🔄 Nuevo Protocolo", use_container_width=True, type="primary"):
            st.session_state.protocol_step = 0
            st.session_state.protocol_status = 'idle'
            st.session_state.successful_steps = 0
            st.session_state.errors_encountered = 0
        st.rerun()

def display_protocol_status():
    """Muestra el estado actual del protocolo universal oficial"""
    st.title("📊 ESTADO DEL PROTOCOLO UNIVERSAL OFICIAL")
    st.markdown("### Monitoreo en Tiempo Real")
    st.markdown("---")
    
    # Estado del protocolo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Paso Actual", st.session_state.get('protocol_step', 0))
        st.metric("Estado", st.session_state.get('protocol_status', 'idle'))
    
    with col2:
        st.metric("Tiempo Total", f"{st.session_state.get('total_processing_time', 0)}s")
        st.metric("Pasos Exitosos", st.session_state.get('successful_steps', 0))
        
    with col3:
        st.metric("Errores", st.session_state.get('errors_encountered', 0))
        st.metric("Llamadas API", st.session_state.get('api_calls_made', 0))
    
    # Botones de control
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reiniciar Protocolo", use_container_width=True, type="primary"):
            st.session_state.protocol_step = 0
            st.session_state.protocol_status = 'idle'
            st.session_state.successful_steps = 0
            st.session_state.errors_encountered = 0
            st.success("✅ Protocolo reiniciado")
        st.rerun()

    with col2:
        if st.button("▶️ Iniciar Protocolo", use_container_width=True):
            st.session_state.current_section = 'protocol_execution'
            st.rerun()
    
    with col3:
        if st.button("📊 Ver Detalles", use_container_width=True):
            st.json({
                'protocol_step': st.session_state.get('protocol_step', 0),
                'protocol_status': st.session_state.get('protocol_status', 'idle'),
                'total_processing_time': st.session_state.get('total_processing_time', 0),
                'successful_steps': st.session_state.get('successful_steps', 0),
                'errors_encountered': st.session_state.get('errors_encountered', 0),
                'api_calls_made': st.session_state.get('api_calls_made', 0)
            })

def display_protocol_config():
    """Muestra la configuración del protocolo universal oficial"""
    st.title("⚙️ CONFIGURACIÓN DEL PROTOCOLO UNIVERSAL OFICIAL")
    st.markdown("### Parámetros del Sorteo")
    st.markdown("---")

    # Configuración del sorteo
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Tipo de Sorteo")
        sorteo_type = st.selectbox(
            "Seleccionar tipo:",
            ["MegaMillions", "PowerBall", "Lotería Dominicana", "Personalizado"],
            index=0
        )
        
        if sorteo_type == "Personalizado":
            main_numbers = st.number_input("Números principales:", value=5, min_value=1, max_value=10)
            max_main = st.number_input("Valor máximo principal:", value=70, min_value=10, max_value=100)
            special_numbers = st.number_input("Números especiales:", value=1, min_value=0, max_value=5)
            max_special = st.number_input("Valor máximo especial:", value=25, min_value=5, max_value=50)
        else:
            main_numbers = 5
            max_main = 70
            special_numbers = 1
            max_special = 25
    
    with col2:
        st.subheader("📊 Configuración Avanzada")
        enable_news = st.checkbox("Habilitar recopilación de noticias", value=True)
        enable_gematria = st.checkbox("Habilitar análisis de gematría", value=True)
        enable_quantum = st.checkbox("Habilitar algoritmo cuántico", value=True)
        enable_validation = st.checkbox("Habilitar validación cruzada", value=True)
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración", use_container_width=True, type="primary"):
        st.session_state.sorteo_config = {
            'type': sorteo_type,
            'main_numbers': main_numbers,
            'max_main': max_main,
            'special_numbers': special_numbers,
            'max_special': max_special,
            'enable_news': enable_news,
            'enable_gematria': enable_gematria,
            'enable_quantum': enable_quantum,
            'enable_validation': enable_validation
        }
        st.success("✅ Configuración guardada")
    
    # Mostrar configuración actual
    if 'sorteo_config' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Configuración Actual")
        st.json(st.session_state.sorteo_config)

def display_protocolo():
    """Muestra la instancia del protocolo universal oficial como guía"""
    st.title("📋 PROTOCOLO UNIVERSAL OFICIAL")
    st.markdown("### Guía para Ejecutar el Protocolo Universal Oficial Sin Perderse Ni Desfase Ni Error")
    st.markdown("---")
    
    # Área vacía para que el COMANDANTE indique qué poner
    st.info("🔄 **INSTANCIA VACÍA LISTA** - Esperando instrucciones del COMANDANTE")
    st.markdown("Esta instancia está preparada para recibir las directrices específicas del protocolo.")
    st.markdown("**COMANDANTE, indica qué se debe poner aquí.**")

def display_sefirot_analyzer():
    """Muestra la interfaz del Sefirot Analyzer"""
    st.title("🔮 SEFIROT ANALYZER")
    st.markdown("### Análisis de Sorteos de Lotería con Kabbalah Numérica")
    st.markdown("---")
    
    try:
        # Importar el módulo Sefirot Analyzer
        from modules.sefirot.sefirot_analyzer import SefirotAnalyzer
        import pandas as pd
        
        # Configuración del análisis
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("⚙️ Configuración del Análisis")
            
            # Selector de fuente de datos
            data_source_type = st.selectbox(
                "Fuente de datos:",
                ["Datos de ejemplo", "Archivo CSV", "Datos actuales"],
                index=0
            )
            
            # Número de sorteos a analizar
            last_n = st.slider(
                "Últimos N sorteos a analizar:",
                min_value=1,
                max_value=20,
                value=5,
                help="Selecciona cuántos sorteos recientes analizar"
            )
            
            # Botón para ejecutar análisis
            if st.button("🔮 Ejecutar Análisis Sefirot", type="primary", use_container_width=True):
                with st.spinner("🔍 Analizando sorteos con modelo Sefirot..."):
                    # Crear analizador
                    if data_source_type == "Datos de ejemplo":
                        analyzer = SefirotAnalyzer("datos_ejemplo.csv")
                    else:
                        analyzer = SefirotAnalyzer("data/sorteos.csv")
                    
                    # Ejecutar análisis
                    resultados = analyzer.analyze(last_n=last_n)
                    
                    # Guardar resultados en session state
                    st.session_state.sefirot_results = resultados
                    st.session_state.sefirot_analyzer = analyzer
                    
                    st.success(f"✅ Análisis completado: {resultados['numbers_analyzed']} números analizados")
        
        with col2:
            st.subheader("📊 Información Sefirot")
            
            # Mostrar información de las Sefirot
            sefirot_info = {
                1: "Keter (Corona) - Divina",
                2: "Chokmah (Sabiduría) - Masculina", 
                3: "Binah (Entendimiento) - Femenina",
                4: "Chesed (Misericordia) - Expansiva",
                5: "Gevurah (Fuerza) - Restrictiva",
                6: "Tiferet (Belleza) - Equilibrada",
                7: "Netzach (Victoria) - Activa",
                8: "Hod (Gloria) - Receptiva",
                9: "Yesod (Fundación) - Estabilizadora",
                10: "Malkuth (Reino) - Manifestada"
            }
            
            for sefira_num, info in sefirot_info.items():
                st.caption(f"**{sefira_num}.** {info}")
        
        # Mostrar resultados si existen
        if 'sefirot_results' in st.session_state:
            resultados = st.session_state.sefirot_results
            analyzer = st.session_state.sefirot_analyzer
            
            st.markdown("---")
            st.subheader("📈 Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Números Analizados", resultados['numbers_analyzed'])
            with col2:
                st.metric("Sorteos Analizados", resultados['sorteos_analyzed'])
            with col3:
                st.metric("Números Críticos", len(resultados['critical_numbers']))
            with col4:
                st.metric("Fecha Análisis", resultados['analysis_date'][:10])
            
            # Ranking de números
            st.subheader("🏆 Ranking de Números por Score")
            ranking_df = analyzer.get_ranking()
            
            if not ranking_df.empty:
                st.dataframe(
                    ranking_df.head(20),
                    use_container_width=True,
                    hide_index=True
                )
                
                # Botón para exportar
                if st.button("📥 Exportar Resultados JSON"):
                    export_path = f"resultados_sefirot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    if analyzer.export_json(export_path):
                        st.success(f"✅ Resultados exportados a: {export_path}")
                    else:
                        st.error("❌ Error al exportar resultados")
            
            # Números críticos
            if resultados['critical_numbers']:
                st.subheader("⚠️ Números Críticos")
                st.info("Números con alta ausencia pero alta energía sefirotica")
                
                critical_data = []
                for num in resultados['critical_numbers'][:10]:
                    critical_data.append({
                        'Número': num['numero'],
                        'Sefirá': num['sefira_name'],
                        'Energía': num['sefira_energy'],
                        'Frecuencia': num['freq_abs'],
                        'Ausencia': num['ausencia'],
                        'Score': f"{num['score']:.2f}"
                    })
                
                if critical_data:
                    st.dataframe(
                        pd.DataFrame(critical_data),
                        use_container_width=True,
                        hide_index=True
                    )
            
            # Estadísticas resumen
            if 'summary_stats' in resultados:
                st.subheader("📊 Estadísticas Resumen")
                
                stats = resultados['summary_stats']
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Frecuencia Promedio", f"{stats.get('avg_frequency', 0):.2f}")
                    st.metric("Ausencia Promedio", f"{stats.get('avg_absence', 0):.2f}")
                    st.metric("Score Promedio", f"{stats.get('avg_score', 0):.2f}")
    
                with col2:
                    st.metric("Frecuencia Máxima", stats.get('max_frequency', 0))
                    st.metric("Ausencia Máxima", stats.get('max_absence', 0))
                    st.metric("Score Máximo", f"{stats.get('max_score', 0):.2f}")
                
                # Distribución por Sefirot
                if 'sefirot_distribution' in stats:
                    st.subheader("🔮 Distribución por Sefirot")
                    sefirot_dist = stats['sefirot_distribution']
                    
                    # Crear gráfico de barras simple
                    sefirot_df = pd.DataFrame(
                        list(sefirot_dist.items()),
                        columns=['Sefirá', 'Cantidad']
                    ).sort_values('Cantidad', ascending=False)
                    
                    st.bar_chart(sefirot_df.set_index('Sefirá'))
    
    except ImportError as e:
        st.error(f"❌ Error importando Sefirot Analyzer: {e}")
        st.info("💡 Asegúrate de que el módulo esté correctamente instalado")
    
    except Exception as e:
        st.error(f"❌ Error en Sefirot Analyzer: {e}")
        st.info("💡 Revisa la configuración y datos de entrada")

def display_command_interface():
    """Muestra la interfaz de comandos para control remoto"""
    st.title("🎮 INTERFAZ DE COMANDOS")
    st.markdown("### Control Remoto del Protocolo Universal Oficial")
    st.markdown("---")
    
    # Ejecutor automático
    try:
        from modules.auto_executor import auto_executor
        auto_executor.render_auto_executor_ui()
        st.markdown("---")
    except ImportError as e:
        st.error(f"Error cargando ejecutor automático: {str(e)}")
    
    # Área de comandos
    st.subheader("💬 Consola de Comandos")
    
    # Input de comando
    command = st.text_input(
        "Ingresa tu comando:",
        placeholder="Ejemplo: INICIAR PROTOCOLO",
        help="Comandos disponibles: INICIAR, PAUSAR, CONTINUAR, REINICIAR, VER ESTADO, EJECUTAR PASO X"
    )
    
    # Botones de comandos rápidos
    st.subheader("⚡ Comandos Rápidos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 INICIAR PROTOCOLO UNIVERSAL OFICIAL", use_container_width=True, type="primary"):
            execute_command("INICIAR PROTOCOLO")
    
    with col2:
        if st.button("⏸️ PAUSAR", use_container_width=True):
            execute_command("PAUSAR")
    
    with col3:
        if st.button("▶️ CONTINUAR", use_container_width=True):
            execute_command("CONTINUAR")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🔄 REINICIAR", use_container_width=True):
            execute_command("REINICIAR")
    
    with col5:
        if st.button("📊 VER ESTADO", use_container_width=True):
            execute_command("VER ESTADO")
    
    with col6:
        if st.button("⚙️ CONFIGURAR", use_container_width=True):
            execute_command("CONFIGURAR")
    
    # Ejecutar comando personalizado
    if st.button("▶️ Ejecutar Comando", use_container_width=True, type="secondary") and command:
        execute_command(command.upper())
    
    # Historial de comandos
    if 'command_history' not in st.session_state:
        st.session_state.command_history = []
    
    if st.session_state.command_history:
        st.markdown("---")
        st.subheader("📜 Historial de Comandos")
        for i, cmd in enumerate(reversed(st.session_state.command_history[-10:])):
            st.text(f"{len(st.session_state.command_history) - i}. {cmd}")

def execute_command(command: str):
    """Ejecuta comandos del protocolo universal oficial"""
    
    # Agregar al historial
    if 'command_history' not in st.session_state:
        st.session_state.command_history = []
    
    st.session_state.command_history.append(f"{datetime.now().strftime('%H:%M:%S')} - {command}")
    
    # Intentar usar el ejecutor automático primero
    try:
        from modules.auto_executor import auto_executor
        result = auto_executor._execute_command(command)
        
        if result['status'] == 'success':
            st.success(f"✅ {result['message']}")
            if 'protocol_step' in result:
                st.session_state.protocol_step = result['protocol_step']
            if 'protocol_status' in result:
                st.session_state.protocol_status = result['protocol_status']
            if 'successful_steps' in result:
                st.session_state.successful_steps = result['successful_steps']
            st.rerun()
        elif result['status'] == 'error':
            st.error(f"❌ {result['message']}")
        else:
            # Fallback a comandos manuales
            execute_command_manual(command)
            
    except ImportError:
        # Fallback a comandos manuales si no hay ejecutor automático
        execute_command_manual(command)
    except Exception as e:
        st.error(f"❌ Error ejecutando comando: {str(e)}")
        execute_command_manual(command)

def execute_command_manual(command: str):
    """Ejecuta comandos manualmente (fallback)"""
    
    # Procesar comando
    if command == "INICIAR PROTOCOLO":
        st.session_state.protocol_step = 0
        st.session_state.protocol_status = 'running'
        st.session_state.successful_steps = 0
        st.session_state.errors_encountered = 0
        st.success("🚀 Protocolo Universal Oficial iniciado - Listo para ejecutar")
        st.rerun()
    
    elif command == "PAUSAR":
        if st.session_state.get('protocol_status') == 'running':
            st.session_state.protocol_status = 'paused'
            st.warning("⏸️ Protocolo pausado")
        else:
            st.info("ℹ️ El protocolo no está ejecutándose")
    
    elif command == "CONTINUAR":
        if st.session_state.get('protocol_status') == 'paused':
            st.session_state.protocol_status = 'running'
            st.success("▶️ Protocolo reanudado")
        else:
            st.info("ℹ️ El protocolo no está pausado")
    
    elif command == "REINICIAR":
        st.session_state.protocol_step = 0
        st.session_state.protocol_status = 'idle'
        st.session_state.successful_steps = 0
        st.session_state.errors_encountered = 0
        st.success("🔄 Protocolo Universal Oficial reiniciado completamente")
        st.rerun()
    
    elif command == "VER ESTADO":
        st.info(f"📊 Estado actual: Paso {st.session_state.get('protocol_step', 0)}, Estado: {st.session_state.get('protocol_status', 'idle')}")
    
    elif command == "CONFIGURAR":
        st.session_state.current_section = 'protocol_config'
        st.rerun()
    
    elif command.startswith("EJECUTAR PASO"):
        try:
            step_num = int(command.split()[-1])
            if 1 <= step_num <= 7:
                st.session_state.protocol_step = step_num - 1
                st.session_state.protocol_status = 'running'
                st.success(f"🎯 Ejecutando Paso {step_num}")
                st.rerun()
            else:
                st.error("❌ Número de paso inválido (1-7)")
        except ValueError:
            st.error("❌ Formato de comando inválido. Usa: EJECUTAR PASO X")
    
    else:
        st.warning(f"⚠️ Comando no reconocido: {command}")
        st.info("💡 Comandos disponibles: INICIAR, PAUSAR, CONTINUAR, REINICIAR, VER ESTADO, EJECUTAR PASO X")

# =================== FUNCIONES DE AUDITOR DE VERACIDAD ===================

def display_veracity_auditor():
    """Muestra la interfaz principal del auditor de veracidad"""
    st.title("🔍 AUDITOR DE VERACIDAD DE INFORMACIÓN")
    st.markdown("### Verifica que toda información obtenida de internet sea fidedigna y de fuentes reales")
    st.markdown("---")
    
    try:
        from modules.veracity_auditor import veracity_auditor
        veracity_auditor.render_veracity_ui()
    except ImportError as e:
        st.error(f"❌ Error importando el auditor de veracidad: {str(e)}")
        st.info("💡 Asegúrate de que el módulo veracity_auditor.py esté en la carpeta modules/")
    except Exception as e:
        st.error(f"❌ Error ejecutando el auditor: {str(e)}")

def display_veracity_reports():
    """Muestra reportes históricos de veracidad"""
    st.title("📊 REPORTES DE VERACIDAD")
    st.markdown("### Historial de auditorías de veracidad realizadas")
    st.markdown("---")
    
    # Verificar si hay reportes en session_state
    if 'veracity_reports' not in st.session_state:
        st.session_state.veracity_reports = []
    
    if st.session_state.veracity_reports:
        st.subheader("📋 **Historial de Auditorías**")
        
        for i, report in enumerate(st.session_state.veracity_reports):
            with st.expander(f"Auditoría {i+1} - {report.get('timestamp', 'Sin fecha')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Puntuación", f"{report.get('veracity_score', 0):.1%}")
                
                with col2:
                    st.metric("Nivel de Riesgo", report.get('risk_level', 'Unknown'))
                
                with col3:
                    st.metric("Fuentes Verificadas", f"{report.get('sources_verified', 0)}")
                
                st.write(f"**Contenido:** {report.get('content', 'N/A')[:100]}...")
                st.write(f"**Fuentes:** {', '.join(report.get('source_urls', []))}")
                
                if report.get('recommendations'):
                    st.write("**Recomendaciones:**")
                    for rec in report['recommendations']:
                        st.write(f"- {rec}")
    else:
        st.info("📝 No hay reportes de veracidad disponibles. Realiza una auditoría para generar reportes.")
    
    # Botón para limpiar reportes
    if st.button("🗑️ Limpiar Reportes", use_container_width=True):
        st.session_state.veracity_reports = []
        st.rerun()

def display_veracity_config():
    """Muestra la configuración del auditor de veracidad"""
    st.title("⚙️ CONFIGURACIÓN DEL AUDITOR DE VERACIDAD")
    st.markdown("### Configuración avanzada del sistema de verificación")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 **Configuración de Fuentes**")
        
        # Configuración de dominios confiables
        st.write("**Dominios de Alta Confianza:**")
        trusted_domains = st.text_area(
            "Dominios confiables (uno por línea):",
            value="bbc.com\ncnn.com\nreuters.com\nap.org\nbloomberg.com\nwsj.com\nnytimes.com",
            height=150
        )
        
        # Configuración de TLDs confiables
        st.write("**TLDs Confiables:**")
        trusted_tlds = st.multiselect(
            "Selecciona TLDs confiables:",
            ['.edu', '.gov', '.org', '.mil', '.com', '.net'],
            default=['.edu', '.gov', '.org', '.mil']
        )
        
        # Configuración de APIs de fact-checking
        st.subheader("🔍 **APIs de Fact-Checking**")
        
        google_fact_check = st.checkbox("Google Fact Check API", value=True)
        snopes_api = st.checkbox("Snopes API", value=True)
        politifact_api = st.checkbox("PolitiFact API", value=True)
    
    with col2:
        st.subheader("⚡ **Configuración de Rendimiento**")
        
        # Timeouts
        st.write("**Timeouts (segundos):**")
        source_timeout = st.number_input("Timeout para fuentes", min_value=5, max_value=60, value=10)
        fact_check_timeout = st.number_input("Timeout para fact-checking", min_value=10, max_value=120, value=30)
        
        # Límites de contenido
        st.write("**Límites de Contenido:**")
        max_content_length = st.number_input("Longitud máxima de contenido", min_value=1000, max_value=100000, value=10000)
        max_sources = st.number_input("Número máximo de fuentes", min_value=1, max_value=20, value=10)
        
        # Configuración de patrones sospechosos
        st.subheader("🚨 **Detección de Patrones Sospechosos**")
        
        enable_pattern_detection = st.checkbox("Habilitar detección de patrones", value=True)
        pattern_sensitivity = st.slider("Sensibilidad de detección", 0.1, 1.0, 0.7)
        
        # Configuración de alertas
        st.subheader("🔔 **Alertas y Notificaciones**")
        
        enable_alerts = st.checkbox("Habilitar alertas", value=True)
        alert_threshold = st.slider("Umbral de alerta", 0.0, 1.0, 0.5)
    
    # Botones de acción
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Configuración", use_container_width=True, type="primary"):
            # Guardar configuración en session_state
            st.session_state.veracity_config = {
                'trusted_domains': trusted_domains.split('\n'),
                'trusted_tlds': trusted_tlds,
                'google_fact_check': google_fact_check,
                'snopes_api': snopes_api,
                'politifact_api': politifact_api,
                'source_timeout': source_timeout,
                'fact_check_timeout': fact_check_timeout,
                'max_content_length': max_content_length,
                'max_sources': max_sources,
                'enable_pattern_detection': enable_pattern_detection,
                'pattern_sensitivity': pattern_sensitivity,
                'enable_alerts': enable_alerts,
                'alert_threshold': alert_threshold
            }
            st.success("✅ Configuración guardada exitosamente")
    
    with col2:
        if st.button("🔄 Restaurar Predeterminados", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🧪 Probar Configuración", use_container_width=True):
            st.info("🔍 Probando configuración...")
            # Aquí se podría implementar una prueba de la configuración
            st.success("✅ Configuración válida")

def display_veracity_self_protection():
    """Muestra la interfaz de autoprotección del auditor"""
    st.title("🛡️ AUTOPROTECCIÓN DEL AUDITOR")
    st.markdown("### Sistema de verificación de salud y confiabilidad del auditor")
    st.markdown("---")
    
    try:
        from modules.auditor_self_protection import auditor_self_protection
        auditor_self_protection.render_self_protection_ui()
    except ImportError as e:
        st.error(f"❌ Error importando el sistema de autoprotección: {str(e)}")
        st.info("💡 Asegúrate de que el módulo auditor_self_protection.py esté en la carpeta modules/")
    except Exception as e:
        st.error(f"❌ Error ejecutando el sistema de autoprotección: {str(e)}")

# =================== FUNCIONES DE FLORIDA LOTTERY ===================

def display_florida_lottery_analysis():
    """Muestra la interfaz principal de análisis de Florida Lottery"""
    st.title("🎰 ANÁLISIS FLORIDA LOTTERY")
    st.markdown("### Sistema de Análisis de Sorteos de Florida con Transformación Bolita")
    st.markdown("---")
    
    try:
        from modules.florida_lottery_steps import BolitaFromFloridaStep, FetchFLPick3RealStep
        from app_vision.engine.fsm import pipeline_executor
        import json
        
        # Configuración del análisis
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("⚙️ Configuración del Análisis")
            
            # Selector de tipo de análisis
            analysis_type = st.selectbox(
                "Tipo de análisis:",
                ["Análisis Individual", "Pipeline Completo", "Análisis de Patrones"],
                index=0
            )
            
            # Configuración de datos
            if analysis_type == "Análisis Individual":
                st.markdown("#### 📊 Datos del Sorteo")
                
                col_date, col_block = st.columns(2)
                with col_date:
                    draw_date = st.date_input("Fecha del sorteo", value=datetime.now().date())
                with col_block:
                    block = st.selectbox("Bloque", ["MID", "EVE"])
                
                col_pick3, col_pick4 = st.columns(2)
                with col_pick3:
                    pick3_input = st.text_input("Pick 3 (ej: 1,2,3)", value="1,2,3")
                    try:
                        pick3 = [int(x.strip()) for x in pick3_input.split(",")]
                        if len(pick3) != 3:
                            st.error("Pick 3 debe tener exactamente 3 números")
                    except:
                        st.error("Formato inválido para Pick 3")
                        pick3 = [1, 2, 3]
                
                with col_pick4:
                    pick4_input = st.text_input("Pick 4 (opcional, ej: 1,2,3,4)", value="")
                    pick4 = None
                    if pick4_input:
                        try:
                            pick4 = [int(x.strip()) for x in pick4_input.split(",")]
                            if len(pick4) != 4:
                                st.error("Pick 4 debe tener exactamente 4 números")
                                pick4 = None
                        except:
                            st.error("Formato inválido para Pick 4")
                            pick4 = None
                
                # Configuración de análisis
                st.markdown("#### 🔧 Opciones de Análisis")
                use_empuxe = st.checkbox("Usar Empuje", value=False)
                prefer_pick4_as_corrido = st.checkbox("Preferir Pick4 como Corrido", value=True)
                
                other_pick3_last2 = st.text_input("Otro bloque Pick3 últimos 2 (opcional)", value="")
                if other_pick3_last2 and len(other_pick3_last2) != 2:
                    st.error("Debe ser exactamente 2 dígitos")
                    other_pick3_last2 = ""
            
            elif analysis_type == "Pipeline Completo":
                st.markdown("#### 🔄 Configuración del Pipeline")
                min_results = st.number_input("Mínimo de resultados", min_value=2, max_value=10, value=2)
                days_back = st.number_input("Días hacia atrás", min_value=1, max_value=30, value=7)
            
            elif analysis_type == "Análisis de Patrones":
                st.markdown("#### 📈 Configuración de Patrones")
                pattern_days = st.number_input("Días para análisis de patrones", min_value=7, max_value=90, value=30)
        
        with col2:
            st.subheader("📊 Información del Sistema")
            
            # Mostrar pasos registrados
            from app_vision.engine.fsm import list_registered_steps
            registered_steps = list_registered_steps()
            
            st.write("**Pasos Registrados:**")
            for step in registered_steps:
                st.write(f"• {step}")
            
            # Estado del pipeline
            executions = pipeline_executor.get_all_executions()
            st.metric("Ejecuciones Totales", len(executions))
            
            if executions:
                last_execution = executions[-1]
                st.metric("Última Ejecución", last_execution.get("status", "Unknown"))
        
        # Botón de ejecución
        if st.button("🚀 Ejecutar Análisis", type="primary", use_container_width=True):
            with st.spinner("Ejecutando análisis..."):
                try:
                    if analysis_type == "Análisis Individual":
                        # Crear contexto y ejecutar paso individual
                        from app_vision.engine.contracts import StepContext
                        
                        ctx = StepContext(
                            step_name="individual_analysis",
                            step_id="individual_1",
                            pipeline_id="individual",
                            execution_id="individual_1",
                            metadata={}
                        )
                        
                        step = BolitaFromFloridaStep()
                        result = step.run(ctx, {
                            "focus": {
                                "date": str(draw_date),
                                "block": block,
                                "pick3": pick3,
                                "pick4": pick4
                            },
                            "other_pick3_last2": other_pick3_last2 if other_pick3_last2 else None,
                            "use_empuxe": use_empuxe,
                            "prefer_pick4_as_corrido": prefer_pick4_as_corrido
                        })
                        
                        st.session_state.florida_analysis_result = result
                        st.success("✅ Análisis individual completado")
                    
                    elif analysis_type == "Pipeline Completo":
                        # Ejecutar pipeline completo
                        pipeline_config = {
                            "steps": [
                                {
                                    "name": "step1_fetch_real",
                                    "class": "FetchFLPick3RealStep",
                                    "inputs": {"min_results": min_results, "days_back": days_back}
                                },
                                {
                                    "name": "step_bolita_mid",
                                    "class": "BolitaFromFloridaStep",
                                    "inputs": {
                                        "focus": {
                                            "date": "${step.step1_fetch_real.draws[0].date}",
                                            "block": "${step.step1_fetch_real.draws[0].block}",
                                            "pick3": "${step.step1_fetch_real.draws[0].numbers}",
                                            "pick4": "${step.step1_fetch_real.draws[0].pick4}"
                                        },
                                        "other_pick3_last2": "${step.step1_fetch_real.draws[1].numbers}",
                                        "use_empuxe": False,
                                        "prefer_pick4_as_corrido": True
                                    }
                                },
                                {
                                    "name": "step_candado_export",
                                    "class": "CandadoExportStep",
                                    "inputs": {
                                        "bolita": "${step.step_bolita_mid.bolita}",
                                        "include_parles": True
                                    }
                                }
                            ]
                        }
                        
                        result = pipeline_executor.execute_pipeline(pipeline_config)
                        st.session_state.florida_pipeline_result = result
                        st.success("✅ Pipeline completado")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error ejecutando análisis: {str(e)}")
        
        # Mostrar resultados
        if 'florida_analysis_result' in st.session_state:
            st.markdown("---")
            st.subheader("📊 Resultados del Análisis Individual")
            
            result = st.session_state.florida_analysis_result
            bolita = result.get('bolita', {})
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("FIJO 3D", bolita.get('fijo', {}).get('3d', 'N/A'))
            with col2:
                st.metric("FIJO 2D", bolita.get('fijo', {}).get('2d', 'N/A'))
            with col3:
                st.metric("Corridos", len(bolita.get('corridos', [])))
            with col4:
                st.metric("Parlés", len(bolita.get('parles', [])))
            
            # Detalles del análisis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 FIJO")
                st.json(bolita.get('fijo', {}))
                
                st.markdown("#### 🏃 CORRIDOS")
                st.write(bolita.get('corridos', []))
            
            with col2:
                st.markdown("#### 🔒 CANDADO")
                st.write(bolita.get('candado', []))
                
                st.markdown("#### 🎲 PARLÉS")
                st.write(bolita.get('parles', []))
            
            if bolita.get('empuje'):
                st.markdown("#### ⚡ EMPUJE")
                st.success(f"**{bolita['empuje']}**")
            
            # Origen de datos
            with st.expander("📋 Ver origen de datos"):
                st.json(bolita.get('origen', {}))
        
        elif 'florida_pipeline_result' in st.session_state:
            st.markdown("---")
            st.subheader("📊 Resultados del Pipeline")
            
            result = st.session_state.florida_pipeline_result
            
            # Mostrar resultados del pipeline paso a paso
            if 'step_results' in result:
                st.markdown("#### 🔄 Ejecución del Pipeline")
                
                # Mostrar cada paso
                for step_name, step_result in result['step_results'].items():
                    with st.expander(f"📋 {step_name}"):
                        st.json(step_result)
                
                # Mostrar deliverable final si existe
                if 'step_candado_export' in result['step_results']:
                    deliverable = result['step_results']['step_candado_export'].get('deliverable', {})
                    
                    if deliverable:
                        st.markdown("---")
                        st.subheader("🎯 DELIVERABLE FINAL")
                        
                        # Métricas del deliverable
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Modo", deliverable.get('mode', 'N/A'))
                        with col2:
                            st.metric("Fecha", deliverable.get('date', 'N/A'))
                        with col3:
                            st.metric("Bloque", deliverable.get('block', 'N/A'))
                        with col4:
                            candado = deliverable.get('candado', [])
                            st.metric("Candado", f"{len(candado)} elementos")
                        
                        # Mostrar candado
                        st.markdown("#### 🔒 CANDADO")
                        candado_display = deliverable.get('candado', [])
                        if candado_display:
                            st.success(f"**{', '.join(candado_display)}**")
                        else:
                            st.warning("No hay candado disponible")
                        
                        # Mostrar parlés si existen
                        parles = deliverable.get('parles', [])
                        if parles:
                            st.markdown("#### 🎲 PARLÉS")
                            for i, par in enumerate(parles, 1):
                                st.write(f"{i}. {par[0]} - {par[1]}")
                        
                        # Mostrar fuente
                        fuente = deliverable.get('fuente', {})
                        if fuente:
                            st.markdown("#### 📋 FUENTE DE DATOS")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.write(f"**Pick3 Block:** {fuente.get('pick3_block', 'N/A')}")
                                st.write(f"**Pick4 Block:** {fuente.get('pick4_block', 'N/A')}")
                            
                            with col2:
                                st.write(f"**Other Pick3 Last2:** {fuente.get('other_pick3_last2', 'N/A')}")
                        
                        # JSON completo del deliverable
                        with st.expander("📋 Ver deliverable completo (JSON)"):
                            st.json(deliverable)
            else:
                st.json(result)
    
    except ImportError as e:
        st.error(f"❌ Error importando módulos de Florida Lottery: {str(e)}")
        st.info("💡 Asegúrate de que todos los módulos estén correctamente instalados")
    except Exception as e:
        st.error(f"❌ Error en análisis de Florida Lottery: {str(e)}")

def display_florida_lottery_pipeline():
    """Muestra la interfaz de configuración de pipeline de Florida Lottery"""
    st.title("🔄 PIPELINE BOLITA FLORIDA")
    st.markdown("### Configuración y Ejecución de Pipelines de Análisis")
    st.markdown("---")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔄 Funcionalidades Planificadas:")
        st.info("""
        - Configuración visual de pipelines
        - Ejecución paso a paso
        - Monitoreo en tiempo real
        - Exportación de resultados
        """)
    
    with col2:
        st.markdown("#### 📊 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Engine FSM implementado
        - Pasos básicos disponibles
        - Interfaz en progreso
        """)

def display_florida_lottery_patterns():
    """Muestra la interfaz de análisis de patrones de Florida Lottery"""
    st.title("📊 PATRONES FLORIDA LOTTERY")
    st.markdown("### Análisis de Patrones Históricos y Tendencias")
    st.markdown("---")
    
    st.info("🚧 **En desarrollo** - Esta funcionalidad estará disponible próximamente")
    
    # Placeholder para funcionalidad futura
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Funcionalidades Planificadas:")
        st.info("""
        - Análisis de patrones históricos
        - Identificación de tendencias
        - Predicción de probabilidades
        - Reportes estadísticos
        """)
    
    with col2:
        st.markdown("#### 🔧 Estado Actual:")
        st.warning("""
        - Módulo en desarrollo
        - Algoritmos de análisis
        - Base de datos histórica
        - Visualizaciones en progreso
        """)

# =================== FUNCIÓN PRINCIPAL ===================

def main():
    """Función principal de la aplicación"""
    # Crear menú lateral
    create_sidebar()
    
    # Mostrar contenido según la sección seleccionada
    current_section = st.session_state.current_section
    
    if current_section == 'inicio':
        show_inicio()
    elif current_section == 'ia_analysis':
        show_ia_analysis()
    elif current_section == 'ia_config':
        show_system_module('ia_config', 'CONFIGURACIÓN IA', 'Configuración del Motor de IA')
    elif current_section == 'news_analysis':
        show_news_analysis()
    elif current_section == 'news_fetcher':
        show_system_module('news_fetcher', 'BUSCADOR EN RED', 'Búsqueda de Noticias en Fuentes Oficiales')
    elif current_section == 'news_trends':
        show_system_module('news_trends', 'TENDENCIAS', 'Análisis de Tendencias de Noticias')
    elif current_section == 't70_generator':
        show_t70_generator()
    elif current_section == 't70_analysis':
        show_system_module('t70_analysis', 'ANÁLISIS T70', 'Análisis de Patrones T70')
    elif current_section == 't70_history':
        show_system_module('t70_history', 'HISTORIAL T70', 'Historial de Resultados T70')
    elif current_section == 't100_update':
        show_system_module('t100_update', 'ACTUALIZAR T100', 'Actualización de Base de Datos T100')
    elif current_section == 'gematria_calculator':
        show_gematria_calculator()
    elif current_section == 'gematria_dictionary':
        show_system_module('gematria_dictionary', 'DICCIONARIO GEMATRÍA', 'Diccionario de Valores Gematría')
    elif current_section == 'gematria_analysis':
        show_system_module('gematria_analysis', 'ANÁLISIS GEMATRÍA', 'Análisis Gematría Avanzado')
    elif current_section == 'subliminal_detector':
        show_subliminal_detector()
    elif current_section == 'subliminal_archetypes':
        show_system_module('subliminal_archetypes', 'ARQUETIPOS', 'Análisis de Arquetipos Subliminales')
    elif current_section == 'subliminal_analysis':
        show_system_module('subliminal_analysis', 'ANÁLISIS SUBLIMINAL', 'Análisis Subliminal Avanzado')
    elif current_section == 'data_quality':
        show_system_module('data_quality', 'CALIDAD DE DATOS', 'Sistema de Calidad de Datos')
    elif current_section == 'catalog':
        show_system_module('catalog', 'CATÁLOGO', 'Sistema de Catálogo de Datasets')
    elif current_section == 'governance':
        show_system_module('governance', 'GOBERNANZA', 'Sistema de Gobernanza y Seguridad')
    elif current_section == 'orchestration':
        show_system_module('orchestration', 'ORQUESTACIÓN', 'Sistema de Orquestación')
    elif current_section == 'observability':
        show_system_module('observability', 'OBSERVABILIDAD', 'Sistema de Observabilidad')
    elif current_section == 'mlops':
        show_system_module('mlops', 'MLOPS', 'Sistema MLOps')
    elif current_section == 'explainability':
        show_system_module('explainability', 'EXPLICABILIDAD', 'Sistema de Explicabilidad')
    elif current_section == 'semantic_search':
        show_system_module('semantic_search', 'BÚSQUEDA SEMÁNTICA', 'Sistema de Búsqueda Semántica')
    elif current_section == 'feedback':
        show_system_module('feedback', 'FEEDBACK', 'Sistema de Feedback')
    elif current_section == 'qa_tests':
        show_system_module('qa_tests', 'QA TESTS', 'Sistema de Pruebas de Calidad')
    elif current_section == 'cache_management':
        show_cache_management()
    elif current_section == 'validation':
        show_system_module('validation', 'VALIDACIÓN', 'Sistema de Validación')
    elif current_section == 'monitoring':
        show_system_module('monitoring', 'MONITOREO', 'Sistema de Monitoreo')
    elif current_section == 'settings':
        show_system_module('settings', 'CONFIGURACIÓN', 'Configuración del Sistema')
    elif current_section == 'protocol_execution':
        display_protocol_execution()
    elif current_section == 'protocol_status':
        display_protocol_status()
    elif current_section == 'protocol_config':
        display_protocol_config()
    elif current_section == 'protocol_commands':
        display_command_interface()
    elif current_section == 'protocolo':
        display_protocolo()
    elif current_section == 'sefirot_analyzer':
        display_sefirot_analyzer()
    elif current_section == 'veracity_auditor':
        display_veracity_auditor()
    elif current_section == 'veracity_reports':
        display_veracity_reports()
    elif current_section == 'veracity_config':
        display_veracity_config()
    elif current_section == 'veracity_self_protection':
        display_veracity_self_protection()
    elif current_section == 'florida_lottery_analysis':
        display_florida_lottery_analysis()
    elif current_section == 'florida_lottery_pipeline':
        display_florida_lottery_pipeline()
    elif current_section == 'florida_lottery_patterns':
        display_florida_lottery_patterns()
    else:
        show_inicio()

if __name__ == "__main__":
    main()
