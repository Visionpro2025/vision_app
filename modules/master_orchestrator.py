# modules/master_orchestrator.py — Orquestador Maestro Unificado
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import traceback

# Importar todos los módulos
try:
    from .noticias_module import NoticiasModule
    from .gematria_module import GematriaAnalyzer
    from .subliminal_module import SubliminalModule
    from .t70_module import T70Module
    from .quantum_layer import QuantumLayer
    from .series_assembler import EnhancedSeriesAssembler
    from .force_panel import ForcePanel
    from .closer import EnhancedCloser
    from .pattern_blocker import PatternBlocker
    from .historical_analysis import HistoricalAnalyzer
    from .auto_corrector import AutoCorrector
    from .orchestrator import ProtocolOrchestrator
except ImportError:
    # Fallback si algún módulo no está disponible
    NoticiasModule = None
    GematriaAnalyzer = None
    SubliminalModule = None
    T70Module = None
    QuantumLayer = None
    EnhancedSeriesAssembler = None
    ForcePanel = None
    EnhancedCloser = None
    PatternBlocker = None
    HistoricalAnalyzer = None
    AutoCorrector = None
    ProtocolOrchestrator = None

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS"
MASTER_LOGS = RUNS / "MASTER_LOGS"
MASTER_LOGS.mkdir(parents=True, exist_ok=True)

