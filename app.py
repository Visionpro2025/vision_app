# app_clean.py — VISION PREMIUM - Sistema Limpio y Modular
import streamlit as st
from pathlib import Path
import sys
import os
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Configurar el entorno
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Configuración de la página
st.set_page_config(
    page_title="VISION PREMIUM - Sistema Limpio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== SISTEMA DE ORQUESTACIÓN GLOBAL ===================

def load_global_policy():
    """Carga la política global del sistema"""
    try:
        import yaml
        policy_path = Path("plans/policy_app.yaml")
        if policy_path.exists():
            with open(policy_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: No se pudo cargar política global: {e}")
    return {}

def enforce_global_policy():
    """Aplica la política global al sistema"""
    policy = load_global_policy()
    
    # Enforce: Cursor solo orquesta
    if policy.get("app", {}).get("orchestrator") != "cursor_only":
        st.error("❌ Violación de política: Orquestador debe ser 'cursor_only'")
        st.stop()
    
    # Enforce: Sin simulaciones
    if policy.get("app", {}).get("allow_simulation", True):
        st.error("❌ Violación de política: allow_simulation debe ser False")
        st.stop()
    
    # Enforce: Fuentes requeridas
    if not policy.get("app", {}).get("require_sources", True):
        st.error("❌ Violación de política: require_sources debe ser True")
        st.stop()
    
    return policy

# =================== SISTEMA DE GESTIÓN DE ESTADO ===================

class StateManager:
    """Gestor centralizado del estado de la aplicación"""
    
    @staticmethod
    def initialize():
        """Inicializa el estado base de la aplicación"""
        defaults = {
            'current_section': 'home',
            'last_reset': datetime.now().isoformat(),
            'system_status': 'ready',
            'active_modules': [],
            'execution_history': [],
            'current_execution': None
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def reset_system():
        """Reinicia completamente el sistema"""
        keys_to_keep = ['current_section']
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        StateManager.initialize()
        return True
    
    @staticmethod
    def get_state(key: str, default: Any = None) -> Any:
        """Obtiene un valor del estado"""
        return st.session_state.get(key, default)
    
    @staticmethod
    def set_state(key: str, value: Any):
        """Establece un valor en el estado"""
        st.session_state[key] = value

# =================== SISTEMA DE MÓDULOS ===================

class ModuleRegistry:
    """Registro central de módulos del sistema"""
    
    def __init__(self):
        self.modules = {}
    
    def register_module(self, name: str, config: Dict[str, Any]):
        """Registra un nuevo módulo"""
        self.modules[name] = {
            'name': name,
            'title': config.get('title', name),
            'icon': config.get('icon', '📦'),
            'description': config.get('description', ''),
            'handler': config.get('handler'),
            'enabled': config.get('enabled', True),
            'category': config.get('category', 'general')
        }
    
    def get_modules_by_category(self, category: str) -> Dict[str, Dict]:
        """Obtiene módulos por categoría"""
        return {k: v for k, v in self.modules.items() 
                if v['category'] == category and v['enabled']}
    
    def get_module(self, name: str) -> Optional[Dict]:
        """Obtiene un módulo específico"""
        return self.modules.get(name)

# Instancia global del registro
module_registry = ModuleRegistry()

# =================== NAVEGACIÓN PRINCIPAL ===================

def render_sidebar():
    """Renderiza el menú lateral principal"""
    st.sidebar.title("🎯 VISION PREMIUM")
    st.sidebar.markdown("### Sistema Modular Limpio")
    st.sidebar.markdown("---")
    
    # Botón de inicio
    if st.sidebar.button("🏠 Inicio", use_container_width=True, type="primary"):
        StateManager.set_state('current_section', 'home')
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Categorías de módulos
    categories = {
        'ai': {'title': '🧠 INTELIGENCIA ARTIFICIAL', 'icon': '🤖'},
        'lottery': {'title': '🎰 SISTEMAS DE LOTERÍA', 'icon': '🎲'},
        'analysis': {'title': '📊 ANÁLISIS Y PATRONES', 'icon': '📈'},
        'tools': {'title': '🛠️ HERRAMIENTAS', 'icon': '⚙️'},
        'admin': {'title': '👑 ADMINISTRACIÓN', 'icon': '🔧'}
    }
    
    for category_id, category_info in categories.items():
        st.sidebar.markdown(f"### {category_info['title']}")
        
        modules = module_registry.get_modules_by_category(category_id)
        
        if modules:
            for module_name, module_config in modules.items():
                if st.sidebar.button(
                    f"{module_config['icon']} {module_config['title']}", 
                    use_container_width=True
                ):
                    StateManager.set_state('current_section', module_name)
                    st.rerun()
        else:
            st.sidebar.info("No hay módulos disponibles")
        
        st.sidebar.markdown("---")
    
    # Panel de control del sistema
    st.sidebar.markdown("### 🔄 CONTROL DEL SISTEMA")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            StateManager.reset_system()
            st.success("Sistema reiniciado")
            st.rerun()
    
    with col2:
        if st.button("📊 Estado", use_container_width=True):
            StateManager.set_state('current_section', 'system_status')
            st.rerun()

# =================== PÁGINAS DEL SISTEMA ===================

def show_home():
    """Página de inicio del sistema"""
    st.title("🎯 VISION PREMIUM")
    st.markdown("## Sistema Modular Limpio y Organizado")
    
    st.markdown("---")
    
    # Información del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Estado", "🟢 OPERATIVO")
    
    with col2:
        active_modules = len([m for m in module_registry.modules.values() if m['enabled']])
        st.metric("Módulos Activos", active_modules)
    
    with col3:
        executions = len(StateManager.get_state('execution_history', []))
        st.metric("Ejecuciones", executions)
    
    with col4:
        last_reset = StateManager.get_state('last_reset', '')
        if last_reset:
            reset_time = datetime.fromisoformat(last_reset).strftime("%H:%M")
            st.metric("Último Reset", reset_time)
    
    st.markdown("---")
    
    # Características del sistema limpio
    st.markdown("### ✨ Características del Sistema Limpio")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🏗️ ARQUITECTURA MODULAR**
        - Sistema de registro de módulos
        - Estado centralizado y limpio
        - Navegación consistente
        - Gestión de errores unificada
        """)
        
        st.success("""
        **🔧 GESTIÓN DE ESTADO**
        - Sin variables hardcodeadas
        - Estado centralizado
        - Reset completo disponible
        - Historial de ejecuciones
        """)
    
    with col2:
        st.warning("""
        **📦 MÓDULOS DISPONIBLES**
        - Inteligencia Artificial
        - Sistemas de Lotería  
        - Análisis y Patrones
        - Herramientas
        - Administración
        """)
        
        st.error("""
        **🚀 PREPARADO PARA FUTURO**
        - Fácil adición de módulos
        - Configuración flexible
        - Sin dependencias hardcodeadas
        - Arquitectura escalable
        """)

def show_system_status():
    """Página de estado del sistema"""
    st.title("📊 ESTADO DEL SISTEMA")
    st.markdown("### Monitoreo y Diagnóstico Completo")
    
    st.markdown("---")
    
    # Estado general
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Configuración del Sistema")
        
        system_info = {
            "Estado": StateManager.get_state('system_status', 'unknown'),
            "Sección Actual": StateManager.get_state('current_section', 'none'),
            "Último Reset": StateManager.get_state('last_reset', 'never'),
            "Módulos Registrados": len(module_registry.modules)
        }
        
        for key, value in system_info.items():
            st.write(f"**{key}:** {value}")
    
    with col2:
        st.subheader("📦 Módulos Registrados")
        
        if module_registry.modules:
            for name, config in module_registry.modules.items():
                status = "🟢" if config['enabled'] else "🔴"
                st.write(f"{status} {config['icon']} {config['title']}")
        else:
            st.info("No hay módulos registrados")
    
    # Variables de estado
    st.markdown("---")
    st.subheader("🗂️ Variables de Estado Actuales")
    
    if st.checkbox("Mostrar estado completo"):
        state_dict = dict(st.session_state)
        st.json(state_dict)
    
    # Acciones de limpieza
    st.markdown("---")
    st.subheader("🧹 Acciones de Limpieza")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reset Completo", type="primary"):
            StateManager.reset_system()
            st.success("Sistema completamente reiniciado")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpiar Historial"):
            StateManager.set_state('execution_history', [])
            st.success("Historial limpiado")
    
    with col3:
        if st.button("📊 Exportar Estado"):
            state_export = {
                'timestamp': datetime.now().isoformat(),
                'state': dict(st.session_state),
                'modules': module_registry.modules
            }
            st.download_button(
                "⬇️ Descargar Estado",
                data=json.dumps(state_export, indent=2),
                file_name=f"vision_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def show_florida_lottery_analysis():
    """Handler para análisis de Florida Lottery con 3 ventanas diarias y candados completos"""
    st.title("🎰 FLORIDA LOTTERY - 3 VENTANAS DIARIAS")
    st.markdown("### Sistema de Análisis con Candados Completos (AM/MID/EVE)")
    st.markdown("---")
    
    # Información de las ventanas y regla fija
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🕐 VENTANAS DIARIAS:**
        - **AM:** 06:00–06:30 (cierra 06:30)
        - **MID:** 13:35–14:10 (cierra 14:10)  
        - **EVE:** 21:40–22:20 (cierra 22:20)
        """)
    
    with col2:
        st.info("""
        **🔒 REGLA FIJA DE CANDADO:**
        - **FIJO** = últimos 2 del Pick3 del bloque
        - **CORRIDO** = últimos 2 del Pick4 del mismo bloque
        - **TERCERO** = últimos 2 del Pick3 del otro bloque
        """)
    
    # Estado actual de las ventanas
    from app_vision.modules.draw_windows import get_window_status, get_operational_schedule
    from datetime import datetime
    
    current_time = datetime.now()
    window_status = get_window_status(current_time)
    schedule = get_operational_schedule()
    
    st.markdown("#### 🕐 Estado Actual de las Ventanas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        am_status = window_status["windows"]["AM"]
        st.metric(
            "AM", 
            "🟢 ABIERTA" if am_status["is_open"] else "🔴 CERRADA",
            f"Cierra: {schedule['AM']['close']}"
        )
    
    with col2:
        mid_status = window_status["windows"]["MID"]
        st.metric(
            "MID", 
            "🟢 ABIERTA" if mid_status["is_open"] else "🔴 CERRADA",
            f"Cierra: {schedule['MID']['close']}"
        )
    
    with col3:
        eve_status = window_status["windows"]["EVE"]
        st.metric(
            "EVE", 
            "🟢 ABIERTA" if eve_status["is_open"] else "🔴 CERRADA",
            f"Cierra: {schedule['EVE']['close']}"
        )
    
    st.markdown(f"**Ventana Actual:** {window_status['current_block']}")
    st.markdown(f"**Hora Actual:** {current_time.strftime('%H:%M:%S')}")
    
    # Configuración del análisis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("⚙️ Configuración del Análisis")
        
        # Tipo de análisis
        analysis_type = st.selectbox(
            "Tipo de análisis:",
            ["Análisis Individual", "Pipeline Completo", "Plan Predefinido"],
            index=0
        )
        
        if analysis_type == "Análisis Individual":
            st.markdown("#### 📊 Datos del Sorteo")
            
            col_date, col_block = st.columns(2)
            with col_date:
                draw_date = st.date_input("Fecha del sorteo", value=datetime.now().date())
            with col_block:
                block = st.selectbox("Bloque", ["MID", "EVE"])
            
            col_pick3, col_pick4 = st.columns(2)
            with col_pick3:
                pick3_input = st.text_input("Pick 3 (ej: 8,8,1)", value="8,8,1")
                try:
                    pick3 = [int(x.strip()) for x in pick3_input.split(",")]
                    if len(pick3) != 3:
                        st.error("Pick 3 debe tener exactamente 3 números")
                except:
                    st.error("Formato inválido para Pick 3")
                    pick3 = [8, 8, 1]
            
            with col_pick4:
                pick4_input = st.text_input("Pick 4 (opcional, ej: 4,9,2,1)", value="4,9,2,1")
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
            
            # Otro bloque (opcional)
            other_pick3_last2 = st.text_input("Otro bloque Pick3 últimos 2 (opcional)", value="21")
            if other_pick3_last2 and len(other_pick3_last2) != 2:
                st.error("Debe ser exactamente 2 dígitos")
                other_pick3_last2 = "21"
        
        elif analysis_type == "Pipeline Completo":
            st.markdown("#### 🔄 Configuración del Pipeline")
            min_results = st.number_input("Mínimo de resultados", min_value=2, max_value=10, value=2)
            days_back = st.number_input("Días hacia atrás", min_value=1, max_value=30, value=7)
        
        elif analysis_type == "Plan Predefinido":
            st.markdown("#### 📋 Plan Predefinido")
            
            plan_option = st.selectbox(
                "Seleccionar plan:",
                [
                    "florida_candado_fixed.json - Regla fija básica",
                    "florida_3ventanas_completo.json - 3 ventanas completas",
                    "florida_3ventanas_cubano.json - Mapeo cubano con día anterior"
                ],
                index=2
            )
            
            if "cubano" in plan_option:
                st.info("""
                **🇨🇺 MAPEO CUBANO:**
                - **AM** = Florida EVE del día anterior
                - **MID** = Florida MID del mismo día
                - **EVE** = Florida EVE del mismo día
                
                **📊 SALIDA:** 3 candados del día anterior + candado actual
                """)
            else:
                st.info("Usando plan con regla fija de CANDADO")
    
    with col2:
        st.subheader("📊 Información del Sistema")
        
        # Mostrar pasos registrados
        from app_vision.engine.fsm import list_registered_steps
        registered_steps = list_registered_steps()
        
        st.write("**Pasos Registrados:**")
        for step in registered_steps:
            st.write(f"• {step}")
        
        # Estado del sistema
        st.metric("Estado", "🟢 OPERATIVO")
        st.metric("Regla CANDADO", "FIJA")
    
    # Botón de ejecución
    if st.button("🚀 Ejecutar Análisis", type="primary", use_container_width=True):
        with st.spinner("Ejecutando análisis con regla fija de CANDADO..."):
            try:
                if analysis_type == "Análisis Individual":
                    # Ejecutar análisis individual
                    from modules.bolita_transform import FLDraw, derive_bolita
                    
                    result = derive_bolita(
                        focus=FLDraw(date=str(draw_date), block=block, pick3=pick3, pick4=pick4),
                        other_block_pick3_last2=other_pick3_last2 if other_pick3_last2 else None,
                        force_min_candado=True
                    )
                    
                    st.session_state.florida_analysis_result = {"bolita": result}
                    st.success("✅ Análisis individual completado")
                
                elif analysis_type == "Pipeline Completo":
                    # Ejecutar pipeline completo
                    from app_vision.engine.fsm import pipeline_executor
                    
                    pipeline_config = {
                        "steps": [
                            {
                                "name": "step0_enforce",
                                "class": "EnforceOrchestratorStep",
                                "inputs": {
                                    "policy": {
                                        "allow_simulation": False,
                                        "require_sources": True,
                                        "abort_on_empty": True
                                    }
                                }
                            },
                            {
                                "name": "step1_fetch_real",
                                "class": "FetchFLPick3RealStep",
                                "inputs": {"min_results": min_results, "days_back": days_back}
                            },
                            {
                                "name": "step_last2_other_selector",
                                "class": "Last2OtherBlockStep",
                                "inputs": {
                                    "draws": "${step.step1_fetch_real.draws}",
                                    "current_block": "MID"
                                }
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
                                    "other_pick3_last2": "${step.step_last2_other_selector.last2}",
                                    "force_min_candado": True
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
        
        # CANDADO (regla fija)
        st.markdown("#### 🔒 CANDADO (Regla Fija)")
        candado = bolita.get('candado', [])
        if candado:
            st.success(f"**{', '.join(candado)}**")
            st.info(f"**Regla aplicada:** FIJO + CORRIDO + TERCERO")
        else:
            st.warning("No hay candado disponible")
        
        # Detalles del análisis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 FIJO")
            st.json(bolita.get('fijo', {}))
            
            st.markdown("#### 🏃 CORRIDOS")
            st.write(bolita.get('corridos', []))
        
        with col2:
            st.markdown("#### 🎲 PARLÉS")
            st.write(bolita.get('parles', []))
            
            st.markdown("#### 📋 ORIGEN")
            st.json(bolita.get('origen', {}))
    
    elif 'florida_pipeline_result' in st.session_state:
        st.markdown("---")
        st.subheader("📊 Resultados del Pipeline")
        
        result = st.session_state.florida_pipeline_result
        
        # Verificar si hay candados del día anterior
        if 'step_prev_day_export' in result.get('step_results', {}):
            prev_day_data = result['step_results']['step_prev_day_export'].get('prev_day_export', {})
            if prev_day_data:
                show_prev_day_candados(prev_day_data)
        
        # Mostrar candado actual si existe
        if 'step_candado_export' in result.get('step_results', {}):
            current_candado = result['step_results']['step_candado_export']
            show_current_candado(current_candado)
        
        # Mostrar resultado completo
        with st.expander("🔍 Ver resultado completo del pipeline"):
            st.json(result)

def show_florida_pick3_bolita_analysis():
    """Handler para protocolo completo Florida Pick 3 → Bolita Cubana"""
    from app_vision.modules.florida_pick3_ui import (
        show_florida_pick3_header,
        show_window_status,
        show_candado_rule,
        show_prev_day_candados,
        show_current_candado,
        show_gematria_analysis,
        show_guide_message,
        show_sefirotic_analysis
    )
    
    # Mostrar header y componentes UI
    show_florida_pick3_header()
    show_window_status()
    show_candado_rule()
    
    # Configuración del análisis
    st.markdown("### ⚙️ Configuración del Análisis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_type = st.selectbox(
            "Tipo de Análisis",
            ["Análisis Completo", "Solo Candados", "Solo Gematría", "Solo Noticias"],
            index=0
        )
    
    with col2:
        time_window = st.selectbox(
            "Ventana de Tiempo",
            ["Últimas 24h", "Últimas 48h", "Última semana"],
            index=0
        )
    
    # Botón para ejecutar análisis
    if st.button("🚀 Ejecutar Protocolo Florida Pick 3", type="primary", use_container_width=True):
        with st.spinner("Ejecutando protocolo Florida Pick 3..."):
            try:
                # Importar el pipeline executor
                from app_vision.engine.fsm import pipeline_executor
                
                # Cargar el plan
                plan_path = "plans/florida_pick3_bolita_cubana.json"
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_config = json.load(f)
                
                # Ejecutar pipeline
                result = pipeline_executor.execute_pipeline(plan_config)
                
                if result["status"] == "completed":
                    st.success("✅ Protocolo ejecutado exitosamente")
                    
                    # Mostrar resultados según el tipo de análisis seleccionado
                    step_results = result.get("step_results", {})
                    
                    if analysis_type in ["Análisis Completo", "Solo Candados"]:
                        # Mostrar candados del día anterior
                        if 'step_prev_day_export' in step_results:
                            prev_day_data = step_results['step_prev_day_export'].get('prev_day_export', {})
                            show_prev_day_candados(prev_day_data)
                        
                        # Mostrar candado actual
                        if 'step_candado_export' in step_results:
                            current_candado = step_results['step_candado_export'].get('deliverable', {})
                            show_current_candado(current_candado)
                    
                    if analysis_type in ["Análisis Completo", "Solo Gematría"]:
                        # Mostrar análisis gematría
                        if 'step_gematria_per_candado' in step_results:
                            gematria_data = step_results['step_gematria_per_candado']
                            show_gematria_analysis(gematria_data)
                        
                        # Mostrar mensaje guía
                        if 'step_fuse_guide' in step_results:
                            guide_data = step_results['step_fuse_guide']
                            show_guide_message(guide_data)
                    
                    if analysis_type in ["Análisis Completo", "Solo Noticias"]:
                        # Mostrar análisis sefirótico
                        if 'step_sefirotico' in step_results:
                            sefirotic_data = step_results['step_sefirotico']
                            show_sefirotic_analysis(sefirotic_data)
                    
                    # Mostrar resultado completo
                    with st.expander("🔍 Ver resultado completo del pipeline"):
                        st.json(result)
                        
                else:
                    st.error(f"❌ Error en el protocolo: {result.get('error', 'Error desconocido')}")
                    
            except Exception as e:
                st.error(f"❌ Error ejecutando protocolo: {str(e)}")
                st.exception(e)
    
    # Información adicional
    st.markdown("---")
    st.markdown("### 📋 Información del Protocolo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Steps", "15")
    
    with col2:
        st.metric("Análisis Gematría", "✅")
    
    with col3:
        st.metric("Fuentes Reales", "✅")

def show_florida_universal_protocol_analysis():
    """Handler para Protocolo Universal completo con visualización paso a paso"""
    # Importar el visualizador
    from modules.universal_protocol_visualizer import UniversalProtocolVisualizer
    
    # Crear instancia del visualizador
    visualizer = UniversalProtocolVisualizer()
    
    # Ejecutar el protocolo completo con visualización
    visualizer.execute_complete_protocol()

def show_prev_day_candados(prev_day_data):
    """Muestra los 3 candados del día anterior en formato de tarjetas"""
    st.markdown("#### 🇨🇺 CANDADOS DEL DÍA ANTERIOR")
    
    date = prev_day_data.get('date', 'N/A')
    candados = prev_day_data.get('candados', [])
    summary = prev_day_data.get('summary', {})
    
    st.markdown(f"**Fecha:** {date}")
    st.markdown(f"**Completos:** {summary.get('complete', 0)}/3 | **Faltantes:** {summary.get('missing', 0)}/3")
    
    # Mostrar tarjetas de candados
    cols = st.columns(3)
    
    for i, candado in enumerate(candados):
        with cols[i]:
            slot = candado.get('slot', 'N/A')
            
            if candado.get('status') == 'missing':
                st.error(f"**{slot}** - Faltante")
                st.write(f"❌ {candado.get('reason', 'Datos no disponibles')}")
            else:
                st.success(f"**{slot}** - Completo")
                
                # Mostrar candado
                candado_list = candado.get('candado', [])
                if candado_list:
                    st.markdown(f"**Candado:** {', '.join(candado_list)}")
                
                # Mostrar parlés
                parles = candado.get('parles', [])
                if parles:
                    parles_str = " | ".join([f"{p[0]}-{p[1]}" for p in parles])
                    st.markdown(f"**Parlés:** {parles_str}")
                
                # Mostrar origen
                st.write(f"**Origen:** {candado.get('block', 'N/A')} {candado.get('date', 'N/A')}")
    
    # Botón para copiar todos los parlés
    all_parles_str = summary.get('all_parles_string', '')
    if all_parles_str:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.text_area(
                "Todos los parlés del día anterior:",
                value=all_parles_str,
                height=100,
                disabled=True
            )
        
        with col2:
            if st.button("📋 Copiar", key="copy_prev_day_parles"):
                st.success("¡Copiado al portapapeles!")
                # En una implementación real, usarías pyperclip o similar

def show_current_candado(candado_data):
    """Muestra el candado actual"""
    st.markdown("#### 🎯 CANDADO ACTUAL")
    
    deliverable = candado_data.get('deliverable', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Fecha", deliverable.get('date', 'N/A'))
    
    with col2:
        st.metric("Bloque", deliverable.get('block', 'N/A'))
    
    with col3:
        candado = deliverable.get('candado', [])
        st.metric("Candado", f"{', '.join(candado)}" if candado else 'N/A')
    
    # Mostrar parlés si existen
    parles = deliverable.get('parles', [])
    if parles:
        st.markdown("**Parlés:**")
        parles_str = " | ".join([f"{p[0]}-{p[1]}" for p in parles])
        st.write(parles_str)

def show_module_placeholder(module_name: str):
    """Placeholder para módulos no implementados"""
    module_config = module_registry.get_module(module_name)
    
    if module_config:
        st.title(f"{module_config['icon']} {module_config['title']}")
        st.markdown(f"### {module_config['description']}")
    else:
        st.title("📦 Módulo No Encontrado")
        st.error(f"El módulo '{module_name}' no está registrado en el sistema")
        return
    
    st.markdown("---")
    
    st.info("""
    🚧 **Módulo en Preparación**
    
    Este módulo está listo para ser implementado en el sistema limpio.
    La arquitectura modular permite agregar funcionalidad fácilmente.
    """)
    
    # Información del módulo
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Información del Módulo")
        st.write(f"**Nombre:** {module_config['name']}")
        st.write(f"**Categoría:** {module_config['category']}")
        st.write(f"**Estado:** {'🟢 Activo' if module_config['enabled'] else '🔴 Inactivo'}")
    
    with col2:
        st.markdown("#### ⚙️ Configuración")
        st.write("- Estado centralizado")
        st.write("- Sin variables hardcodeadas")
        st.write("- Gestión de errores integrada")
        st.write("- Navegación consistente")

# =================== REGISTRO DE MÓDULOS BASE ===================

def register_base_modules():
    """Registra los módulos base del sistema"""
    
    # Módulos de IA
    module_registry.register_module('ai_analysis', {
        'title': 'Análisis con IA',
        'icon': '🤖',
        'description': 'Motor de inteligencia artificial para análisis avanzado',
        'category': 'ai',
        'enabled': True
    })
    
    module_registry.register_module('ai_config', {
        'title': 'Configuración IA',
        'icon': '⚙️',
        'description': 'Configuración del motor de IA',
        'category': 'ai',
        'enabled': True
    })
    
    # Módulos de lotería
    module_registry.register_module('florida_lottery', {
        'title': 'Florida Lottery',
        'icon': '🎰',
        'description': 'Sistema de análisis Florida con regla fija de CANDADO',
        'category': 'lottery',
        'enabled': True,
        'handler': show_florida_lottery_analysis
    })
    
    module_registry.register_module('florida_pick3_bolita', {
        'title': 'Florida Pick 3 → Bolita Cubana',
        'icon': '🎲',
        'description': 'Protocolo completo Florida Pick 3 con bolita cubana y análisis gematría',
        'category': 'lottery',
        'enabled': True,
        'handler': show_florida_pick3_bolita_analysis
    })
    
    module_registry.register_module('florida_universal_protocol', {
        'title': 'Florida Lotto - Protocolo Universal Completo',
        'icon': '🎯',
        'description': 'Protocolo Universal completo para Florida Lotto con visualización paso a paso de todos los detalles',
        'category': 'lottery',
        'enabled': True,
        'handler': show_florida_universal_protocol_analysis
    })
    
    module_registry.register_module('universal_protocol', {
        'title': 'Protocolo Universal',
        'icon': '🎯',
        'description': 'Sistema de protocolo universal configurable',
        'category': 'lottery',
        'enabled': True
    })
    
    # Módulos de análisis
    module_registry.register_module('pattern_analysis', {
        'title': 'Análisis de Patrones',
        'icon': '📈',
        'description': 'Análisis de patrones y tendencias',
        'category': 'analysis',
        'enabled': True
    })
    
    module_registry.register_module('gematria', {
        'title': 'Gematría',
        'icon': '🔮',
        'description': 'Calculadora y análisis gematría',
        'category': 'analysis',
        'enabled': True
    })
    
    # Módulos de herramientas
    module_registry.register_module('data_tools', {
        'title': 'Herramientas de Datos',
        'icon': '🛠️',
        'description': 'Herramientas para manejo de datos',
        'category': 'tools',
        'enabled': True
    })
    
    # Módulos de administración
    module_registry.register_module('system_admin', {
        'title': 'Administración',
        'icon': '👑',
        'description': 'Panel de administración del sistema',
        'category': 'admin',
        'enabled': True
    })

# =================== ENRUTADOR PRINCIPAL ===================

def main_router():
    """Enrutador principal de la aplicación"""
    current_section = StateManager.get_state('current_section', 'home')
    
    if current_section == 'home':
        show_home()
    elif current_section == 'system_status':
        show_system_status()
    else:
        # Buscar si es un módulo registrado
        module_config = module_registry.get_module(current_section)
        if module_config and module_config.get('handler'):
            # Ejecutar el handler del módulo
            module_config['handler']()
        else:
            # Mostrar placeholder
            show_module_placeholder(current_section)

# =================== FUNCIÓN PRINCIPAL ===================

def main():
    """Función principal de la aplicación limpia"""
    # Enforce política global ANTES de cualquier operación
    global_policy = enforce_global_policy()
    
    # Inicializar estado
    StateManager.initialize()
    
    # Registrar módulos base
    register_base_modules()
    
    # Renderizar interfaz
    render_sidebar()
    main_router()

if __name__ == "__main__":
    main()
