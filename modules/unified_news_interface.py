# modules/unified_news_interface.py — Interfaz Principal Unificada del Sistema de Noticias

import streamlit as st
import pandas as pd
from datetime import datetime
import time

# Importar módulos del sistema
from .protocol_manager import protocol_manager
from .storage_config import news_storage_config
from .noticias_module import (
    _run_pipeline_manual, _group_news_by_category, _map_categories_to_t70,
    _prepare_news_for_capas, _show_gem_results, _show_sub_results,
    _show_t70_mapping_results, _show_pipeline_summary, _show_news_selection_details
)

class UnifiedNewsInterface:
    """Interfaz principal unificada del sistema de noticias."""
    
    def __init__(self):
        self.current_view = "dashboard"
        self.views = {
            "dashboard": "🏠 Dashboard",
            "protocol": "🎯 Protocolo",
            "storage": "💾 Almacenamiento",
            "analysis": "🔍 Análisis",
            "export": "📥 Exportación"
        }
    
    def render_main_interface(self):
        """Renderiza la interfaz principal unificada."""
        st.title("📰 **SISTEMA UNIFICADO DE NOTICIAS - VISIÓN PREMIUM**")
        st.markdown("### Sistema Organizado de Almacenamiento y Protocolos - Sin Complejidad Visual")
        
        # Sidebar de navegación
        self._render_sidebar()
        
        # Contenido principal según la vista seleccionada
        if self.current_view == "dashboard":
            self._render_dashboard()
        elif self.current_view == "protocol":
            self._render_protocol_interface()
        elif self.current_view == "storage":
            self._render_storage_interface()
        elif self.current_view == "analysis":
            self._render_analysis_interface()
        elif self.current_view == "export":
            self._render_export_interface()
    
    def _render_sidebar(self):
        """Renderiza la barra lateral de navegación."""
        with st.sidebar:
            st.title("🔮 Visión Premium")
            st.markdown("### Navegación Principal")
            
            # Selector de vista
            selected_view = st.selectbox(
                "Seleccionar Vista:",
                list(self.views.keys()),
                format_func=lambda x: self.views[x],
                index=list(self.views.keys()).index(self.current_view)
            )
            
            if selected_view != self.current_view:
                self.current_view = selected_view
                st.rerun()
            
            st.markdown("---")
            
            # Estado del sistema
            st.markdown("#### 📊 Estado del Sistema")
            
            # Verificar estado del protocolo
            if "protocol_execution_log" in st.session_state:
                protocol_status = "🔄 En Progreso"
            else:
                protocol_status = "⏳ No Iniciado"
            
            st.metric("Protocolo", protocol_status)
            
            # Verificar estado del almacenamiento
            storage_status = news_storage_config.get_storage_status()
            total_files = sum(status["file_count"] for status in storage_status.values())
            st.metric("Archivos", total_files)
            
            # Botones de acción rápida
            st.markdown("#### ⚡ Acciones Rápidas")
            
            if st.button("🚀 Iniciar Protocolo", use_container_width=True):
                protocol_manager.start_protocol()
                self.current_view = "protocol"
                st.rerun()
            
            if st.button("🧹 Limpiar Sistema", use_container_width=True):
                self._cleanup_system()
            
            if st.button("📊 Estado Completo", use_container_width=True):
                self._show_system_status()
    
    def _render_dashboard(self):
        """Renderiza el dashboard principal."""
        st.header("🏠 **DASHBOARD PRINCIPAL**")
        st.markdown("### Resumen del Sistema y Estado General")
        
        # KPIs principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Estado del protocolo
            if "protocol_execution_log" in st.session_state:
                protocol_progress = protocol_manager.get_protocol_progress()
                st.metric("Protocolo", f"{protocol_progress['progress_percentage']:.1f}%")
            else:
                st.metric("Protocolo", "No Iniciado")
        
        with col2:
            # Estado del almacenamiento
            storage_status = news_storage_config.get_storage_status()
            total_size = sum(status["total_size_mb"] for status in storage_status.values())
            st.metric("Almacenamiento", f"{total_size:.1f} MB")
        
        with col3:
            # Noticias disponibles
            if "news_selected_df" in st.session_state:
                news_count = len(st.session_state["news_selected_df"])
                st.metric("Noticias", news_count)
            else:
                st.metric("Noticias", "0")
        
        with col4:
            # Estado general
            if "protocol_execution_log" in st.session_state:
                protocol_progress = protocol_manager.get_protocol_progress()
                if protocol_progress["status"] == "completed":
                    st.metric("Estado", "✅ COMPLETADO")
                elif protocol_progress["status"] == "failed":
                    st.metric("Estado", "❌ FALLIDO")
                else:
                    st.metric("Estado", "🔄 EN PROGRESO")
            else:
                st.metric("Estado", "⏳ PENDIENTE")
        
        # Resumen del protocolo
        st.markdown("#### 🎯 **RESUMEN DEL PROTOCOLO**")
        
        if "protocol_execution_log" in st.session_state:
            protocol_progress = protocol_manager.get_protocol_progress()
            protocol_manager.render_progress_dashboard()
        else:
            st.info("ℹ️ **No hay protocolo en ejecución.** Haz clic en 'Iniciar Protocolo' para comenzar.")
        
        # Acciones principales
        st.markdown("#### 🚀 **ACCIONES PRINCIPALES**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎯 **INICIAR PROTOCOLO COMPLETO**", 
                        type="primary", use_container_width=True):
                protocol_manager.start_protocol()
                self.current_view = "protocol"
                st.rerun()
        
        with col2:
            if st.button("🔍 **ACOPIO RÁPIDO**", 
                        type="secondary", use_container_width=True):
                self._execute_quick_acopio()
        
        with col3:
            if st.button("📊 **VER ESTADO COMPLETO**", 
                        type="secondary", use_container_width=True):
                self._show_system_status()
        
        # Información del sistema
        st.markdown("#### ℹ️ **INFORMACIÓN DEL SISTEMA**")
        
        with st.expander("📋 **Características del Sistema**"):
            st.markdown("""
            **🎯 Protocolo Organizado:**
            • 6 pasos secuenciales y organizados
            • Verificación automática de dependencias
            • Seguimiento visual del progreso
            • Logs detallados de ejecución
            
            **💾 Almacenamiento Organizado:**
            • Estructura de directorios clara
            • Separación por tipo de datos
            • Archivo automático de datos antiguos
            • Limpieza de archivos temporales
            
            **🔍 Análisis Especializado:**
            • Categorización emocional automática
            • Mapeo T70 por categorías
            • Análisis Gematría y Subliminal
            • Exportación de resultados
            
            **📱 Interfaz Simplificada:**
            • Sin complejidad visual
            • Navegación clara y directa
            • Estado visible en todo momento
            • Acciones contextuales
            """)
    
    def _render_protocol_interface(self):
        """Renderiza la interfaz del protocolo."""
        st.header("🎯 **INTERFAZ DEL PROTOCOLO**")
        st.markdown("### Ejecución Paso a Paso del Protocolo de Noticias")
        
        # Verificar si el protocolo está iniciado
        if "protocol_execution_log" not in st.session_state:
            st.warning("⚠️ **El protocolo no está iniciado.**")
            if st.button("🚀 Iniciar Protocolo", type="primary"):
                protocol_manager.start_protocol()
                st.rerun()
            return
        
        # Dashboard de progreso
        protocol_manager.render_progress_dashboard()
        
        # Selector de paso
        st.markdown("#### 🔍 **SELECCIONAR PASO PARA EJECUTAR**")
        
        step_options = [f"{step['id']}: {step['name']}" for step in protocol_manager.steps]
        selected_step = st.selectbox(
            "Paso a ejecutar:",
            step_options,
            index=protocol_manager.protocol_state["current_step"]
        )
        
        selected_step_id = int(selected_step.split(":")[0])
        
        # Mostrar interfaz del paso seleccionado
        protocol_manager.render_step_interface(selected_step_id)
        
        # Botones de ejecución
        st.markdown("#### ⚡ **EJECUCIÓN DEL PASO**")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button(f"🚀 **EJECUTAR PASO {selected_step_id}**", 
                        type="primary", use_container_width=True):
                self._execute_protocol_step(selected_step_id)
        
        with col2:
            if st.button("📊 Ver Resultados", use_container_width=True):
                self._show_step_results(selected_step_id)
        
        # Navegación entre pasos
        st.markdown("#### 🧭 **NAVEGACIÓN**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⏮️ Paso Anterior", 
                        disabled=selected_step_id == 0, use_container_width=True):
                protocol_manager.protocol_state["current_step"] = max(0, selected_step_id - 1)
                st.rerun()
        
        with col2:
            if st.button("⏭️ Paso Siguiente", 
                        disabled=selected_step_id >= len(protocol_manager.steps) - 1, use_container_width=True):
                protocol_manager.protocol_state["current_step"] = min(len(protocol_manager.steps) - 1, selected_step_id + 1)
                st.run()
        
        with col3:
            if st.button("🏠 Dashboard", use_container_width=True):
                self.current_view = "dashboard"
                st.rerun()
        
        with col4:
            if st.button("📋 Resumen", use_container_width=True):
                protocol_manager.render_protocol_summary()
    
    def _render_storage_interface(self):
        """Renderiza la interfaz de almacenamiento."""
        st.header("💾 **INTERFAZ DE ALMACENAMIENTO**")
        st.markdown("### Gestión del Sistema de Almacenamiento Organizado")
        
        # Estado del almacenamiento
        storage_status = news_storage_config.get_storage_status()
        
        # KPIs del almacenamiento
        col1, col2, col3, col4 = st.columns(4)
        
        total_files = sum(status["file_count"] for status in storage_status.values())
        total_size = sum(status["total_size_mb"] for status in storage_status.values())
        
        with col1:
            st.metric("Total Archivos", total_files)
        
        with col2:
            st.metric("Tamaño Total", f"{total_size:.1f} MB")
        
        with col3:
            st.metric("Directorios", len(storage_status))
        
        with col4:
            st.metric("Estado", "✅ OPERATIVO")
        
        # Detalle por tipo de almacenamiento
        st.markdown("#### 📊 **DETALLE POR TIPO DE ALMACENAMIENTO**")
        
        storage_data = []
        for storage_type, status in storage_status.items():
            storage_data.append({
                "Tipo": storage_type.replace("_", " ").title(),
                "Archivos": status["file_count"],
                "Tamaño (MB)": f"{status['total_size_mb']:.2f}",
                "Último Archivo": status["latest_file"] or "Ninguno",
                "Ruta": status["path"]
            })
        
        st.dataframe(pd.DataFrame(storage_data), use_container_width=True, hide_index=True)
        
        # Acciones de almacenamiento
        st.markdown("#### 🔧 **ACCIONES DE ALMACENAMIENTO**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 Archivar Datos Antiguos", use_container_width=True):
                with st.spinner("Archivando datos antiguos..."):
                    news_storage_config.archive_old_data(days_to_keep=30)
                    st.success("✅ Datos archivados correctamente")
                    st.rerun()
        
        with col2:
            if st.button("🧹 Limpiar Temporales", use_container_width=True):
                with st.spinner("Limpiando archivos temporales..."):
                    news_storage_config.cleanup_temp_files()
                    st.success("✅ Archivos temporales limpiados")
                    st.rerun()
        
        with col3:
            if st.button("📊 Actualizar Estado", use_container_width=True):
                st.rerun()
        
        # Explorador de archivos
        st.markdown("#### 🔍 **EXPLORADOR DE ARCHIVOS**")
        
        selected_storage = st.selectbox(
            "Seleccionar tipo de almacenamiento:",
            list(storage_status.keys()),
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        if selected_storage:
            storage_path = news_storage_config.get_storage_path(selected_storage)
            files = list(storage_path.glob("*.csv"))
            
            if files:
                st.markdown(f"**Archivos en {selected_storage}:**")
                
                file_data = []
                for file_path in files:
                    file_stat = file_path.stat()
                    file_data.append({
                        "Nombre": file_path.name,
                        "Tamaño (KB)": f"{file_stat.st_size / 1024:.1f}",
                        "Modificado": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                st.dataframe(pd.DataFrame(file_data), use_container_width=True, hide_index=True)
                
                # Botón para cargar archivo
                selected_file = st.selectbox(
                    "Seleccionar archivo para cargar:",
                    [f.name for f in files]
                )
                
                if st.button("📂 Cargar Archivo", use_container_width=True):
                    data = news_storage_config.load_news_data(selected_storage, selected_file)
                    if not data.empty:
                        st.session_state[f"loaded_{selected_storage}"] = data
                        st.success(f"✅ Archivo {selected_file} cargado correctamente")
                        st.dataframe(data.head(10), use_container_width=True)
                    else:
                        st.error("❌ Error al cargar el archivo")
            else:
                st.info(f"ℹ️ No hay archivos en {selected_storage}")
    
    def _render_analysis_interface(self):
        """Renderiza la interfaz de análisis."""
        st.header("🔍 **INTERFAZ DE ANÁLISIS**")
        st.markdown("### Análisis Especializado de Noticias")
        
        # Verificar datos disponibles
        available_data = self._check_available_data()
        
        if not available_data["has_news"]:
            st.warning("⚠️ **No hay noticias disponibles para analizar.**")
            st.info("ℹ️ Ejecuta el acopio de noticias primero.")
            return
        
        # Análisis disponibles
        st.markdown("#### 📊 **ANÁLISIS DISPONIBLES**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if available_data["has_categorized"]:
                st.success("✅ Categorización Emocional")
                if st.button("📊 Ver Categorías", use_container_width=True):
                    self._show_categorization_analysis()
            else:
                st.warning("⚠️ Categorización Emocional")
        
        with col2:
            if available_data["has_t70"]:
                st.success("✅ Mapeo T70")
                if st.button("🔢 Ver T70", use_container_width=True):
                    self._show_t70_analysis()
            else:
                st.warning("⚠️ Mapeo T70")
        
        with col3:
            if available_data["has_gem_sub"]:
                st.success("✅ Gematría + Subliminal")
                if st.button("🔮 Ver Análisis", use_container_width=True):
                    self._show_gem_sub_analysis()
            else:
                st.warning("⚠️ Gematría + Subliminal")
        
        # Análisis personalizado
        st.markdown("#### 🔍 **ANÁLISIS PERSONALIZADO**")
        
        if available_data["has_news"]:
            df_news = st.session_state["news_selected_df"]
            
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                if "_categoria_emocional" in df_news.columns:
                    categories = sorted(df_news["_categoria_emocional"].unique())
                    selected_category = st.selectbox("Filtrar por categoría:", ["Todas"] + list(categories))
                else:
                    selected_category = "Todas"
            
            with col2:
                if "_nivel_impacto" in df_news.columns:
                    impact_levels = sorted(df_news["_nivel_impacto"].unique())
                    selected_impact = st.selectbox("Filtrar por impacto:", ["Todos"] + [str(l) for l in impact_levels])
                else:
                    selected_impact = "Todos"
            
            # Aplicar filtros
            filtered_news = df_news.copy()
            
            if selected_category != "Todas" and "_categoria_emocional" in filtered_news.columns:
                filtered_news = filtered_news[filtered_news["_categoria_emocional"] == selected_category]
            
            if selected_impact != "Todos" and "_nivel_impacto" in filtered_news.columns:
                filtered_news = filtered_news[filtered_news["_nivel_impacto"] == int(selected_impact)]
            
            # Mostrar noticias filtradas
            st.markdown(f"#### 📰 **Noticias Filtradas ({len(filtered_news)} de {len(df_news)})**")
            
            if not filtered_news.empty:
                display_cols = ["titular", "fuente", "_score_es"]
                if "_categoria_emocional" in filtered_news.columns:
                    display_cols.insert(1, "_categoria_emocional")
                if "_nivel_impacto" in filtered_news.columns:
                    display_cols.append("_nivel_impacto")
                
                st.dataframe(filtered_news[display_cols], use_container_width=True, hide_index=True)
                
                # KPIs de las noticias filtradas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Noticias Filtradas", len(filtered_news))
                
                with col2:
                    st.metric("Score Promedio", f"{filtered_news['_score_es'].mean():.3f}")
                
                with col3:
                    if "_nivel_impacto" in filtered_news.columns:
                        st.metric("Impacto Promedio", f"{filtered_news['_nivel_impacto'].mean():.1f}/5")
                    else:
                        st.metric("Fuentes Únicas", filtered_news["fuente"].nunique())
                
                with col4:
                    st.metric("Recencia Promedio", f"{((pd.Timestamp.now() - filtered_news['fecha_dt']).dt.total_seconds()/3600).mean():.1f}h")
            else:
                st.info("ℹ️ No hay noticias que coincidan con los filtros seleccionados.")
    
    def _render_export_interface(self):
        """Renderiza la interfaz de exportación."""
        st.header("📥 **INTERFAZ DE EXPORTACIÓN**")
        st.markdown("### Exportación de Datos y Resultados")
        
        # Verificar datos disponibles
        available_data = self._check_available_data()
        
        if not available_data["has_news"]:
            st.warning("⚠️ **No hay datos disponibles para exportar.**")
            st.info("ℹ️ Ejecuta el protocolo primero para generar datos.")
            return
        
        # Opciones de exportación
        st.markdown("#### 📤 **OPCIONES DE EXPORTACIÓN**")
        
        # Exportación por tipo de dato
        export_options = []
        
        if available_data["has_news"]:
            export_options.append("📰 Noticias Seleccionadas")
        
        if available_data["has_categorized"]:
            export_options.append("📊 Noticias Categorizadas")
        
        if available_data["has_t70"]:
            export_options.append("🔢 Mapeo T70")
        
        if available_data["has_gem_sub"]:
            export_options.append("🔮 Análisis Gematría + Subliminal")
        
        if export_options:
            selected_export = st.selectbox("Seleccionar datos para exportar:", export_options)
            
            # Botones de exportación
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Exportar CSV", use_container_width=True):
                    self._export_data_csv(selected_export)
            
            with col2:
                if st.button("📥 Exportar JSON", use_container_width=True):
                    self._export_data_json(selected_export)
        
        # Exportación completa del protocolo
        st.markdown("#### 🎯 **EXPORTACIÓN COMPLETA DEL PROTOCOLO**")
        
        if "protocol_execution_log" in st.session_state:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Log de Ejecución", use_container_width=True):
                    protocol_manager.export_execution_log()
            
            with col2:
                if st.button("📊 Resumen Pipeline", use_container_width=True):
                    if "news_raw_df" in st.session_state and "news_selected_df" in st.session_state:
                        _show_pipeline_summary(
                            st.session_state["news_raw_df"],
                            st.session_state["news_selected_df"],
                            st.session_state.get("pipeline_logs", {})
                        )
            
            with col3:
                if st.button("📰 Detalles Noticias", use_container_width=True):
                    if "news_selected_df" in st.session_state:
                        _show_news_selection_details(st.session_state["news_selected_df"])
        else:
            st.info("ℹ️ No hay protocolo en ejecución para exportar.")
        
        # Limpieza del sistema
        st.markdown("#### 🧹 **LIMPIEZA DEL SISTEMA**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Limpiar Datos Temporales", use_container_width=True):
                self._cleanup_system()
        
        with col2:
            if st.button("🔄 Reiniciar Todo", use_container_width=True):
                self._reset_everything()
    
    def _execute_quick_acopio(self):
        """Ejecuta un acopio rápido de noticias."""
        with st.spinner("🔄 **Ejecutando acopio rápido...**"):
            try:
                df_raw, df_sel, logs = _run_pipeline_manual()
                
                # Guardar en sesión
                st.session_state["news_raw_df"] = df_raw.copy()
                st.session_state["news_selected_df"] = df_sel.copy()
                st.session_state["pipeline_logs"] = logs.copy()
                
                if len(df_sel) >= 50:
                    st.success(f"✅ **Acopio rápido completado!** {len(df_sel)} noticias recolectadas")
                else:
                    st.warning(f"⚠️ **Solo se recolectaron {len(df_sel)} noticias. Se requieren mínimo 50.**")
                    
            except Exception as e:
                st.error(f"❌ **Error en acopio rápido:** {str(e)}")
    
    def _execute_protocol_step(self, step_id: int):
        """Ejecuta un paso específico del protocolo."""
        step_functions = {
            0: self._execute_step_acopio,
            1: self._execute_step_categorization,
            2: self._execute_step_t70,
            3: self._execute_step_gematria,
            4: self._execute_step_subliminal,
            5: self._execute_step_results
        }
        
        if step_id in step_functions:
            execution_function = step_functions[step_id]
            protocol_manager.execute_step(step_id, execution_function)
        else:
            st.error(f"❌ **Paso {step_id} no implementado**")
    
    def _execute_step_acopio(self):
        """Ejecuta el paso de acopio."""
        try:
            df_raw, df_sel, logs = _run_pipeline_manual()
            
            # Guardar en sesión
            st.session_state["news_raw_df"] = df_raw.copy()
            st.session_state["news_selected_df"] = df_sel.copy()
            st.session_state["pipeline_logs"] = logs.copy()
            
            # Guardar en almacenamiento
            news_storage_config.save_news_data(df_raw, "raw_news")
            news_storage_config.save_news_data(df_sel, "processed_news")
            
            return len(df_sel) >= 50
            
        except Exception as e:
            st.error(f"Error en acopio: {e}")
            return False
    
    def _execute_step_categorization(self):
        """Ejecuta el paso de categorización."""
        try:
            if "news_selected_df" not in st.session_state:
                return False
            
            df_sel = st.session_state["news_selected_df"]
            
            # La categorización ya se hace en el scoring, solo verificar
            if "_categoria_emocional" in df_sel.columns:
                # Guardar noticias categorizadas
                news_storage_config.save_news_data(df_sel, "categorized_news")
                st.session_state["categorized_news"] = df_sel.copy()
                return True
            else:
                return False
                
        except Exception as e:
            st.error(f"Error en categorización: {e}")
            return False
    
    def _execute_step_t70(self):
        """Ejecuta el paso de mapeo T70."""
        try:
            if "categorized_news" not in st.session_state:
                return False
            
            df_cat = st.session_state["categorized_news"]
            
            # Agrupar por categorías
            category_groups = _group_news_by_category(df_cat)
            
            if not category_groups:
                return False
            
            # Mapear a T70
            t70_mapping = _map_categories_to_t70(category_groups)
            
            if not t70_mapping:
                return False
            
            # Guardar resultados
            st.session_state["t70_mapping"] = t70_mapping
            
            # Crear DataFrame de resultados T70
            t70_results = []
            for categoria, data in t70_mapping.items():
                for _, noticia in data["noticias"].iterrows():
                    t70_numbers = [str(item["numero"]) for item in data["t70_equivalencias"]]
                    t70_results.append({
                        "id_noticia": noticia.get("id_noticia", ""),
                        "titular": noticia.get("titular", ""),
                        "categoria_emocional": categoria,
                        "t70_numbers": ", ".join(t70_numbers),
                        "total_t70": len(t70_numbers)
                    })
            
            if t70_results:
                df_t70 = pd.DataFrame(t70_results)
                news_storage_config.save_news_data(df_t70, "t70_mapped")
                st.session_state["t70_results"] = df_t70
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error en mapeo T70: {e}")
            return False
    
    def _execute_step_gematria(self):
        """Ejecuta el paso de análisis Gematría."""
        try:
            if "t70_mapping" not in st.session_state:
                return False
            
            t70_mapping = st.session_state["t70_mapping"]
            
            # Preparar datos para GEM
            gem_data, _ = _prepare_news_for_capas(t70_mapping)
            
            if gem_data.empty:
                return False
            
            # Guardar resultados
            st.session_state["gem_results"] = gem_data
            news_storage_config.save_news_data(gem_data, "gem_results")
            
            return True
            
        except Exception as e:
            st.error(f"Error en análisis Gematría: {e}")
            return False
    
    def _execute_step_subliminal(self):
        """Ejecuta el paso de análisis Subliminal."""
        try:
            if "t70_mapping" not in st.session_state:
                return False
            
            t70_mapping = st.session_state["t70_mapping"]
            
            # Preparar datos para SUB
            _, sub_data = _prepare_news_for_capas(t70_mapping)
            
            if sub_data.empty:
                return False
            
            # Guardar resultados
            st.session_state["sub_results"] = sub_data
            news_storage_config.save_news_data(sub_data, "sub_results")
            
            return True
            
        except Exception as e:
            st.error(f"Error en análisis Subliminal: {e}")
            return False
    
    def _execute_step_results(self):
        """Ejecuta el paso de resultados finales."""
        try:
            # Verificar que todos los pasos estén completados
            required_data = ["gem_results", "sub_results"]
            
            for data_key in required_data:
                if data_key not in st.session_state:
                    return False
                if isinstance(st.session_state[data_key], pd.DataFrame) and st.session_state[data_key].empty:
                    return False
            
            # Crear resumen del protocolo
            protocol_summary = {
                "timestamp": datetime.now().isoformat(),
                "total_steps": len(protocol_manager.steps),
                "completed_steps": len(protocol_manager.protocol_state["completed_steps"]),
                "news_count": len(st.session_state["news_selected_df"]),
                "categories_count": st.session_state["news_selected_df"]["_categoria_emocional"].nunique() if "_categoria_emocional" in st.session_state["news_selected_df"].columns else 0,
                "t70_mappings": len(st.session_state["t70_mapping"]),
                "gem_results_count": len(st.session_state["gem_results"]),
                "sub_results_count": len(st.session_state["sub_results"])
            }
            
            st.session_state["protocol_summary"] = protocol_summary
            
            return True
            
        except Exception as e:
            st.error(f"Error en resultados finales: {e}")
            return False
    
    def _show_step_results(self, step_id: int):
        """Muestra los resultados de un paso específico."""
        if step_id == 0 and "news_selected_df" in st.session_state:
            st.subheader("📰 **Resultados del Acopio**")
            df_sel = st.session_state["news_selected_df"]
            st.dataframe(df_sel.head(10), use_container_width=True)
            
        elif step_id == 1 and "categorized_news" in st.session_state:
            st.subheader("📊 **Resultados de Categorización**")
            df_cat = st.session_state["categorized_news"]
            if "_categoria_emocional" in df_cat.columns:
                cat_counts = df_cat["_categoria_emocional"].value_counts()
                st.dataframe(cat_counts, use_container_width=True)
        
        elif step_id == 2 and "t70_mapping" in st.session_state:
            st.subheader("🔢 **Resultados del Mapeo T70**")
            _show_t70_mapping_results(st.session_state["t70_mapping"])
        
        elif step_id == 3 and "gem_results" in st.session_state:
            st.subheader("🔡 **Resultados del Análisis Gematría**")
            _show_gem_results(st.session_state["gem_results"])
        
        elif step_id == 4 and "sub_results" in st.session_state:
            st.subheader("🧠 **Resultados del Análisis Subliminal**")
            _show_sub_results(st.session_state["sub_results"])
        
        elif step_id == 5 and "protocol_summary" in st.session_state:
            st.subheader("📋 **Resumen del Protocolo**")
            st.json(st.session_state["protocol_summary"])
        
        else:
            st.info("ℹ️ No hay resultados disponibles para este paso.")
    
    def _check_available_data(self) -> dict:
        """Verifica qué datos están disponibles."""
        return {
            "has_news": "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty,
            "has_categorized": "categorized_news" in st.session_state and not st.session_state["categorized_news"].empty,
            "has_t70": "t70_mapping" in st.session_state and st.session_state["t70_mapping"],
            "has_gem_sub": ("gem_results" in st.session_state and not st.session_state["gem_results"].empty and
                           "sub_results" in st.session_state and not st.session_state["sub_results"].empty)
        }
    
    def _show_system_status(self):
        """Muestra el estado completo del sistema."""
        st.subheader("📊 **ESTADO COMPLETO DEL SISTEMA**")
        
        # Estado del protocolo
        if "protocol_execution_log" in st.session_state:
            protocol_progress = protocol_manager.get_protocol_progress()
            st.markdown("#### 🎯 **Estado del Protocolo**")
            st.json(protocol_progress)
        else:
            st.info("ℹ️ No hay protocolo en ejecución")
        
        # Estado del almacenamiento
        storage_status = news_storage_config.get_storage_status()
        st.markdown("#### 💾 **Estado del Almacenamiento**")
        st.json(storage_status)
        
        # Datos en sesión
        session_data = {}
        for key in st.session_state.keys():
            if key.startswith("news_") or key.endswith("_df") or key.endswith("_results"):
                if isinstance(st.session_state[key], pd.DataFrame):
                    session_data[key] = {
                        "type": "DataFrame",
                        "rows": len(st.session_state[key]),
                        "columns": list(st.session_state[key].columns)
                    }
                elif isinstance(st.session_state[key], dict):
                    session_data[key] = {
                        "type": "dict",
                        "keys": list(st.session_state[key].keys())
                    }
                else:
                    session_data[key] = {
                        "type": type(st.session_state[key]).__name__,
                        "value": str(st.session_state[key])
                    }
        
        if session_data:
            st.markdown("#### 📋 **Datos en Sesión**")
            st.json(session_data)
    
    def _cleanup_system(self):
        """Limpia el sistema."""
        # Limpiar archivos temporales
        news_storage_config.cleanup_temp_files()
        
        # Limpiar datos de sesión (mantener logs)
        keys_to_clear = [
            "news_raw_df", "news_selected_df", "pipeline_logs",
            "categorized_news", "t70_mapping", "t70_results",
            "gem_results", "sub_results", "protocol_summary"
        ]
        
        cleaned_count = 0
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
                cleaned_count += 1
        
        st.success(f"🧹 **Sistema limpiado:** {cleaned_count} variables limpiadas")
    
    def _reset_everything(self):
        """Reinicia todo el sistema."""
        # Reiniciar protocolo
        protocol_manager.reset_protocol()
        
        # Limpiar sistema
        self._cleanup_system()
        
        # Limpiar almacenamiento temporal
        news_storage_config.cleanup_temp_files()
        
        st.success("🔄 **Sistema completamente reiniciado**")
        st.rerun()
    
    def _export_data_csv(self, data_type: str):
        """Exporta datos en formato CSV."""
        data_mapping = {
            "📰 Noticias Seleccionadas": ("news_selected_df", "noticias_seleccionadas"),
            "📊 Noticias Categorizadas": ("categorized_news", "noticias_categorizadas"),
            "🔢 Mapeo T70": ("t70_results", "mapeo_t70"),
            "🔮 Análisis Gematría + Subliminal": ("gem_results", "analisis_gematria_subliminal")
        }
        
        if data_type in data_mapping:
            session_key, filename = data_mapping[data_type]
            
            if session_key in st.session_state:
                data = st.session_state[session_key]
                if not data.empty:
                    csv_data = data.to_csv(index=False, encoding="utf-8")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    download_filename = f"{filename}_{timestamp}.csv"
                    
                    st.download_button(
                        f"📥 Descargar {data_type} (CSV)",
                        csv_data.encode("utf-8"),
                        download_filename,
                        "text/csv"
                    )
                else:
                    st.warning(f"No hay datos disponibles para {data_type}")
            else:
                st.warning(f"No hay datos disponibles para {data_type}")
    
    def _export_data_json(self, data_type: str):
        """Exporta datos en formato JSON."""
        data_mapping = {
            "📰 Noticias Seleccionadas": ("news_selected_df", "noticias_seleccionadas"),
            "📊 Noticias Categorizadas": ("categorized_news", "noticias_categorizadas"),
            "🔢 Mapeo T70": ("t70_results", "mapeo_t70"),
            "🔮 Análisis Gematría + Subliminal": ("gem_results", "analisis_gematria_subliminal")
        }
        
        if data_type in data_mapping:
            session_key, filename = data_mapping[data_type]
            
            if session_key in st.session_state:
                data = st.session_state[session_key]
                if not data.empty:
                    json_data = data.to_json(orient="records", force_ascii=False, indent=2)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    download_filename = f"{filename}_{timestamp}.json"
                    
                    st.download_button(
                        f"📥 Descargar {data_type} (JSON)",
                        json_data.encode("utf-8"),
                        download_filename,
                        "application/json"
                    )
                else:
                    st.warning(f"No hay datos disponibles para {data_type}")
            else:
                st.warning(f"No hay datos disponibles para {data_type}")

# Instancia global
unified_news_interface = UnifiedNewsInterface()