class MasterOrchestrator:
    def __init__(self):
        self.modules_status = {}
        self.protocol_history = []
        self.current_protocol = None
        self.execution_log = {}
        
        # Inicializar módulos disponibles
        self._initialize_modules()
        
        # Inicializar orquestador de protocolos
        self.protocol_orchestrator = ProtocolOrchestrator() if ProtocolOrchestrator else None
        
        # Inicializar sistema de corrección automática
        self.auto_corrector = AutoCorrector() if AutoCorrector else None
        
        # Inicializar analizador histórico
        self.historical_analyzer = HistoricalAnalyzer() if HistoricalAnalyzer else None
    
    def _initialize_modules(self):
        """Inicializa todos los módulos disponibles."""
        self.modules_status = {
            "noticias": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": NoticiasModule is not None,
                "version": "1.0.0"
            },
            "gematria": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": GematriaAnalyzer is not None,
                "version": "1.0.0"
            },
            "subliminal": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": SubliminalModule is not None,
                "version": "1.0.0"
            },
            "t70": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": T70Module is not None,
                "version": "1.0.0"
            },
            "quantum": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": QuantumLayer is not None,
                "version": "1.0.0"
            },
            "assembler": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": EnhancedSeriesAssembler is not None,
                "version": "1.0.0"
            },
            "force_panel": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": ForcePanel is not None,
                "version": "1.0.0"
            },
            "closer": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": EnhancedCloser is not None,
                "version": "1.0.0"
            },
            "pattern_blocker": {
                "module": None,  # Se inicializará cuando sea necesario
                "available": PatternBlocker is not None,
                "version": "1.0.0"
            }
        }
    
    def get_system_status(self) -> Dict:
        """Obtiene el estado completo del sistema."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_modules": len(self.modules_status),
            "available_modules": sum(1 for m in self.modules_status.values() if m["available"]),
            "modules_details": {},
            "system_health": "healthy"
        }
        
        # Detalles de cada módulo
        for module_name, module_info in self.modules_status.items():
            status["modules_details"][module_name] = {
                "available": module_info["available"],
                "version": module_info["version"],
                "status": "active" if module_info["available"] else "missing"
            }
        
        # Evaluar salud del sistema
        missing_modules = [name for name, info in self.modules_status.items() if not info["available"]]
        if len(missing_modules) > 3:
            status["system_health"] = "critical"
        elif len(missing_modules) > 1:
            status["system_health"] = "warning"
        
        return status
    
    def get_module(self, module_name: str):
        """Obtiene un módulo específico, inicializándolo si es necesario."""
        if module_name not in self.modules_status:
            return None
        
        module_info = self.modules_status[module_name]
        
        # Si el módulo no está disponible, retornar None
        if not module_info["available"]:
            return None
        
        # Si el módulo no está inicializado, inicializarlo
        if module_info["module"] is None:
            try:
                if module_name == "noticias" and NoticiasModule:
                    module_info["module"] = NoticiasModule()
                elif module_name == "gematria" and GematriaAnalyzer:
                    module_info["module"] = GematriaAnalyzer()
                elif module_name == "subliminal" and SubliminalModule:
                    module_info["module"] = SubliminalModule()
                elif module_name == "t70" and T70Module:
                    module_info["module"] = T70Module()
                elif module_name == "quantum" and QuantumLayer:
                    module_info["module"] = QuantumLayer()
                elif module_name == "assembler" and EnhancedSeriesAssembler:
                    module_info["module"] = EnhancedSeriesAssembler()
                elif module_name == "force_panel" and ForcePanel:
                    module_info["module"] = ForcePanel()
                elif module_name == "closer" and EnhancedCloser:
                    module_info["module"] = EnhancedCloser()
                elif module_name == "pattern_blocker" and PatternBlocker:
                    module_info["module"] = PatternBlocker()
            except Exception as e:
                st.error(f"Error inicializando módulo {module_name}: {e}")
                return None
        
        return module_info["module"]
    
    def execute_complete_protocol(self, protocol_name: str = "PROTOCOLO_COMPLETO_NOTICIAS") -> Dict:
        """Ejecuta el protocolo completo unificado."""
        protocol_start = datetime.now()
        
        # Inicializar log de ejecución
        self.execution_log = {
            "protocol_name": protocol_name,
            "start_time": protocol_start.isoformat(),
            "expected_steps": [
                "acopio_noticias",
                "analisis_historico",
                "categorizacion_emocional",
                "mapeo_t70",
                "analisis_gematria",
                "analisis_subliminal",
                "analisis_cuantico",
                "ensamblaje_series",
                "validacion_patrones",
                "analisis_fuerza",
                "cierre_protocolo"
            ],
            "completed_steps": [],
            "failed_steps": [],
            "step_errors": {},
            "dataframes": {},
            "quality_metrics": {},
            "expected_files": [],
            "required_columns": {},
            "required_modules": list(self.modules_status.keys()),
            "available_modules": [name for name, info in self.modules_status.items() if info["available"]],
            "module_versions": {name: info["version"] for name, info in self.modules_status.items()}
        }
        
        try:
            # PASO 1: Acopio de Noticias
            st.info("🚀 **PASO 1: Iniciando Acopio de Noticias**")
            news_result = self._execute_news_acopio()
            if news_result["success"]:
                self.execution_log["completed_steps"].append("acopio_noticias")
                self.execution_log["dataframes"]["news_raw"] = {
                    "available": True,
                    "empty": news_result["raw_news"].empty,
                    "columns": list(news_result["raw_news"].columns) if not news_result["raw_news"].empty else []
                }
                self.execution_log["dataframes"]["news_selected"] = {
                    "available": True,
                    "empty": news_result["selected_news"].empty,
                    "columns": list(news_result["selected_news"].columns) if not news_result["selected_news"].empty else []
                }
                self.execution_log["quality_metrics"]["actual_news_count"] = len(news_result["selected_news"])
                self.execution_log["quality_metrics"]["min_news_required"] = 50
            else:
                self.execution_log["failed_steps"].append("acopio_noticias")
                self.execution_log["step_errors"]["acopio_noticias"] = news_result["error"]
            
            # PASO 2: Análisis Histórico
            st.info("📅 **PASO 2: Ejecutando Análisis Histórico**")
            if self.historical_analyzer and not news_result["selected_news"].empty:
                historical_result = self._execute_historical_analysis(news_result["selected_news"])
                if historical_result["success"]:
                    self.execution_log["completed_steps"].append("analisis_historico")
                else:
                    self.execution_log["failed_steps"].append("analisis_historico")
                    self.execution_log["step_errors"]["analisis_historico"] = historical_result["error"]
            else:
                st.warning("⚠️ Analizador histórico no disponible o sin noticias para analizar")
            
            # PASO 3: Categorización Emocional
            st.info("🧠 **PASO 3: Aplicando Categorización Emocional**")
            if not news_result["selected_news"].empty:
                categorization_result = self._execute_emotional_categorization(news_result["selected_news"])
                if categorization_result["success"]:
                    self.execution_log["completed_steps"].append("categorizacion_emocional")
                    categorized_news = categorization_result["categorized_news"]
                else:
                    self.execution_log["failed_steps"].append("categorizacion_emocional")
                    self.execution_log["step_errors"]["categorizacion_emocional"] = categorization_result["error"]
                    categorized_news = news_result["selected_news"]
            else:
                categorized_news = news_result["selected_news"]
            
            # PASO 4: Mapeo T70
            st.info("🔢 **PASO 4: Aplicando Mapeo T70**")
            if not categorized_news.empty:
                t70_result = self._execute_t70_mapping(categorized_news)
                if t70_result["success"]:
                    self.execution_log["completed_steps"].append("mapeo_t70")
                    t70_mapped_news = t70_result["mapped_news"]
                else:
                    self.execution_log["failed_steps"].append("mapeo_t70")
                    self.execution_log["step_errors"]["mapeo_t70"] = t70_result["error"]
                    t70_mapped_news = categorized_news
            else:
                t70_mapped_news = categorized_news
            
            # PASO 5: Análisis Gematría
            st.info("🔡 **PASO 5: Ejecutando Análisis Gematría**")
            if not t70_mapped_news.empty:
                gematria_result = self._execute_gematria_analysis(t70_mapped_news)
                if gematria_result["success"]:
                    self.execution_log["completed_steps"].append("analisis_gematria")
                else:
                    self.execution_log["failed_steps"].append("analisis_gematria")
                    self.execution_log["step_errors"]["analisis_gematria"] = gematria_result["error"]
            
            # PASO 6: Análisis Subliminal
            st.info("🧠 **PASO 6: Ejecutando Análisis Subliminal**")
            if not t70_mapped_news.empty:
                subliminal_result = self._execute_subliminal_analysis(t70_mapped_news)
                if subliminal_result["success"]:
                    self.execution_log["completed_steps"].append("analisis_subliminal")
                else:
                    self.execution_log["failed_steps"].append("analisis_subliminal")
                    self.execution_log["step_errors"]["analisis_subliminal"] = subliminal_result["error"]
            
            # PASO 7: Análisis Cuántico
            st.info("🔮 **PASO 7: Ejecutando Análisis Cuántico**")
            if self.modules_status["quantum"]["available"]:
                quantum_result = self._execute_quantum_analysis(t70_mapped_news)
                if quantum_result["success"]:
                    self.execution_log["completed_steps"].append("analisis_cuantico")
                else:
                    self.execution_log["failed_steps"].append("analisis_cuantico")
                    self.execution_log["step_errors"]["analisis_cuantico"] = quantum_result["error"]
            else:
                st.warning("⚠️ Módulo cuántico no disponible")
            
            # PASO 8: Ensamblaje de Series
            st.info("⚙️ **PASO 8: Ensamblando Series**")
            if self.modules_status["assembler"]["available"]:
                assembler_result = self._execute_series_assembler(t70_mapped_news)
                if assembler_result["success"]:
                    self.execution_log["completed_steps"].append("ensamblaje_series")
                else:
                    self.execution_log["failed_steps"].append("ensamblaje_series")
                    self.execution_log["step_errors"]["ensamblaje_series"] = assembler_result["error"]
            else:
                st.warning("⚠️ Ensamblador no disponible")
            
            # PASO 9: Validación de Patrones
            st.info("🚫 **PASO 9: Validando Patrones**")
            if self.modules_status["pattern_blocker"]["available"]:
                pattern_result = self._execute_pattern_validation(t70_mapped_news)
                if pattern_result["success"]:
                    self.execution_log["completed_steps"].append("validacion_patrones")
                else:
                    self.execution_log["failed_steps"].append("validacion_patrones")
                    self.execution_log["step_errors"]["validacion_patrones"] = pattern_result["error"]
            else:
                st.warning("⚠️ Validador de patrones no disponible")
            
            # PASO 10: Análisis de Fuerza
            st.info("💪 **PASO 10: Analizando Fuerza Comparada**")
            if self.modules_status["force_panel"]["available"]:
                force_result = self._execute_force_analysis(t70_mapped_news)
                if force_result["success"]:
                    self.execution_log["completed_steps"].append("analisis_fuerza")
                else:
                    self.execution_log["failed_steps"].append("analisis_fuerza")
                    self.execution_log["step_errors"]["analisis_fuerza"] = force_result["error"]
            else:
                st.warning("⚠️ Panel de fuerza no disponible")
            
            # PASO 11: Cierre del Protocolo
            st.info("🔒 **PASO 11: Cerrando Protocolo**")
            if self.modules_status["closer"]["available"]:
                closer_result = self._execute_protocol_closure(protocol_name)
                if closer_result["success"]:
                    self.execution_log["completed_steps"].append("cierre_protocolo")
                else:
                    self.execution_log["failed_steps"].append("cierre_protocolo")
                    self.execution_log["step_errors"]["cierre_protocolo"] = closer_result["error"]
            else:
                st.warning("⚠️ Cerrador no disponible")
            
            # Finalizar protocolo
            protocol_end = datetime.now()
            self.execution_log["end_time"] = protocol_end.isoformat()
            self.execution_log["duration_seconds"] = (protocol_end - protocol_start).total_seconds()
            
            # Ejecutar corrección automática si hay fallas
            if self.auto_corrector:
                st.info("🔧 **Ejecutando Corrección Automática**")
                failures = self.auto_corrector.detect_protocol_failures(protocol_name, self.execution_log)
                if failures:
                    st.warning(f"⚠️ Se detectaron {len(failures)} fallas en el protocolo")
                    corrections = self.auto_corrector.auto_correct_failures(failures, {})
                    if corrections["corrections_applied"] > 0:
                        st.success(f"✅ Se corrigieron automáticamente {corrections['corrections_applied']} fallas")
                    
                    # Generar reporte de corrección
                    correction_report = self.auto_corrector.generate_correction_report(protocol_name, failures, corrections)
                    self.execution_log["correction_report"] = correction_report
            
            # Guardar log de ejecución
            self._save_execution_log()
            
            # Actualizar historial
            self.protocol_history.append({
                "protocol_name": protocol_name,
                "start_time": protocol_start.isoformat(),
                "end_time": protocol_end.isoformat(),
                "success_rate": len(self.execution_log["completed_steps"]) / len(self.execution_log["expected_steps"]),
                "total_steps": len(self.execution_log["expected_steps"]),
                "completed_steps": len(self.execution_log["completed_steps"]),
                "failed_steps": len(self.execution_log["failed_steps"])
            })
            
            st.success(f"🎉 **PROTOCOLO COMPLETADO** - {len(self.execution_log['completed_steps'])}/{len(self.execution_log['expected_steps'])} pasos exitosos")
            
            return {
                "success": True,
                "protocol_name": protocol_name,
                "completed_steps": len(self.execution_log["completed_steps"]),
                "total_steps": len(self.execution_log["expected_steps"]),
                "success_rate": len(self.execution_log["completed_steps"]) / len(self.execution_log["expected_steps"]),
                "execution_log": self.execution_log
            }
            
        except Exception as e:
            st.error(f"❌ **ERROR CRÍTICO EN PROTOCOLO**: {str(e)}")
            self.execution_log["critical_error"] = str(e)
            self.execution_log["end_time"] = datetime.now().isoformat()
            self._save_execution_log()
            
            return {
                "success": False,
                "error": str(e),
                "execution_log": self.execution_log
            }
    
    def _execute_news_acopio(self) -> Dict:
        """Ejecuta el acopio de noticias."""
        try:
            if not self.modules_status["noticias"]["available"]:
                return {"success": False, "error": "Módulo de noticias no disponible"}
            
            noticias_module = self.modules_status["noticias"]["module"]
            
            # Ejecutar pipeline de noticias
            result = noticias_module._run_pipeline_manual()
            
            if result and "news_selected_df" in st.session_state:
                selected_news = st.session_state["news_selected_df"]
                raw_news = st.session_state.get("news_raw_df", pd.DataFrame())
                
                return {
                    "success": True,
                    "selected_news": selected_news,
                    "raw_news": raw_news,
                    "message": f"Acopio exitoso: {len(selected_news)} noticias seleccionadas"
                }
            else:
                return {"success": False, "error": "No se pudo obtener noticias del pipeline"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_historical_analysis(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta análisis histórico."""
        try:
            if not self.historical_analyzer:
                return {"success": False, "error": "Analizador histórico no disponible"}
            
            # Generar reporte histórico completo
            historical_report = self.historical_analyzer.generate_historical_report(news_df)
            
            # Guardar reporte
            report_file = MASTER_LOGS / f"historical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(historical_report, f, indent=2, ensure_ascii=False)
            
            return {
                "success": True,
                "report": historical_report,
                "report_file": str(report_file),
                "message": "Análisis histórico completado exitosamente"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_emotional_categorization(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta categorización emocional."""
        try:
            if not self.modules_status["noticias"]["available"]:
                return {"success": False, "error": "Módulo de noticias no disponible"}
            
            noticias_module = self.modules_status["noticias"]["module"]
            
            # Aplicar categorización emocional
            if hasattr(noticias_module, '_add_emotional_categories'):
                categorized_df = noticias_module._add_emotional_categories(news_df.copy())
                
                # Balancear categorías si está habilitado
                if hasattr(noticias_module, '_balance_categories'):
                    categorized_df = noticias_module._balance_categories(categorized_df)
                
                return {
                    "success": True,
                    "categorized_news": categorized_df,
                    "message": f"Categorización exitosa: {len(categorized_df)} noticias categorizadas"
                }
            else:
                return {"success": False, "error": "Función de categorización emocional no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_t70_mapping(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta mapeo T70."""
        try:
            if not self.modules_status["t70"]["available"]:
                return {"success": False, "error": "Módulo T70 no disponible"}
            
            t70_module = self.modules_status["t70"]["module"]
            
            # Aplicar mapeo T70
            if hasattr(t70_module, 'map_news_to_t70'):
                mapped_df = t70_module.map_news_to_t70(news_df)
                
                return {
                    "success": True,
                    "mapped_news": mapped_df,
                    "message": f"Mapeo T70 exitoso: {len(mapped_df)} noticias mapeadas"
                }
            else:
                return {"success": False, "error": "Función de mapeo T70 no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_gematria_analysis(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta análisis gematría."""
        try:
            if not self.modules_status["gematria"]["available"]:
                return {"success": False, "error": "Módulo de gematría no disponible"}
            
            gematria_module = self.modules_status["gematria"]["module"]
            
            # Ejecutar análisis gematría
            if hasattr(gematria_module, 'analyze'):
                gematria_result = gematria_module.analyze(news_df)
                
                return {
                    "success": True,
                    "result": gematria_result,
                    "message": "Análisis gematría completado exitosamente"
                }
            else:
                return {"success": False, "error": "Función de análisis gematría no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_subliminal_analysis(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta análisis subliminal."""
        try:
            if not self.modules_status["subliminal"]["available"]:
                return {"success": False, "error": "Módulo subliminal no disponible"}
            
            subliminal_module = self.modules_status["subliminal"]["module"]
            
            # Ejecutar análisis subliminal
            if hasattr(subliminal_module, 'analyze_subliminal_messages'):
                subliminal_result = subliminal_module.analyze_subliminal_messages(news_df)
                
                return {
                    "success": True,
                    "result": subliminal_result,
                    "message": "Análisis subliminal completado exitosamente"
                }
            else:
                return {"success": False, "error": "Función de análisis subliminal no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_quantum_analysis(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta análisis cuántico."""
        try:
            quantum_module = self.modules_status["quantum"]["module"]
            
            # Ejecutar análisis cuántico
            if hasattr(quantum_module, 'compute_priors'):
                priors = quantum_module.compute_priors()
                
                return {
                    "success": True,
                    "priors": priors,
                    "message": "Análisis cuántico completado exitosamente"
                }
            else:
                return {"success": False, "error": "Función de análisis cuántico no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_series_assembler(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta ensamblador de series."""
        try:
            assembler_module = self.modules_status["assembler"]["module"]
            
            # Ejecutar ensamblaje
            if hasattr(assembler_module, 'assemble_series'):
                series_result = assembler_module.assemble_series(news_df)
                
                return {
                    "success": True,
                    "series": series_result,
                    "message": "Ensamblaje de series completado exitosamente"
                }
            else:
                return {"success": False, "error": "Función de ensamblaje no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_pattern_validation(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta validación de patrones."""
        try:
            pattern_module = self.modules_status["pattern_blocker"]["module"]
            
            # Validar patrones
            if hasattr(pattern_module, 'validate_news_patterns'):
                validation_result = pattern_module.validate_news_patterns(news_df)
                
                return {
                    "success": True,
                    "validation": validation_result,
                    "message": "Validación de patrones completada exitosamente"
                }
            else:
                return {"success": False, "error": "Función de validación de patrones no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_force_analysis(self, news_df: pd.DataFrame) -> Dict:
        """Ejecuta análisis de fuerza."""
        try:
            force_module = self.modules_status["force_panel"]["module"]
            
            # Analizar fuerza
            if hasattr(force_module, 'analyze_force_comparison'):
                force_result = force_module.analyze_force_comparison(news_df)
                
                return {
                    "success": True,
                    "force_analysis": force_result,
                    "message": "Análisis de fuerza completado exitosamente"
                }
            else:
                return {"success": False, "error": "Función de análisis de fuerza no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _execute_protocol_closure(self, protocol_name: str) -> Dict:
        """Ejecuta cierre del protocolo."""
        try:
            closer_module = self.modules_status["closer"]["module"]
            
            # Cerrar protocolo
            if hasattr(closer_module, 'close_protocol'):
                closure_result = closer_module.close_protocol(protocol_name, self.execution_log)
                
                return {
                    "success": True,
                    "closure": closure_result,
                    "message": "Protocolo cerrado exitosamente"
                }
            else:
                return {"success": False, "error": "Función de cierre no disponible"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_execution_log(self):
        """Guarda el log de ejecución."""
        try:
            log_file = MASTER_LOGS / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.execution_log, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # No fallar si no se puede guardar el log
    
    def get_protocol_summary(self) -> Dict:
        """Obtiene resumen del protocolo actual."""
        if not self.execution_log:
            return {"message": "No hay protocolo en ejecución"}
        
        return {
            "protocol_name": self.execution_log.get("protocol_name", "Desconocido"),
            "start_time": self.execution_log.get("start_time", "Desconocido"),
            "end_time": self.execution_log.get("end_time", "En ejecución"),
            "total_steps": len(self.execution_log.get("expected_steps", [])),
            "completed_steps": len(self.execution_log.get("completed_steps", [])),
            "failed_steps": len(self.execution_log.get("failed_steps", [])),
            "success_rate": len(self.execution_log.get("completed_steps", [])) / max(len(self.execution_log.get("expected_steps", [])), 1),
            "current_step": self.execution_log.get("current_step", "No especificado"),
            "quality_metrics": self.execution_log.get("quality_metrics", {})
        }
    
    def get_protocol_history(self) -> List[Dict]:
        """Obtiene historial de protocolos ejecutados."""
        return self.protocol_history

# Instancia global
master_orchestrator = MasterOrchestrator()
