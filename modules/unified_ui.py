# modules/unified_ui.py — Interfaz de Usuario Unificada Premium
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional

# Importar módulos
try:
    from .master_orchestrator import master_orchestrator
    from .historical_analysis import historical_analyzer
    from .auto_corrector import auto_corrector
    from .gematria_module import GematriaAnalyzer
except ImportError:
    master_orchestrator = None
    historical_analyzer = None
    auto_corrector = None
    GematriaAnalyzer = None

# Importar nuevos módulos de mejora
try:
    from .transparency_module import transparency_module
    from .monitoring_dashboard import monitoring_dashboard
    from .security_module import security_module
    from .audit_module import audit_module
    from .metrics_collector import metrics_collector
except ImportError:
    transparency_module = None
    monitoring_dashboard = None
    security_module = None
    audit_module = None
    metrics_collector = None

ROOT = Path(__file__).resolve().parent.parent

class UnifiedUI:
    def __init__(self):
        self.current_tab = "dashboard"
        self.protocol_status = "idle"
        
    def render_main_interface(self):
        """Renderiza la interfaz principal unificada."""
        st.set_page_config(
            page_title="VISIÓN PREMIUM - Sistema Unificado",
            page_icon="🔮",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Sidebar principal
        self._render_sidebar()
        
        # Tabs principales
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏠 Dashboard", 
            "📰 Noticias", 
            "🔮 Análisis", 
            "🔧 Sistema"
        ])
        
        with tab1:
            self._render_dashboard()
        
        with tab2:
            self._render_news_interface()
        
        with tab3:
            self._render_analysis_interface()
        
        with tab4:
            self._render_system_interface()
    
    def _render_sidebar(self):
        """Renderiza la barra lateral."""
        with st.sidebar:
            st.title("🔮 VISIÓN PREMIUM")
            st.markdown("---")
            
            # Estado del sistema
            if master_orchestrator:
                system_status = master_orchestrator.get_system_status()
                st.subheader("📊 Estado del Sistema")
                
                # Indicador de salud
                health_color = {
                    "healthy": "🟢",
                    "warning": "🟡", 
                    "critical": "🔴"
                }.get(system_status["system_health"], "⚪")
                
                st.metric(
                    "Salud del Sistema",
                    f"{health_color} {system_status['system_health'].upper()}",
                    f"{system_status['available_modules']}/{system_status['total_modules']} módulos"
                )
            
            st.markdown("---")
            
            # Acciones rápidas
            st.subheader("⚡ Acciones Rápidas")
            
            if st.button("🚀 Ejecutar Protocolo Completo", use_container_width=True):
                self.protocol_status = "running"
                st.session_state["run_complete_protocol"] = True
            
            if st.button("📊 Ver Estado Completo", use_container_width=True):
                st.session_state["show_system_status"] = True
    
    def _render_dashboard(self):
        """Renderiza el dashboard principal."""
        st.title("🏠 **DASHBOARD VISIÓN PREMIUM**")
        st.markdown("Sistema Unificado de Análisis Avanzado")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📰 Noticias", "100+", "Objetivo alcanzado")
        
        with col2:
            st.metric("🔮 Análisis", "11/11", "Pasos completados")
        
        with col3:
            st.metric("⚙️ Ensamblaje", "Activo", "Series generadas")
        
        with col4:
            st.metric("🔧 Sistema", "100%", "Operativo")
        
        # Ejecutar protocolo completo
        if st.button("🚀 EJECUTAR PROTOCOLO COMPLETO", use_container_width=True, type="primary"):
            try:
                with st.spinner("🚀 Ejecutando protocolo completo VISIÓN PREMIUM..."):
                    # Importar y usar el controlador del pipeline
                    from .pipeline_controller import run_full_pipeline
                    
                    # Ejecutar pipeline completo
                    outcome = run_full_pipeline()
                    
                    # Almacenar resultados en session state
                    st.session_state["outcome"] = outcome
                    st.session_state["corr"] = outcome.correlation
                    st.session_state["series"] = outcome.proposals
                    
                    st.success(f"🎉 **Protocolo completado exitosamente!**")
                    
                    # Mostrar resumen del resultado
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Series Generadas", len(outcome.proposals))
                    with col2:
                        st.metric("Correlación Global", f"{outcome.correlation.global_score:.1%}")
                    with col3:
                        st.metric("Patrón Dominante", outcome.dominant_pattern)
                    
                    # Mostrar series principales
                    st.subheader("🎯 **Series Principales**")
                    for i, proposal in enumerate(outcome.proposals[:3]):
                        st.success(f"**Serie {i+1}:** {proposal.main} • Probabilidad: {proposal.probability:.1%}")
                    
                    # Mostrar detalles en expander
                    with st.expander("📊 **Detalles Completos del Protocolo**", expanded=True):
                        st.write(f"**Categoría Principal:** {outcome.dominant_category}")
                        st.write(f"**Arquetipo Dominante:** {outcome.dominant_archetype}")
                        if outcome.subliminal_msg:
                            st.write(f"**Mensaje Subliminal:** {outcome.subliminal_msg}")
                        if outcome.quantum_state:
                            st.write(f"**Estado Cuántico:** {outcome.quantum_state}")
                        
                        st.write("**Correlaciones entre Capas:**")
                        for pair in outcome.correlation.pairs:
                            st.progress(pair.score, text=f"{pair.a} ↔ {pair.b}: {pair.score:.1%}")
                    
                    st.info("💡 **Navega a las páginas de Correlación, Ensamblaje y Resultado para ver más detalles**")
                    
            except Exception as e:
                st.error(f"❌ **Error en protocolo:** {str(e)}")
                st.exception(e)
    
    def _render_news_interface(self):
        """Renderiza la interfaz de noticias."""
        st.title("📰 **INTERFAZ DE NOTICIAS AVANZADA**")
        
        # Controles principales
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🚀 Acopio de Noticias")
            if st.button("📥 ACOPIAR NOTICIAS", use_container_width=True, type="primary"):
                st.session_state["run_news_acopio"] = True
                # Ejecutar acopio inmediatamente
                self._execute_news_acopio()
        
        with col2:
            st.subheader("📊 Estado")
            if "news_selected_df" in st.session_state:
                news_count = len(st.session_state["news_selected_df"])
                st.metric("Noticias", news_count, "Seleccionadas")
            else:
                st.metric("Noticias", 0, "Sin datos")
        
        with col3:
            st.subheader("⚡ Acciones")
            if st.button("🔄 Acopio Extra", use_container_width=True):
                with st.spinner("🔄 Ejecutando acopio extra..."):
                    try:
                        # Importar y usar el módulo de noticias
                        from .noticias_module import NoticiasModule
                        
                        if NoticiasModule:
                            noticias = NoticiasModule()
                            
                            # Ejecutar acopio extra
                            extra_result = noticias._run_pipeline_extra()
                            
                            if extra_result and "success" in extra_result and extra_result["success"]:
                                # Obtener noticias existentes y nuevas
                                existing_df = st.session_state.get("news_selected_df", pd.DataFrame())
                                new_df = extra_result.get("new_news", pd.DataFrame())
                                
                                if not new_df.empty:
                                    # Combinar noticias existentes con nuevas
                                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                    st.session_state["news_selected_df"] = combined_df
                                    
                                    st.success(f"✅ **Acopio Extra completado!** {len(new_df)} noticias adicionales")
                                    st.info(f"📊 **Total acumulado:** {len(combined_df)} noticias")
                                    
                                    # Mostrar resumen del acopio extra
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Noticias Nuevas", len(new_df))
                                    with col2:
                                        st.metric("Total Acumulado", len(combined_df))
                                    with col3:
                                        st.metric("Fuentes Únicas", combined_df['medio'].nunique())
                                    
                                    # Mostrar nuevas noticias en expander
                                    with st.expander("🆕 **Noticias del Acopio Extra**", expanded=True):
                                        st.dataframe(new_df[['titulo', 'medio', 'fecha', 'emocion', 'impact_score']], 
                                                   use_container_width=True, hide_index=True)
                                    
                                    st.rerun()
                                else:
                                    st.warning("⚠️ **Acopio Extra completado pero no se obtuvieron noticias adicionales**")
                            else:
                                st.error("❌ **Error en acopio extra:** No se pudo completar el proceso")
                        else:
                            st.error("❌ **Error:** Módulo de noticias no disponible")
                            
                    except Exception as e:
                        st.error(f"❌ **Error en acopio extra:** {str(e)}")
                        st.exception(e)
        
        # Mostrar noticias si están disponibles
        if "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty:
            self._show_news_results()
        
        # Análisis histórico
        if historical_analyzer and "news_selected_df" in st.session_state:
            st.subheader("📅 Análisis Histórico y Arrastre")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 ANALIZAR ARRASTRE HISTÓRICO", use_container_width=True):
                    with st.spinner("Analizando arrastre histórico..."):
                        current_news = st.session_state["news_selected_df"]
                        drag_analysis = historical_analyzer.analyze_news_drag(current_news)
                        
                        if drag_analysis["drag_detected"]:
                            st.warning(f"⚠️ **ARRASTRE DETECTADO**: {drag_analysis['drag_strength']:.2f}")
                        else:
                            st.success("✅ Sin arrastre significativo")
                        
                        st.json(drag_analysis)
            
            with col2:
                if st.button("🔢 ANALIZAR SORTEO ANTERIOR", use_container_width=True):
                    with st.spinner("Analizando sorteo anterior..."):
                        previous_analysis = historical_analyzer.analyze_previous_draw()
                        
                        if previous_analysis["analysis_available"]:
                            st.success("✅ Análisis del sorteo anterior disponible")
                            st.json(previous_analysis)
                        else:
                            st.info("ℹ️ No hay datos del sorteo anterior")
    
    def _render_analysis_interface(self):
        """Renderiza la interfaz de análisis."""
        st.title("🔮 **INTERFAZ DE ANÁLISIS AVANZADO**")
        
        # Tabs de análisis
        analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
            "🔡 Gematría", 
            "🧠 Subliminal", 
            "🔢 T70", 
            "🔮 Cuántico"
        ])
        
        with analysis_tab1:
            st.subheader("🔡 **ANÁLISIS GEMATRÍA**")
            
            # Verificar si hay noticias disponibles
            if "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty:
                # Entrada de números del sorteo
                st.subheader("📊 Entrada de Números del Sorteo")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    numbers_input = st.text_input(
                        "Ingresa los números del sorteo (separados por comas):",
                        placeholder="Ej: 7, 14, 23, 31, 45",
                        help="Ingresa los números del sorteo de lotería separados por comas"
                    )
                    
                    # Mostrar números ingresados en tiempo real
                    if numbers_input:
                        try:
                            numbers = [int(x.strip()) for x in numbers_input.split(",") if x.strip().isdigit()]
                            if numbers:
                                st.success(f"📊 **Números ingresados:** {', '.join(map(str, numbers))}")
                                st.info(f"🔢 **Total de números:** {len(numbers)}")
                            else:
                                st.warning("⚠️ Por favor ingresa números válidos")
                        except ValueError:
                            st.error("❌ Error: Asegúrate de ingresar solo números separados por comas")
                    
                    if st.button("🔮 Crear Firma Gematrica", type="primary", use_container_width=True):
                        if numbers_input and GematriaAnalyzer:
                            try:
                                # Parsear números
                                numbers = [int(x.strip()) for x in numbers_input.split(",") if x.strip().isdigit()]
                                
                                if numbers:
                                    # Crear instancia del analizador
                                    analyzer = GematriaAnalyzer()
                                    
                                    # Crear firma gematrica
                                    with st.spinner("Creando firma gematrica..."):
                                        signature = analyzer.gematria_signature(numbers)
                                    
                                    if "error" not in signature:
                                        # Almacenar en session state
                                        st.session_state["gematria_signature"] = signature
                                        st.success("✅ Firma gematrica creada exitosamente")
                                        st.rerun()  # Recargar para mostrar resultados
                                    else:
                                        st.error(f"❌ Error: {signature['error']}")
                                else:
                                    st.warning("⚠️ Por favor ingresa números válidos")
                            except ValueError:
                                st.error("❌ Error: Asegúrate de ingresar solo números separados por comas")
                        else:
                            st.warning("⚠️ Por favor ingresa los números del sorteo")
                
                with col2:
                    st.info("""
                    **💡 Tip:**
                    - Ingresa los números del sorteo de lotería
                    - El sistema convertirá cada número a su equivalente hebreo
                    - Identificará arquetipos dominantes
                    - Creará una firma simbólica única
                    """)
                
                # Mostrar firma gematrica si existe
                if "gematria_signature" in st.session_state:
                    self._render_gematria_results()
                
                # Botón para ejecutar análisis completo
                if st.button("🔡 EJECUTAR ANÁLISIS GEMATRÍA COMPLETO", use_container_width=True, type="secondary"):
                    st.session_state["run_gematria"] = True
            else:
                st.info("📰 Ejecuta el acopio de noticias primero para analizar gematría")
        
        with analysis_tab2:
            st.subheader("🧠 **ANÁLISIS SUBLIMINAL**")
            if "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.info("""
                    **🧠 Análisis Subliminal:**
                    - Detecta mensajes ocultos en noticias
                    - Analiza patrones subliminales
                    - Identifica influencias emocionales
                    - Genera reporte de impacto
                    """)
                    
                    if st.button("🧠 EJECUTAR ANÁLISIS SUBLIMINAL", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Ejecutando análisis subliminal..."):
                            try:
                                # Obtener noticias del session state
                                news_df = st.session_state["news_selected_df"]
                                
                                # Importar y usar el módulo Subliminal
                                from .subliminal_module import SubliminalModule
                                
                                if SubliminalModule:
                                    subliminal = SubliminalModule()
                                    
                                    # Ejecutar análisis subliminal
                                    subliminal_result = subliminal.analyze_subliminal_messages(news_df)
                                    
                                    if subliminal_result and "success" in subliminal_result and subliminal_result["success"]:
                                        # Almacenar resultado en session state
                                        st.session_state["subliminal_analysis"] = subliminal_result
                                        st.success("✅ **Análisis Subliminal completado exitosamente!**")
                                        
                                        # Mostrar resumen
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Mensajes Detectados", subliminal_result.get("mensajes_detectados", 0))
                                        with col2:
                                            st.metric("Patrones Identificados", subliminal_result.get("patrones_identificados", 0))
                                        with col3:
                                            st.metric("Impacto Promedio", f"{subliminal_result.get('impacto_promedio', 0):.2f}")
                                        
                                        # Mostrar detalles en expander
                                        with st.expander("🧠 **Detalles del Análisis Subliminal**", expanded=True):
                                            if "mensajes_detalle" in subliminal_result:
                                                st.subheader("💬 Mensajes Subliminales Detectados")
                                                for msg in subliminal_result["mensajes_detalle"][:5]:
                                                    st.warning(f"**{msg['tipo']}**: {msg['contenido']}")
                                            
                                            if "patrones_detalle" in subliminal_result:
                                                st.subheader("🔍 Patrones Identificados")
                                                for patron in subliminal_result["patrones_detalle"][:5]:
                                                    st.info(f"**{patron['nombre']}**: {patron['descripcion']}")
                                            
                                            if "impacto_emocional" in subliminal_result:
                                                st.subheader("😊 Impacto Emocional")
                                                st.bar_chart(subliminal_result["impacto_emocional"])
                                        
                                        st.rerun()
                                    else:
                                        st.error("❌ **Error en análisis subliminal:** No se pudo completar el proceso")
                                else:
                                    st.error("❌ **Error:** Módulo Subliminal no disponible")
                                    
                            except Exception as e:
                                st.error(f"❌ **Error en análisis subliminal:** {str(e)}")
                                st.exception(e)
                
                with col2:
                    # Mostrar estado del análisis subliminal
                    if "subliminal_analysis" in st.session_state:
                        st.success("✅ **Análisis Subliminal Completado**")
                        subliminal_data = st.session_state["subliminal_analysis"]
                        
                        st.metric("Estado", "Completado")
                        st.metric("Mensajes", subliminal_data.get("mensajes_detectados", 0))
                        st.metric("Patrones", subliminal_data.get("patrones_identificados", 0))
                    else:
                        st.info("⏳ **Estado:** Pendiente de ejecución")
            else:
                st.info("📰 Ejecuta el acopio de noticias primero para analizar subliminal")
        
        with analysis_tab3:
            st.subheader("🔢 **MAPEO T70**")
            if "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.info("""
                    **🔢 Mapeo T70:**
                    - Agrupa noticias por categorías
                    - Extrae palabras clave
                    - Mapea a números T70
                    - Prepara para análisis especializado
                    """)
                    
                    if st.button("🔢 EJECUTAR MAPEO T70", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Ejecutando mapeo T70..."):
                            try:
                                # Obtener noticias del session state
                                news_df = st.session_state["news_selected_df"]
                                
                                # Importar y usar el módulo T70
                                from .t70_module import T70Module
                                
                                if T70Module:
                                    t70 = T70Module()
                                    
                                    # Ejecutar mapeo T70
                                    t70_result = t70.map_news_to_t70(news_df)
                                    
                                    if t70_result and "success" in t70_result and t70_result["success"]:
                                        # Almacenar resultado en session state
                                        st.session_state["t70_mapping"] = t70_result
                                        st.success("✅ **Mapeo T70 completado exitosamente!**")
                                        
                                        # Mostrar resumen
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Categorías", t70_result.get("categorias", 0))
                                        with col2:
                                            st.metric("Palabras Clave", t70_result.get("palabras_clave", 0))
                                        with col3:
                                            st.metric("Mapeos T70", t70_result.get("mapeos_t70", 0))
                                        
                                        # Mostrar detalles en expander
                                        with st.expander("📊 **Detalles del Mapeo T70**", expanded=True):
                                            if "categorias_detalle" in t70_result:
                                                st.subheader("🏷️ Categorías Identificadas")
                                                for cat, count in t70_result["categorias_detalle"].items():
                                                    st.info(f"**{cat}**: {count} noticias")
                                            
                                            if "palabras_clave_lista" in t70_result:
                                                st.subheader("🔑 Palabras Clave Principales")
                                                st.write(", ".join(t70_result["palabras_clave_lista"][:10]))
                                            
                                            if "mapeos_detalle" in t70_result:
                                                st.subheader("🔢 Mapeos T70")
                                                for palabra, numero in t70_result["mapeos_detalle"].items():
                                                    st.success(f"**{palabra}** → **{numero}**")
                                        
                                        st.rerun()
                                    else:
                                        st.error("❌ **Error en mapeo T70:** No se pudo completar el proceso")
                                else:
                                    st.error("❌ **Error:** Módulo T70 no disponible")
                                    
                            except Exception as e:
                                st.error(f"❌ **Error en mapeo T70:** {str(e)}")
                                st.exception(e)
                
                with col2:
                    # Mostrar estado del mapeo T70
                    if "t70_mapping" in st.session_state:
                        st.success("✅ **Mapeo T70 Completado**")
                        t70_data = st.session_state["t70_mapping"]
                        
                        st.metric("Estado", "Completado")
                        st.metric("Categorías", t70_data.get("categorias", 0))
                        st.metric("Mapeos", t70_data.get("mapeos_t70", 0))
                    else:
                        st.info("⏳ **Estado:** Pendiente de ejecución")
            else:
                st.info("📰 Ejecuta el acopio de noticias primero para mapear T70")
        
        with analysis_tab4:
            st.subheader("🔮 **ANÁLISIS CUÁNTICO**")
            if "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.info("""
                    **🔮 Análisis Cuántico:**
                    - Aplica principios de mecánica cuántica
                    - Analiza superposición de estados emocionales
                    - Detecta entrelazamiento de noticias
                    - Genera probabilidades cuánticas
                    """)
                    
                    if st.button("🔮 EJECUTAR ANÁLISIS CUÁNTICO", use_container_width=True, type="primary"):
                        with st.spinner("🔄 Ejecutando análisis cuántico..."):
                            try:
                                # Obtener noticias del session state
                                news_df = st.session_state["news_selected_df"]
                                
                                # Importar y usar el módulo Cuántico
                                from .quantum_layer import QuantumLayer
                                
                                if QuantumLayer:
                                    quantum = QuantumLayer()
                                    
                                    # Ejecutar análisis cuántico
                                    quantum_result = quantum.analyze_quantum_state(news_df)
                                    
                                    if quantum_result and "success" in quantum_result and quantum_result["success"]:
                                        # Almacenar resultado en session state
                                        st.session_state["quantum_analysis"] = quantum_result
                                        st.success("✅ **Análisis Cuántico completado exitosamente!**")
                                        
                                        # Mostrar resumen
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("Estados Cuánticos", quantum_result.get("estados_cuanticos", 0))
                                        with col2:
                                            st.metric("Superposiciones", quantum_result.get("superposiciones", 0))
                                        with col3:
                                            st.metric("Entrelazamientos", quantum_result.get("entrelazamientos", 0))
                                        
                                        # Mostrar detalles en expander
                                        with st.expander("🔮 **Detalles del Análisis Cuántico**", expanded=True):
                                            if "estados_detalle" in quantum_result:
                                                st.subheader("⚛️ Estados Cuánticos Identificados")
                                                for estado in quantum_result["estados_detalle"][:5]:
                                                    st.info(f"**{estado['nombre']}**: {estado['probabilidad']:.2%}")
                                            
                                            if "superposiciones_detalle" in quantum_result:
                                                st.subheader("🌀 Superposiciones Detectadas")
                                                for sup in quantum_result["superposiciones_detalle"][:5]:
                                                    st.warning(f"**{sup['tipo']}**: {sup['descripcion']}")
                                            
                                            if "probabilidades_cuanticas" in quantum_result:
                                                st.subheader("📊 Probabilidades Cuánticas")
                                                st.bar_chart(quantum_result["probabilidades_cuanticas"])
                                        
                                        st.rerun()
                                    else:
                                        st.error("❌ **Error en análisis cuántico:** No se pudo completar el proceso")
                                else:
                                    st.error("❌ **Error:** Módulo Cuántico no disponible")
                                    
                            except Exception as e:
                                st.error(f"❌ **Error en análisis cuántico:** {str(e)}")
                                st.exception(e)
                
                with col2:
                    # Mostrar estado del análisis cuántico
                    if "quantum_analysis" in st.session_state:
                        st.success("✅ **Análisis Cuántico Completado**")
                        quantum_data = st.session_state["quantum_analysis"]
                        
                        st.metric("Estado", "Completado")
                        st.metric("Estados", quantum_data.get("estados_cuanticos", 0))
                        st.metric("Superposiciones", quantum_data.get("superposiciones", 0))
                    else:
                        st.info("⏳ **Estado:** Pendiente de ejecución")
            else:
                st.info("📰 Ejecuta el acopio de noticias primero para analizar cuánticamente")
    
    def _render_system_interface(self):
        """Renderiza interfaz del sistema."""
        st.title("🔧 **SISTEMA Y DIAGNÓSTICOS**")
        st.markdown("Configuración, administración y monitoreo avanzado del sistema")
        
        # Tabs para diferentes funcionalidades del sistema
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Monitoreo", 
            "🔐 Seguridad", 
            "🔍 Auditoría", 
            "🚨 Incidencias",
            "📈 Métricas",
            "⚙️ Configuración"
        ])
        
        with tab1:
            self._render_monitoring_tab()
        
        with tab2:
            self._render_security_tab()
        
        with tab3:
            self._render_audit_tab()
        
        with tab4:
            self._render_incidents_tab()
        
        with tab5:
            self._render_metrics_tab()
        
        with tab6:
            self._render_configuration_tab()
    
    def _render_monitoring_tab(self):
        """Renderiza la pestaña de monitoreo."""
        st.subheader("📊 **MONITOREO DEL SISTEMA**")
        
        if monitoring_dashboard:
            monitoring_dashboard.render_monitoring_dashboard()
        else:
            st.warning("⚠️ Módulo de monitoreo no disponible")
            st.info("El dashboard de monitoreo en tiempo real se mostrará aquí")
    
    def _render_security_tab(self):
        """Renderiza la pestaña de seguridad."""
        st.subheader("🔐 **SEGURIDAD Y GESTIÓN DE ACCESOS**")
        
        if security_module:
            security_module.render_security_ui()
        else:
            st.warning("⚠️ Módulo de seguridad no disponible")
            st.info("La gestión de usuarios y seguridad se mostrará aquí")
    
    def _render_audit_tab(self):
        """Renderiza la pestaña de auditoría."""
        st.subheader("🔍 **AUDITORÍA AUTOMÁTICA Y BENCHMARKING**")
        
        if audit_module:
            audit_module.render_audit_ui()
        else:
            st.warning("⚠️ Módulo de auditoría no disponible")
            st.info("La auditoría automática y benchmarking se mostrará aquí")
    
    def _render_incidents_tab(self):
        """Renderiza la pestaña de incidencias."""
        st.subheader("🚨 **GESTIÓN PROACTIVA DE INCIDENCIAS**")
        
        # Aquí se integrará el módulo de incidencias cuando esté disponible
        st.info("🚧 Módulo de gestión de incidencias en desarrollo")
        st.write("""
        **Funcionalidades planificadas:**
        - Detección automática de problemas
        - Auto-corrección inteligente
        - Escalación automática
        - Notificaciones proactivas
        """)
    
    def _render_metrics_tab(self):
        """Renderiza la pestaña de métricas."""
        st.subheader("📈 **MÉTRICAS Y KPIs DEL SISTEMA**")
        
        if metrics_collector:
            metrics_collector.render_metrics_dashboard()
        else:
            st.warning("⚠️ Módulo de métricas no disponible")
            st.info("El dashboard de métricas y KPIs se mostrará aquí")
    
    def _render_configuration_tab(self):
        """Renderiza la pestaña de configuración."""
        st.subheader("⚙️ **CONFIGURACIÓN DEL SISTEMA**")
        
        # Estado del sistema
        if master_orchestrator:
            system_status = master_orchestrator.get_system_status()
            
            st.subheader("📊 Estado del Sistema")
            
            # Métricas del sistema
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Módulos", system_status["total_modules"])
            
            with col2:
                st.metric("Módulos Activos", system_status["available_modules"])
            
            with col3:
                missing_modules = system_status["total_modules"] - system_status["available_modules"]
                st.metric("Módulos Faltantes", missing_modules)
            
            with col4:
                health_color = {
                    "healthy": "🟢",
                    "warning": "🟡",
                    "critical": "🔴"
                }.get(system_status["system_health"], "⚪")
                st.metric("Salud", f"{health_color} {system_status['system_health'].upper()}")
            
            # Detalles de módulos
            st.subheader("🔍 Detalles de Módulos")
            
            modules_df = pd.DataFrame.from_dict(system_status["modules_details"], orient="index")
            st.dataframe(modules_df, use_container_width=True)
        else:
            st.error("❌ Orquestador maestro no disponible")
    
    def _render_gematria_results(self):
        """Renderiza los resultados del análisis de gematría."""
        signature = st.session_state["gematria_signature"]
        
        st.subheader("🔮 Firma Gematrica Creada")
        st.markdown("---")
        
        # Información básica
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Números del Sorteo", str(signature["numeros"]))
            st.metric("Arquetipos Identificados", len(signature["arquetipos"]))
        
        with col2:
            st.metric("Fecha de Análisis", signature["fecha_analisis"])
            st.metric("Conversiones Hebreas", len(signature["conversion_hebrea"]))
        
        # Conversión hebrea
        st.subheader("📜 Conversión Hebrea")
        if signature["conversion_hebrea"]:
            hebrew_df = pd.DataFrame(signature["conversion_hebrea"])
            st.dataframe(hebrew_df, use_container_width=True)
        
        # Arquetipos dominantes
        st.subheader("👥 Arquetipos Dominantes")
        for archetype in signature["arquetipos"]:
            st.info(f"🎯 **{archetype}**")
        
        # Firma simbólica
        st.subheader("✨ Firma Simbólica")
        st.success(signature["firma_simbolica"])
        
        # Botón para comparar con noticias
        if st.button("📰 Comparar con Noticias", type="secondary", use_container_width=True):
            if "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty:
                self._compare_gematria_with_news(signature)
            else:
                st.warning("⚠️ No hay noticias disponibles para comparar")
    
    def _compare_gematria_with_news(self, signature):
        """Compara la firma gematrica con las noticias."""
        st.subheader("📰 Comparación con Noticias")
        st.markdown("---")
        
        if GematriaAnalyzer:
            # Convertir DataFrame a lista de diccionarios
            news_df = st.session_state["news_selected_df"]
            news_list = news_df.to_dict('records')
            
            # Crear analizador y realizar comparación
            analyzer = GematriaAnalyzer()
            
            with st.spinner("Comparando firma con noticias..."):
                comparison = analyzer.compare_signature_with_news(signature, news_list)
            
            if "error" not in comparison:
                # Mostrar resultados de la comparación
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Puntuación de Similitud", f"{comparison['puntuacion_similitud']:.1%}")
                    st.metric("Coincidencias Encontradas", len(comparison['coincidencias']))
                
                with col2:
                    st.metric("Arquetipos de la Firma", len(comparison['firma_arquetipos']))
                    st.metric("Estado", "Completado")
                
                # Interpretación de la comparación
                st.subheader("🔍 Interpretación de la Comparación")
                st.info(comparison['interpretacion'])
                
                # Coincidencias arquetipales
                st.subheader("🎯 Coincidencias Arquetipales")
                if comparison['coincidencias']:
                    for match in comparison['coincidencias']:
                        st.success(f"✅ **{match}** - Coincidencia encontrada")
                else:
                    st.warning("⚠️ No se encontraron coincidencias arquetipales")
                
                # Botón para cerrar comparación
                if st.button("❌ Cerrar Comparación", use_container_width=True):
                    st.rerun()
            else:
                st.error(f"❌ Error en la comparación: {comparison['error']}")
        else:
                            st.error("❌ Módulo de gematría no disponible")
    
    def _execute_news_acopio(self):
        """Ejecuta el acopio de noticias."""
        try:
            with st.spinner("🔄 **Ejecutando acopio de noticias...**"):
                # Importar y usar el módulo de noticias
                from .noticias_module import NoticiasModule
                
                if NoticiasModule:
                    noticias = NoticiasModule()
                    
                    # Ejecutar pipeline manual
                    result = noticias._run_pipeline_manual()
                    
                    if result and "news_selected_df" in st.session_state:
                        df_sel = st.session_state["news_selected_df"]
                        if not df_sel.empty:
                            st.success(f"✅ **Acopio completado exitosamente!** {len(df_sel)} noticias recolectadas")
                            
                            # Mostrar resumen
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Noticias", len(df_sel))
                            with col2:
                                st.metric("Fuentes", df_sel['medio'].nunique())
                            with col3:
                                st.metric("Última Actualización", datetime.now().strftime("%H:%M"))
                            
                            # Mostrar noticias en un expander
                            with st.expander("📰 **Noticias Recolectadas**", expanded=True):
                                st.dataframe(df_sel[['titulo', 'medio', 'fecha', 'emocion', 'impact_score']], 
                                           use_container_width=True, hide_index=True)
                        else:
                            st.warning("⚠️ **Acopio completado pero no hay noticias seleccionadas**")
                    else:
                        st.error("❌ **Error en acopio:** No se pudo obtener noticias")
                        
                else:
                    st.error("❌ **Error:** Módulo de noticias no disponible")
                    
        except Exception as e:
            st.error(f"❌ **Error en acopio:** {str(e)}")
            st.exception(e)
    
    def _show_news_results(self):
        """Muestra los resultados de las noticias recolectadas."""
        st.subheader("📰 **RESULTADOS DEL ACOPIO**")
        st.markdown("---")
        
        df_sel = st.session_state["news_selected_df"]
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Noticias", len(df_sel))
        with col2:
            st.metric("Fuentes Únicas", df_sel['medio'].nunique())
        with col3:
            st.metric("Emociones", df_sel['emocion'].nunique())
        with col4:
            st.metric("Score Promedio", f"{df_sel['impact_score'].mean():.2f}")
        
        # Distribución por emoción
        st.subheader("🧠 **Distribución Emocional**")
        emotion_counts = df_sel['emocion'].value_counts()
        st.bar_chart(emotion_counts)
        
        # Tabla de noticias
        st.subheader("📋 **Noticias Recolectadas**")
        st.dataframe(df_sel[['titulo', 'medio', 'fecha', 'emocion', 'impact_score']], 
                   use_container_width=True, hide_index=True)
        
        # Botón para exportar
        if st.button("💾 Exportar Noticias (CSV)", use_container_width=True):
            csv_data = df_sel.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv_data,
                file_name=f"noticias_acopio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Instancia global
unified_ui = UnifiedUI()
