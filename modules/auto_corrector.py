# modules/auto_corrector.py — Sistema de Corrección Automática
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import traceback

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "__RUNS"
LOGS_DIR = RUNS / "LOGS"
CORRECTION_DIR = RUNS / "CORRECTIONS"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CORRECTION_DIR.mkdir(parents=True, exist_ok=True)

class AutoCorrector:
    def __init__(self):
        self.correction_history = []
        self.failure_patterns = {}
        self.auto_correction_enabled = True
        
    def detect_protocol_failures(self, protocol_name: str, execution_log: Dict) -> List[Dict]:
        """Detecta fallas en protocolos basándose en logs de ejecución."""
        failures = []
        
        # Verificar integridad de datos
        data_failures = self._check_data_integrity(execution_log)
        failures.extend(data_failures)
        
        # Verificar completitud de pasos
        step_failures = self._check_step_completeness(execution_log)
        failures.extend(step_failures)
        
        # Verificar calidad de resultados
        quality_failures = self._check_result_quality(execution_log)
        failures.extend(quality_failures)
        
        # Verificar dependencias entre módulos
        dependency_failures = self._check_module_dependencies(execution_log)
        failures.extend(dependency_failures)
        
        return failures
    
    def _check_data_integrity(self, execution_log: Dict) -> List[Dict]:
        """Verifica integridad de los datos del protocolo."""
        failures = []
        
        # Verificar que existan los archivos esperados
        expected_files = execution_log.get("expected_files", [])
        for file_path in expected_files:
            if not Path(file_path).exists():
                failures.append({
                    "type": "data_integrity",
                    "severity": "high",
                    "description": f"Archivo esperado no encontrado: {file_path}",
                    "suggested_action": "Verificar ruta y permisos del archivo",
                    "auto_correctable": False
                })
        
        # Verificar que los DataFrames no estén vacíos
        dataframes = execution_log.get("dataframes", {})
        for df_name, df_info in dataframes.items():
            if df_info.get("empty", False):
                failures.append({
                    "type": "data_integrity",
                    "severity": "medium",
                    "description": f"DataFrame vacío: {df_name}",
                    "suggested_action": "Verificar fuente de datos y filtros aplicados",
                    "auto_correctable": True
                })
        
        # Verificar columnas requeridas
        required_columns = execution_log.get("required_columns", {})
        for df_name, columns in required_columns.items():
            df_info = dataframes.get(df_name, {})
            if df_info.get("available", False):
                missing_columns = set(columns) - set(df_info.get("columns", []))
                if missing_columns:
                    failures.append({
                        "type": "data_integrity",
                        "severity": "medium",
                        "description": f"Columnas faltantes en {df_name}: {missing_columns}",
                        "suggested_action": "Regenerar DataFrame con columnas requeridas",
                        "auto_correctable": True
                    })
        
        return failures
    
    def _check_step_completeness(self, execution_log: Dict) -> List[Dict]:
        """Verifica que todos los pasos del protocolo se hayan completado."""
        failures = []
        
        expected_steps = execution_log.get("expected_steps", [])
        completed_steps = execution_log.get("completed_steps", [])
        failed_steps = execution_log.get("failed_steps", [])
        
        # Pasos que no se ejecutaron
        missing_steps = set(expected_steps) - set(completed_steps) - set(failed_steps)
        for step in missing_steps:
            failures.append({
                "type": "step_completeness",
                "severity": "high",
                "description": f"Paso no ejecutado: {step}",
                "suggested_action": "Ejecutar paso faltante",
                "auto_correctable": True
            })
        
        # Pasos que fallaron
        for step in failed_steps:
            step_error = execution_log.get("step_errors", {}).get(step, "Error desconocido")
            failures.append({
                "type": "step_completeness",
                "severity": "high",
                "description": f"Paso falló: {step} - {step_error}",
                "suggested_action": "Reintentar paso con manejo de errores",
                "auto_correctable": True
            })
        
        return failures
    
    def _check_result_quality(self, execution_log: Dict) -> List[Dict]:
        """Verifica la calidad de los resultados del protocolo."""
        failures = []
        
        # Verificar métricas de calidad
        quality_metrics = execution_log.get("quality_metrics", {})
        
        # Verificar número mínimo de noticias
        min_news_required = quality_metrics.get("min_news_required", 50)
        actual_news_count = quality_metrics.get("actual_news_count", 0)
        if actual_news_count < min_news_required:
            failures.append({
                "type": "result_quality",
                "severity": "medium",
                "description": f"Noticias insuficientes: {actual_news_count}/{min_news_required}",
                "suggested_action": "Ejecutar acopio extra de noticias",
                "auto_correctable": True
            })
        
        # Verificar cobertura de categorías
        category_coverage = quality_metrics.get("category_coverage", {})
        min_category_coverage = quality_metrics.get("min_category_coverage", 0.8)
        if category_coverage:
            avg_coverage = sum(category_coverage.values()) / len(category_coverage)
            if avg_coverage < min_category_coverage:
                failures.append({
                    "type": "result_quality",
                    "severity": "low",
                    "description": f"Cobertura de categorías baja: {avg_coverage:.2f}",
                    "suggested_action": "Balancear distribución de categorías",
                    "auto_correctable": True
                })
        
        return failures
    
    def _check_module_dependencies(self, execution_log: Dict) -> List[Dict]:
        """Verifica dependencias entre módulos del protocolo."""
        failures = []
        
        # Verificar que los módulos requeridos estén disponibles
        required_modules = execution_log.get("required_modules", [])
        available_modules = execution_log.get("available_modules", [])
        
        missing_modules = set(required_modules) - set(available_modules)
        for module in missing_modules:
            failures.append({
                "type": "module_dependencies",
                "severity": "high",
                "description": f"Módulo requerido no disponible: {module}",
                "suggested_action": "Instalar o habilitar módulo faltante",
                "auto_correctable": False
            })
        
        # Verificar versiones de módulos
        module_versions = execution_log.get("module_versions", {})
        required_versions = execution_log.get("required_versions", {})
        
        for module, required_version in required_versions.items():
            actual_version = module_versions.get(module, "desconocida")
            if actual_version != required_version:
                failures.append({
                    "type": "module_dependencies",
                    "severity": "medium",
                    "description": f"Versión incorrecta de {module}: {actual_version} (requerida: {required_version})",
                    "suggested_action": "Actualizar módulo a versión requerida",
                    "auto_correctable": False
                })
        
        return failures
    
    def auto_correct_failures(self, failures: List[Dict], execution_context: Dict) -> Dict:
        """Intenta corregir automáticamente las fallas detectadas."""
        if not self.auto_correction_enabled:
            return {
                "corrections_applied": 0,
                "corrections_failed": 0,
                "remaining_failures": failures,
                "message": "Corrección automática deshabilitada"
            }
        
        corrections_applied = 0
        corrections_failed = 0
        remaining_failures = []
        
        for failure in failures:
            if failure.get("auto_correctable", False):
                try:
                    correction_result = self._apply_correction(failure, execution_context)
                    if correction_result.get("success", False):
                        corrections_applied += 1
                        # Registrar corrección exitosa
                        self._log_correction(failure, correction_result, True)
                    else:
                        corrections_failed += 1
                        remaining_failures.append(failure)
                        # Registrar corrección fallida
                        self._log_correction(failure, correction_result, False)
                except Exception as e:
                    corrections_failed += 1
                    remaining_failures.append(failure)
                    # Registrar error en corrección
                    self._log_correction(failure, {"error": str(e)}, False)
            else:
                remaining_failures.append(failure)
        
        return {
            "corrections_applied": corrections_applied,
            "corrections_failed": corrections_failed,
            "remaining_failures": remaining_failures,
            "message": f"Correcciones aplicadas: {corrections_applied}, Fallidas: {corrections_failed}"
        }
    
    def _apply_correction(self, failure: Dict, execution_context: Dict) -> Dict:
        """Aplica una corrección específica basada en el tipo de falla."""
        failure_type = failure.get("type", "")
        
        if failure_type == "data_integrity":
            return self._correct_data_integrity(failure, execution_context)
        elif failure_type == "step_completeness":
            return self._correct_step_completeness(failure, execution_context)
        elif failure_type == "result_quality":
            return self._correct_result_quality(failure, execution_context)
        else:
            return {"success": False, "message": f"Tipo de falla no soportado: {failure_type}"}
    
    def _correct_data_integrity(self, failure: Dict, execution_context: Dict) -> Dict:
        """Corrige fallas de integridad de datos."""
        description = failure.get("description", "")
        
        if "DataFrame vacío" in description:
            # Intentar regenerar DataFrame
            return self._regenerate_empty_dataframe(failure, execution_context)
        elif "Columnas faltantes" in description:
            # Intentar regenerar DataFrame con columnas requeridas
            return self._regenerate_dataframe_with_columns(failure, execution_context)
        else:
            return {"success": False, "message": "Falla de integridad no corregible automáticamente"}
    
    def _correct_step_completeness(self, failure: Dict, execution_context: Dict) -> Dict:
        """Corrige fallas de completitud de pasos."""
        description = failure.get("description", "")
        
        if "Paso no ejecutado" in description:
            # Intentar ejecutar paso faltante
            return self._execute_missing_step(failure, execution_context)
        elif "Paso falló" in description:
            # Intentar reintentar paso fallido
            return self._retry_failed_step(failure, execution_context)
        else:
            return {"success": False, "message": "Falla de completitud no corregible automáticamente"}
    
    def _correct_result_quality(self, failure: Dict, execution_context: Dict) -> Dict:
        """Corrige fallas de calidad de resultados."""
        description = failure.get("description", "")
        
        if "Noticias insuficientes" in description:
            # Ejecutar acopio extra
            return self._execute_extra_news_collection(failure, execution_context)
        elif "Cobertura de categorías baja" in description:
            # Balancear categorías
            return self._balance_news_categories(failure, execution_context)
        else:
            return {"success": False, "message": "Falla de calidad no corregible automáticamente"}
    
    def _regenerate_empty_dataframe(self, failure: Dict, execution_context: Dict) -> Dict:
        """Regenera un DataFrame vacío."""
        try:
            # Buscar en el contexto cómo regenerar el DataFrame
            df_name = failure.get("description", "").split(":")[0].strip()
            regeneration_function = execution_context.get("regeneration_functions", {}).get(df_name)
            
            if regeneration_function and callable(regeneration_function):
                result = regeneration_function()
                if result is not None and not result.empty:
                    return {"success": True, "message": f"DataFrame {df_name} regenerado exitosamente"}
            
            return {"success": False, "message": f"No se pudo regenerar DataFrame {df_name}"}
        except Exception as e:
            return {"success": False, "message": f"Error al regenerar DataFrame: {str(e)}"}
    
    def _regenerate_dataframe_with_columns(self, failure: Dict, execution_context: Dict) -> Dict:
        """Regenera DataFrame con columnas requeridas."""
        try:
            # Extraer información de columnas faltantes
            description = failure.get("description", "")
            df_name = description.split(":")[0].strip()
            missing_columns_str = description.split(":")[1].strip()
            missing_columns = eval(missing_columns_str)  # Convertir string a set
            
            # Buscar función de regeneración
            regeneration_function = execution_context.get("regeneration_functions", {}).get(df_name)
            
            if regeneration_function and callable(regeneration_function):
                result = regeneration_function(required_columns=list(missing_columns))
                if result is not None and not result.empty:
                    return {"success": True, "message": f"DataFrame {df_name} regenerado con columnas requeridas"}
            
            return {"success": False, "message": f"No se pudo regenerar DataFrame {df_name} con columnas requeridas"}
        except Exception as e:
            return {"success": False, "message": f"Error al regenerar DataFrame con columnas: {str(e)}"}
    
    def _execute_missing_step(self, failure: Dict, execution_context: Dict) -> Dict:
        """Ejecuta un paso faltante."""
        try:
            description = failure.get("description", "")
            step_name = description.split(":")[1].strip()
            
            # Buscar función de ejecución del paso
            step_functions = execution_context.get("step_functions", {})
            step_function = step_functions.get(step_name)
            
            if step_function and callable(step_function):
                result = step_function()
                if result:
                    return {"success": True, "message": f"Paso {step_name} ejecutado exitosamente"}
            
            return {"success": False, "message": f"No se pudo ejecutar paso {step_name}"}
        except Exception as e:
            return {"success": False, "message": f"Error al ejecutar paso: {str(e)}"}
    
    def _retry_failed_step(self, failure: Dict, execution_context: Dict) -> Dict:
        """Reintenta un paso fallido."""
        try:
            description = failure.get("description", "")
            step_name = description.split(":")[1].strip()
            
            # Buscar función de reintento
            retry_functions = execution_context.get("retry_functions", {})
            retry_function = retry_functions.get(step_name)
            
            if retry_function and callable(retry_function):
                result = retry_function()
                if result:
                    return {"success": True, "message": f"Paso {step_name} reintentado exitosamente"}
            
            return {"success": False, "message": f"No se pudo reintentar paso {step_name}"}
        except Exception as e:
            return {"success": False, "message": f"Error al reintentar paso: {str(e)}"}
    
    def _execute_extra_news_collection(self, failure: Dict, execution_context: Dict) -> Dict:
        """Ejecuta acopio extra de noticias."""
        try:
            # Buscar función de acopio extra
            extra_collection_function = execution_context.get("extra_collection_function")
            
            if extra_collection_function and callable(extra_collection_function):
                result = extra_collection_function()
                if result:
                    return {"success": True, "message": "Acopio extra de noticias ejecutado exitosamente"}
            
            return {"success": False, "message": "No se pudo ejecutar acopio extra de noticias"}
        except Exception as e:
            return {"success": False, "message": f"Error en acopio extra: {str(e)}"}
    
    def _balance_news_categories(self, failure: Dict, execution_context: Dict) -> Dict:
        """Balancea categorías de noticias."""
        try:
            # Buscar función de balanceo
            balance_function = execution_context.get("balance_function")
            
            if balance_function and callable(balance_function):
                result = balance_function()
                if result:
                    return {"success": True, "message": "Categorías de noticias balanceadas exitosamente"}
            
            return {"success": False, "message": "No se pudo balancear categorías de noticias"}
        except Exception as e:
            return {"success": False, "message": f"Error al balancear categorías: {str(e)}"}
    
    def _log_correction(self, failure: Dict, correction_result: Dict, success: bool):
        """Registra el resultado de una corrección."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "failure": failure,
            "correction_result": correction_result,
            "success": success
        }
        
        self.correction_history.append(log_entry)
        
        # Guardar en archivo
        try:
            log_file = CORRECTION_DIR / f"correction_log_{datetime.now().strftime('%Y%m%d')}.json"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []
            
            existing_logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # No fallar si no se puede guardar el log
    
    def generate_correction_report(self, protocol_name: str, failures: List[Dict], corrections: Dict) -> Dict:
        """Genera reporte completo de correcciones aplicadas."""
        return {
            "protocol_name": protocol_name,
            "timestamp": datetime.now().isoformat(),
            "total_failures": len(failures),
            "corrections_applied": corrections.get("corrections_applied", 0),
            "corrections_failed": corrections.get("corrections_failed", 0),
            "remaining_failures": len(corrections.get("remaining_failures", [])),
            "correction_success_rate": corrections.get("corrections_applied", 0) / max(len(failures), 1),
            "failures_details": failures,
            "corrections_details": corrections,
            "recommendations": self._generate_correction_recommendations(failures, corrections)
        }
    
    def _generate_correction_recommendations(self, failures: List[Dict], corrections: Dict) -> List[str]:
        """Genera recomendaciones basadas en las correcciones aplicadas."""
        recommendations = []
        
        remaining_failures = corrections.get("remaining_failures", [])
        
        if not remaining_failures:
            recommendations.append("✅ Todas las fallas fueron corregidas automáticamente")
        else:
            # Agrupar fallas por tipo
            failure_types = {}
            for failure in remaining_failures:
                failure_type = failure.get("type", "desconocido")
                if failure_type not in failure_types:
                    failure_types[failure_type] = []
                failure_types[failure_type].append(failure)
            
            for failure_type, type_failures in failure_types.items():
                count = len(type_failures)
                if count == 1:
                    recommendations.append(f"⚠️ 1 falla de tipo '{failure_type}' requiere intervención manual")
                else:
                    recommendations.append(f"⚠️ {count} fallas de tipo '{failure_type}' requieren intervención manual")
        
        # Recomendaciones específicas por tipo de falla
        for failure in remaining_failures:
            if failure.get("type") == "module_dependencies":
                recommendations.append("🔧 Verificar instalación y versiones de módulos requeridos")
            elif failure.get("type") == "data_integrity" and not failure.get("auto_correctable", False):
                recommendations.append("📁 Verificar permisos y rutas de archivos del sistema")
        
        return recommendations

# Instancia global
auto_corrector = AutoCorrector()

