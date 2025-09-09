# modules/news_interface.py — Interfaz Visual Unificada de Noticias
# Sigue el protocolo paso a paso de manera clara y organizada

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

# Importar funciones del módulo de noticias
from .noticias_module import (
    _run_pipeline_manual, _group_news_by_category, _map_categories_to_t70,
    _prepare_news_for_capas, _show_gem_results, _show_sub_results,
    _show_t70_mapping_results, _show_pipeline_summary, _show_news_selection_details
)

class NewsInterface:
    def __init__(self):
        self.current_step = 0
        self.steps = [
            "🔍 ACOPIO DE NOTICIAS",
            "📊 CATEGORIZACIÓN EMOCIONAL", 
            "🔢 MAPEO T70",
            "🔡 ANÁLISIS GEMATRÍA",
            "🧠 ANÁLISIS SUBLIMINAL",
            "📋 RESULTADOS COMPLETOS"
        ]
    
    def render_protocol_interface(self):
        """Renderiza la interfaz principal del protocolo de noticias."""
        st.title("📰 **PROTOCOLO COMPLETO DE NOTICIAS**")
        st.markdown("### Sistema Organizado Paso a Paso - Sin Complejidad Visual")
        
        # Barra de progreso del protocolo
        self._render_progress_bar()
        
        # Contenido principal según el paso actual
        if self.current_step == 0:
            self._render_step_acopio()
        elif self.current_step == 1:
            self._render_step_categorizacion()
        elif self.current_step == 2:
            self._render_step_t70()
        elif self.current_step == 3:
            self._render_step_gematria()
        elif self.current_step == 4:
            self._render_step_subliminal()
        elif self.current_step == 5:
            self._render_step_resultados()
        
        # Navegación entre pasos
        self._render_navigation()
    
    def _render_progress_bar(self):
        """Renderiza la barra de progreso del protocolo."""
        st.markdown("---")
        st.markdown("#### 🎯 **PROGRESO DEL PROTOCOLO**")
        
        # Crear columnas para cada paso
        cols = st.columns(len(self.steps))
        
        for i, (col, step) in enumerate(zip(cols, self.steps)):
            with col:
                if i < self.current_step:
                    # Paso completado
                    st.success(f"✅ {step}")
                elif i == self.current_step:
                    # Paso actual
                    st.info(f"🔄 {step}")
                else:
                    # Paso pendiente
                    st.caption(f"⏳ {step}")
        
        st.markdown("---")
    
    def _render_step_acopio(self):
        """Paso 1: Acopio de noticias."""
        st.header("🔍 **PASO 1: ACOPIO DE NOTICIAS**")
        st.markdown("### Recolección y filtrado inicial de noticias")
        
        # Botón principal de acopio
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🚀 **INICIAR ACOPIO DE NOTICIAS**", 
                        type="primary", use_container_width=True, key="btn_acopio_principal"):
                self._execute_news_acopio()
        
        with col2:
            if st.button("📊 Ver KPIs", use_container_width=True, key="btn_kpis"):
                st.session_state["show_kpis"] = True
        
        with col3:
            if st.button("📋 Ver Noticias", use_container_width=True, key="btn_ver_noticias"):
                st.session_state["show_news"] = True
        
        # Mostrar KPIs si están disponibles
        if st.session_state.get("show_kpis", False) and "news_selected_df" in st.session_state:
            self._show_acopio_kpis()
        
        # Mostrar noticias si están disponibles
        if st.session_state.get("show_news", False) and "news_selected_df" in st.session_state:
            self._show_acopio_news()
        
        # Información del paso
        st.markdown("---")
        st.markdown("#### ℹ️ **INFORMACIÓN DEL PASO**")
        st.info("""
        **Objetivo:** Recolectar mínimo 50 noticias, meta 100 noticias
        
        **Proceso:**
        1. ✅ Recolección de RSS, Google News, Bing News
        2. ✅ Filtrado por recencia (72 horas)
        3. ✅ Scoring emocional y relevancia
        4. ✅ Deduplicación semántica
        5. ✅ Categorización emocional automática
        
        **Resultado:** DataFrame con noticias seleccionadas y categorizadas
        """)
    
    def _render_step_categorizacion(self):
        """Paso 2: Categorización emocional."""
        st.header("📊 **PASO 2: CATEGORIZACIÓN EMOCIONAL**")
        st.markdown("### Análisis automático de impacto emocional")
        
        if "news_selected_df" not in st.session_state or st.session_state["news_selected_df"].empty:
            st.warning("⚠️ **Debes completar el Paso 1 (Acopio) primero**")
            return
        
        df_sel = st.session_state["news_selected_df"]
        
        # KPIs de categorización
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Noticias", len(df_sel))
        with col2:
            if "_categoria_emocional" in df_sel.columns:
                st.metric("Categorías", df_sel["_categoria_emocional"].nunique())
            else:
                st.metric("Categorías", "No disponible")
        with col3:
            if "_nivel_impacto" in df_sel.columns:
                st.metric("Impacto Promedio", f"{df_sel['_nivel_impacto'].mean():.1f}/5")
            else:
                st.metric("Impacto Promedio", "No disponible")
        with col4:
            st.metric("Score Promedio", f"{df_sel['_score_es'].mean():.3f}")
        
        # Mostrar distribución de categorías
        if "_categoria_emocional" in df_sel.columns:
            st.markdown("#### 📊 **DISTRIBUCIÓN POR CATEGORÍAS EMOCIONALES**")
            
            # Contar noticias por categoría
            cat_counts = df_sel["_categoria_emocional"].value_counts()
            
            # Mostrar en columnas
            cat_cols = st.columns(min(4, len(cat_counts)))
            for i, (categoria, count) in enumerate(cat_counts.items()):
                with cat_cols[i % 4]:
                    st.metric(categoria.replace("_", " ").title(), count)
        
        # Botón para continuar
        if st.button("✅ **CATEGORIZACIÓN COMPLETADA - CONTINUAR**", 
                    type="primary", use_container_width=True, key="btn_cat_complete"):
            self.current_step = 2
            st.rerun()
        
        # Información del paso
        st.markdown("---")
        st.markdown("#### ℹ️ **INFORMACIÓN DEL PASO**")
        st.info("""
        **Objetivo:** Categorizar automáticamente las noticias por impacto emocional
        
        **Categorías Identificadas:**
        • 🚨 Protestas Sociales
        • 🔫 Violencia y Seguridad  
        • 💰 Crisis Económica
        • 🌪️ Desastres Naturales
        • 🏛️ Política y Corrupción
        • 💻 Tecnología y Ciberseguridad
        • 🏥 Salud Pública
        • ⚡ Infraestructura
        
        **Niveles de Impacto:** 1-5 (Muy Bajo a Muy Alto)
        """)
    
    def _render_step_t70(self):
        """Paso 3: Mapeo T70."""
        st.header("🔢 **PASO 3: MAPEO T70**")
        st.markdown("### Agrupación por categorías y mapeo a equivalencias T70")
        
        if "news_selected_df" not in st.session_state or st.session_state["news_selected_df"].empty:
            st.warning("⚠️ **Debes completar los pasos anteriores primero**")
            return
        
        df_sel = st.session_state["news_selected_df"]
        
        # Botón para ejecutar mapeo T70
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 **EJECUTAR MAPEO T70**", 
                        type="primary", use_container_width=True, key="btn_t70_execute"):
                self._execute_t70_mapping(df_sel)
        
        with col2:
            if st.button("📊 Ver Mapeo", use_container_width=True, key="btn_ver_t70"):
                st.session_state["show_t70"] = True
        
        # Mostrar resultados del mapeo T70
        if st.session_state.get("show_t70", False) and "t70_mapping" in st.session_state:
            _show_t70_mapping_results(st.session_state["t70_mapping"])
        
        # Botón para continuar
        if "t70_mapping" in st.session_state and st.session_state["t70_mapping"]:
            if st.button("✅ **MAPEO T70 COMPLETADO - CONTINUAR**", 
                        type="primary", use_container_width=True, key="btn_t70_complete"):
                self.current_step = 3
                st.rerun()
        
        # Información del paso
        st.markdown("---")
        st.markdown("#### ℹ️ **INFORMACIÓN DEL PASO**")
        st.info("""
        **Objetivo:** Mapear cada categoría emocional a equivalencias en la tabla T70
        
        **Proceso:**
        1. ✅ Agrupar noticias por categoría emocional
        2. ✅ Buscar palabras clave en tabla T70
        3. ✅ Asignar números T70 a cada categoría
        4. ✅ Preparar datos para capas especializadas
        
        **Resultado:** Mapeo completo con números T70 por categoría
        """)
    
    def _render_step_gematria(self):
        """Paso 4: Análisis Gematría."""
        st.header("🔡 **PASO 4: ANÁLISIS GEMATRÍA**")
        st.markdown("### Búsqueda de números en noticias procesadas por T70")
        
        if "t70_mapping" not in st.session_state or not st.session_state["t70_mapping"]:
            st.warning("⚠️ **Debes completar el mapeo T70 primero**")
            return
        
        # Botón para ejecutar análisis Gematría
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 **EJECUTAR ANÁLISIS GEMATRÍA**", 
                        type="primary", use_container_width=True, key="btn_gem_execute"):
                self._execute_gematria_analysis()
        
        with col2:
            if st.button("📊 Ver Resultados GEM", use_container_width=True, key="btn_ver_gem"):
                st.session_state["show_gem"] = True
        
        # Mostrar resultados de Gematría
        if st.session_state.get("show_gem", False) and "gem_results" in st.session_state:
            _show_gem_results(st.session_state["gem_results"])
        
        # Botón para continuar
        if "gem_results" in st.session_state and not st.session_state["gem_results"].empty:
            if st.button("✅ **ANÁLISIS GEMATRÍA COMPLETADO - CONTINUAR**", 
                        type="primary", use_container_width=True, key="btn_gem_complete"):
                self.current_step = 4
                st.rerun()
        
        # Información del paso
        st.markdown("---")
        st.markdown("#### ℹ️ **INFORMACIÓN DEL PASO**")
        st.info("""
        **Objetivo:** Buscar números en noticias basándose en equivalencias T70
        
        **Proceso:**
        1. ✅ Recibir noticias procesadas por T70
        2. ✅ Analizar contenido anunciado en noticias
        3. ✅ Identificar números relevantes
        4. ✅ Generar análisis gematría completo
        
        **Resultado:** Análisis gematría con números encontrados
        """)
    
    def _render_step_subliminal(self):
        """Paso 5: Análisis Subliminal."""
        st.header("🧠 **PASO 5: ANÁLISIS SUBLIMINAL**")
        st.markdown("### Búsqueda de mensajes subliminales en las mismas noticias")
        
        if "t70_mapping" not in st.session_state or not st.session_state["t70_mapping"]:
            st.warning("⚠️ **Debes completar el mapeo T70 primero**")
            return
        
        # Botón para ejecutar análisis Subliminal
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🚀 **EJECUTAR ANÁLISIS SUBLIMINAL**", 
                        type="primary", use_container_width=True, key="btn_sub_execute"):
                self._execute_subliminal_analysis()
        
        with col2:
            if st.button("📊 Ver Resultados SUB", use_container_width=True, key="btn_ver_sub"):
                st.session_state["show_sub"] = True
        
        # Mostrar resultados de Subliminal
        if st.session_state.get("show_sub", False) and "sub_results" in st.session_state:
            _show_sub_results(st.session_state["sub_results"])
        
        # Botón para continuar
        if "sub_results" in st.session_state and not st.session_state["sub_results"].empty:
            if st.button("✅ **ANÁLISIS SUBLIMINAL COMPLETADO - CONTINUAR**", 
                        type="primary", use_container_width=True, key="btn_sub_complete"):
                self.current_step = 5
                st.rerun()
        
        # Información del paso
        st.markdown("---")
        st.markdown("#### ℹ️ **INFORMACIÓN DEL PASO**")
        st.info("""
        **Objetivo:** Buscar mensajes subliminales en las mismas noticias procesadas
        
        **Proceso:**
        1. ✅ Recibir las mismas noticias del mapeo T70
        2. ✅ Análisis de sentimiento del texto
        3. ✅ Clasificación de arquetipos
        4. ✅ Detección de mensajes subliminales
        
        **Resultado:** Análisis subliminal con mensajes detectados
        """)
    
    def _render_step_resultados(self):
        """Paso 6: Resultados completos."""
        st.header("📋 **PASO 6: RESULTADOS COMPLETOS**")
        st.markdown("### Resumen y exportación de todos los análisis")
        
        # Verificar que todos los pasos estén completados
        steps_completed = self._check_completion_status()
        
        if not steps_completed["all_complete"]:
            st.warning("⚠️ **Algunos pasos del protocolo no están completados**")
            self._show_completion_status(steps_completed)
            return
        
        st.success("🎉 **¡PROTOCOLO COMPLETADO EXITOSAMENTE!**")
        
        # Resumen general
        st.markdown("#### 📊 **RESUMEN GENERAL DEL PROTOCOLO**")
        self._show_protocol_summary()
        
        # Exportación completa
        st.markdown("#### 📥 **EXPORTACIÓN COMPLETA**")
        self._show_export_options()
        
        # Botón para reiniciar protocolo
        if st.button("🔄 **REINICIAR PROTOCOLO**", 
                    type="secondary", use_container_width=True, key="btn_restart"):
            self._reset_protocol()
            st.rerun()
    
    def _render_navigation(self):
        """Renderiza la navegación entre pasos."""
        st.markdown("---")
        st.markdown("#### 🧭 **NAVEGACIÓN DEL PROTOCOLO**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("⏮️ PASO ANTERIOR", 
                        disabled=self.current_step == 0, use_container_width=True):
                self.current_step = max(0, self.current_step - 1)
                st.rerun()
        
        with col2:
            if st.button("⏭️ PASO SIGUIENTE", 
                        disabled=self.current_step >= len(self.steps) - 1, use_container_width=True):
                self.current_step = min(len(self.steps) - 1, self.current_step + 1)
                st.rerun()
        
        with col3:
            if st.button("🏠 INICIO", use_container_width=True):
                self.current_step = 0
                st.rerun()
        
        with col4:
            if st.button("📋 RESUMEN", use_container_width=True):
                st.session_state["show_summary"] = True
    
    def _execute_news_acopio(self):
        """Ejecuta el acopio de noticias."""
        with st.spinner("🔄 **Acopiando noticias...**"):
            try:
                # Ejecutar pipeline manual
                df_raw, df_sel, logs = _run_pipeline_manual()
                
                # Guardar en sesión
                st.session_state["news_raw_df"] = df_raw.copy()
                st.session_state["news_selected_df"] = df_sel.copy()
                st.session_state["pipeline_logs"] = logs.copy()
                
                # Verificar mínimo de noticias
                if len(df_sel) >= 50:
                    st.success(f"✅ **Acopio completado exitosamente!** {len(df_sel)} noticias recolectadas")
                    self.current_step = 1
                    st.rerun()
                else:
                    st.warning(f"⚠️ **Solo se recolectaron {len(df_sel)} noticias. Se requieren mínimo 50.**")
                    
            except Exception as e:
                st.error(f"❌ **Error en acopio:** {str(e)}")
    
    def _execute_t70_mapping(self, df_sel):
        """Ejecuta el mapeo T70."""
        with st.spinner("🔄 **Ejecutando mapeo T70...**"):
            try:
                # Agrupar por categorías
                category_groups = _group_news_by_category(df_sel)
                
                if not category_groups:
                    st.error("❌ **No se pudieron agrupar las categorías**")
                    return
                
                # Mapear a T70
                t70_mapping = _map_categories_to_t70(category_groups)
                
                if not t70_mapping:
                    st.error("❌ **No se pudo mapear a T70**")
                    return
                
                # Guardar en sesión
                st.session_state["t70_mapping"] = t70_mapping
                
                st.success(f"✅ **Mapeo T70 completado!** {len(t70_mapping)} categorías mapeadas")
                
            except Exception as e:
                st.error(f"❌ **Error en mapeo T70:** {str(e)}")
    
    def _execute_gematria_analysis(self):
        """Ejecuta el análisis de Gematría."""
        with st.spinner("🔄 **Ejecutando análisis Gematría...**"):
            try:
                t70_mapping = st.session_state["t70_mapping"]
                
                # Preparar datos para GEM
                gem_data, _ = _prepare_news_for_capas(t70_mapping)
                
                if gem_data.empty:
                    st.error("❌ **No se pudieron preparar datos para Gematría**")
                    return
                
                # Guardar en sesión
                st.session_state["gem_results"] = gem_data
                
                st.success(f"✅ **Análisis Gematría completado!** {len(gem_data)} noticias procesadas")
                
            except Exception as e:
                st.error(f"❌ **Error en análisis Gematría:** {str(e)}")
    
    def _execute_subliminal_analysis(self):
        """Ejecuta el análisis Subliminal."""
        with st.spinner("🔄 **Ejecutando análisis Subliminal...**"):
            try:
                t70_mapping = st.session_state["t70_mapping"]
                
                # Preparar datos para SUB
                _, sub_data = _prepare_news_for_capas(t70_mapping)
                
                if sub_data.empty:
                    st.error("❌ **No se pudieron preparar datos para Subliminal**")
                    return
                
                # Guardar en sesión
                st.session_state["sub_results"] = sub_data
                
                st.success(f"✅ **Análisis Subliminal completado!** {len(sub_data)} noticias procesadas")
                
            except Exception as e:
                st.error(f"❌ **Error en análisis Subliminal:** {str(e)}")
    
    def _show_acopio_kpis(self):
        """Muestra KPIs del acopio."""
        df_sel = st.session_state["news_selected_df"]
        logs = st.session_state["pipeline_logs"]
        
        st.markdown("#### 📊 **KPIs DEL ACOPIO**")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Fuentes", len(logs.get("sources", [])))
        with col2:
            st.metric("Noticias Brutas", len(st.session_state["news_raw_df"]))
        with col3:
            st.metric("Noticias Seleccionadas", len(df_sel))
        with col4:
            st.metric("Ventana (h)", logs.get("recency_hours_used", 72))
        with col5:
            st.metric("Tiempo (s)", logs.get("elapsed_sec", 0))
    
    def _show_acopio_news(self):
        """Muestra las noticias del acopio."""
        df_sel = st.session_state["news_selected_df"]
        
        st.markdown("#### 📰 **NOTICIAS ACOPIADAS**")
        
        # Mostrar tabla principal
        display_cols = ["titular", "fuente", "_score_es"]
        if "_categoria_emocional" in df_sel.columns:
            display_cols.insert(1, "_categoria_emocional")
        if "_nivel_impacto" in df_sel.columns:
            display_cols.append("_nivel_impacto")
        
        st.dataframe(df_sel[display_cols], use_container_width=True, hide_index=True)
    
    def _check_completion_status(self):
        """Verifica el estado de completitud de todos los pasos."""
        status = {
            "acopio": "news_selected_df" in st.session_state and not st.session_state["news_selected_df"].empty,
            "categorizacion": "_categoria_emocional" in st.session_state.get("news_selected_df", pd.DataFrame()).columns,
            "t70": "t70_mapping" in st.session_state and st.session_state["t70_mapping"],
            "gematria": "gem_results" in st.session_state and not st.session_state["gem_results"].empty,
            "subliminal": "sub_results" in st.session_state and not st.session_state["sub_results"].empty
        }
        
        status["all_complete"] = all(status.values())
        return status
    
    def _show_completion_status(self, status):
        """Muestra el estado de completitud de los pasos."""
        st.markdown("#### 📋 **ESTADO DE COMPLETITUD**")
        
        steps_info = [
            ("🔍 Acopio", status["acopio"]),
            ("📊 Categorización", status["categorizacion"]),
            ("🔢 Mapeo T70", status["t70"]),
            ("🔡 Gematría", status["gematria"]),
            ("🧠 Subliminal", status["subliminal"])
        ]
        
        for step_name, completed in steps_info:
            if completed:
                st.success(f"✅ {step_name}")
            else:
                st.error(f"❌ {step_name}")
    
    def _show_protocol_summary(self):
        """Muestra el resumen del protocolo."""
        st.markdown("#### 📊 **RESUMEN DEL PROTOCOLO**")
        
        # Resumen por paso
        summary_data = {
            "Paso": ["Acopio", "Categorización", "T70", "Gematría", "Subliminal"],
            "Estado": ["✅ Completado", "✅ Completado", "✅ Completado", "✅ Completado", "✅ Completado"],
            "Noticias": [
                len(st.session_state["news_selected_df"]),
                st.session_state["news_selected_df"]["_categoria_emocional"].nunique(),
                len(st.session_state["t70_mapping"]),
                len(st.session_state["gem_results"]),
                len(st.session_state["sub_results"])
            ]
        }
        
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    
    def _show_export_options(self):
        """Muestra opciones de exportación."""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Exportar Todo (ZIP)", use_container_width=True):
                st.info("Funcionalidad de exportación ZIP en desarrollo")
        
        with col2:
            if st.button("📊 Resumen Pipeline", use_container_width=True):
                _show_pipeline_summary(
                    st.session_state["news_raw_df"],
                    st.session_state["news_selected_df"],
                    st.session_state["pipeline_logs"]
                )
        
        with col3:
            if st.button("📰 Detalles Noticias", use_container_width=True):
                _show_news_selection_details(st.session_state["news_selected_df"])
    
    def _reset_protocol(self):
        """Reinicia el protocolo."""
        # Limpiar variables de sesión
        keys_to_clear = [
            "news_raw_df", "news_selected_df", "pipeline_logs",
            "t70_mapping", "gem_results", "sub_results",
            "show_kpis", "show_news", "show_t70", "show_gem", "show_sub"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Resetear paso actual
        self.current_step = 0
        
        st.success("🔄 **Protocolo reiniciado correctamente**")

# Instancia global
news_interface = NewsInterface()

