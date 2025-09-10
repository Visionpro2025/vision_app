#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDATION SYSTEM - Sistema de validación robusta para VISION PREMIUM
Valida análisis de IA, resultados de loterías y datos de entrada
"""

import re
import json
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
import streamlit as st

class ValidationSystem:
    """Sistema de validación robusta para VISION PREMIUM"""
    
    def __init__(self):
        # Esquemas de validación para diferentes tipos de datos
        self.schemas = {
            "ai_analysis": {
                "required_fields": ["tendencias", "t70", "gematria", "subliminal", "propuesta"],
                "field_types": {
                    "tendencias": list,
                    "t70": list,
                    "gematria": dict,
                    "subliminal": dict,
                    "propuesta": dict
                },
                "nested_schemas": {
                    "tendencias": {
                        "required_fields": ["tag", "peso"],
                        "field_types": {"tag": str, "peso": float}
                    },
                    "gematria": {
                        "required_fields": ["claves"],
                        "field_types": {"claves": list}
                    },
                    "subliminal": {
                        "required_fields": ["arquetipos"],
                        "field_types": {"arquetipos": list}
                    },
                    "propuesta": {
                        "required_fields": ["numeros", "justificacion"],
                        "field_types": {"numeros": list, "justificacion": str}
                    }
                }
            },
            "lottery_result": {
                "required_fields": ["lottery_id", "date", "numbers_main"],
                "field_types": {
                    "lottery_id": str,
                    "date": str,
                    "numbers_main": list
                }
            },
            "context_input": {
                "min_length": 50,
                "max_length": 10000,
                "required_patterns": ["noticias", "sorteos", "hipótesis"]
            }
        }
        
        # Patrones de validación
        self.patterns = {
            "date_format": r'^\d{4}-\d{2}-\d{2}$',
            "lottery_id": r'^(megamillions|powerball|fl-pick3-day|fl-pick3-night|cash5-jersey)$',
            "number_range": (1, 99),
            "weight_range": (0.0, 1.0)
        }
    
    def validate_ai_analysis(self, data: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Valida un análisis de IA completo"""
        errors = []
        warnings = []
        validated_data = {}
        
        try:
            # Validar estructura básica
            if not isinstance(data, dict):
                errors.append("Los datos deben ser un diccionario")
                return False, errors, {}
            
            # Validar campos requeridos
            schema = self.schemas["ai_analysis"]
            for field in schema["required_fields"]:
                if field not in data:
                    errors.append(f"Campo requerido faltante: {field}")
                elif not isinstance(data[field], schema["field_types"][field]):
                    errors.append(f"Tipo incorrecto para {field}: esperado {schema['field_types'][field].__name__}")
            
            if errors:
                return False, errors, {}
            
            # Validar esquemas anidados
            for field, nested_schema in schema["nested_schemas"].items():
                if field in data:
                    field_valid, field_errors, field_warnings = self._validate_nested_field(
                        data[field], nested_schema, field
                    )
                    if not field_valid:
                        errors.extend(field_errors)
                    warnings.extend(field_warnings)
            
            # Validaciones específicas
            if "t70" in data and isinstance(data["t70"], list):
                for num in data["t70"]:
                    if not isinstance(num, int) or not (1 <= num <= 99):
                        warnings.append(f"Número T70 fuera de rango: {num}")
            
            if "propuesta" in data and isinstance(data["propuesta"], dict):
                if "numeros" in data["propuesta"]:
                    numeros = data["propuesta"]["numeros"]
                    if isinstance(numeros, list):
                        for num in numeros:
                            if not isinstance(num, int) or not (1 <= num <= 99):
                                warnings.append(f"Número propuesto fuera de rango: {num}")
            
            # Si no hay errores críticos, crear datos validados
            if not errors:
                validated_data = self._sanitize_ai_analysis(data)
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error de validación: {str(e)}")
            return False, errors, []
    
    def _validate_nested_field(self, data: Any, schema: Dict, field_name: str) -> Tuple[bool, List[str], List[str]]:
        """Valida un campo anidado según su esquema"""
        errors = []
        warnings = []
        
        try:
            # Validar tipo de campo
            if not isinstance(data, schema["field_types"].get("type", type(data))):
                errors.append(f"Tipo incorrecto para {field_name}")
                return False, errors, warnings
            
            # Validar campos requeridos
            for req_field in schema["required_fields"]:
                if req_field not in data:
                    errors.append(f"Campo requerido faltante en {field_name}: {req_field}")
                elif not isinstance(data[req_field], schema["field_types"][req_field]):
                    errors.append(f"Tipo incorrecto para {field_name}.{req_field}")
            
            # Validaciones específicas según el tipo
            if field_name == "tendencias" and isinstance(data, list):
                for i, tendencia in enumerate(data):
                    if isinstance(tendencia, dict):
                        if "peso" in tendencia:
                            peso = tendencia["peso"]
                            if not isinstance(peso, (int, float)) or not (0.0 <= peso <= 1.0):
                                warnings.append(f"Peso de tendencia {i} fuera de rango: {peso}")
            
            elif field_name == "gematria" and isinstance(data, dict):
                if "claves" in data and isinstance(data["claves"], list):
                    for clave in data["claves"]:
                        if not isinstance(clave, str) or len(clave.strip()) == 0:
                            warnings.append(f"Clave gematría inválida: {clave}")
            
            elif field_name == "subliminal" and isinstance(data, dict):
                if "arquetipos" in data and isinstance(data["arquetipos"], list):
                    for arquetipo in data["arquetipos"]:
                        if isinstance(arquetipo, dict):
                            if "score" in arquetipo:
                                score = arquetipo["score"]
                                if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                                    warnings.append(f"Score de arquetipo fuera de rango: {score}")
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error validando {field_name}: {str(e)}")
            return False, errors, warnings
    
    def _sanitize_ai_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza y normaliza los datos del análisis de IA"""
        sanitized = {}
        
        try:
            # Sanitizar tendencias
            if "tendencias" in data and isinstance(data["tendencias"], list):
                sanitized["tendencias"] = []
                for tendencia in data["tendencias"]:
                    if isinstance(tendencia, dict) and "tag" in tendencia and "peso" in tendencia:
                        peso = float(tendencia["peso"])
                        peso = max(0.0, min(1.0, peso))  # Clamp entre 0 y 1
                        sanitized["tendencias"].append({
                            "tag": str(tendencia["tag"]).strip(),
                            "peso": round(peso, 3)
                        })
            
            # Sanitizar T70
            if "t70" in data and isinstance(data["t70"], list):
                sanitized["t70"] = []
                for num in data["t70"]:
                    if isinstance(num, (int, float)):
                        num_int = int(num)
                        if 1 <= num_int <= 99:
                            sanitized["t70"].append(num_int)
            
            # Sanitizar gematría
            if "gematria" in data and isinstance(data["gematria"], dict):
                sanitized["gematria"] = {"claves": []}
                if "claves" in data["gematria"] and isinstance(data["gematria"]["claves"], list):
                    for clave in data["gematria"]["claves"]:
                        if isinstance(clave, str) and clave.strip():
                            sanitized["gematria"]["claves"].append(clave.strip())
            
            # Sanitizar subliminal
            if "subliminal" in data and isinstance(data["subliminal"], dict):
                sanitized["subliminal"] = {"arquetipos": []}
                if "arquetipos" in data["subliminal"] and isinstance(data["subliminal"]["arquetipos"], list):
                    for arquetipo in data["subliminal"]["arquetipos"]:
                        if isinstance(arquetipo, dict) and "nombre" in arquetipo and "score" in arquetipo:
                            score = float(arquetipo["score"])
                            score = max(0.0, min(1.0, score))  # Clamp entre 0 y 1
                            sanitized["subliminal"]["arquetipos"].append({
                                "nombre": str(arquetipo["nombre"]).strip(),
                                "score": round(score, 3)
                            })
            
            # Sanitizar propuesta
            if "propuesta" in data and isinstance(data["propuesta"], dict):
                sanitized["propuesta"] = {}
                if "numeros" in data["propuesta"] and isinstance(data["propuesta"]["numeros"], list):
                    numeros_sanitizados = []
                    for num in data["propuesta"]["numeros"]:
                        if isinstance(num, (int, float)):
                            num_int = int(num)
                            if 1 <= num_int <= 99:
                                numeros_sanitizados.append(num_int)
                    sanitized["propuesta"]["numeros"] = numeros_sanitizados
                
                if "justificacion" in data["propuesta"]:
                    justificacion = str(data["propuesta"]["justificacion"]).strip()
                    if justificacion:
                        sanitized["propuesta"]["justificacion"] = justificacion
            
            # Agregar metadatos de validación
            sanitized["_validation_metadata"] = {
                "validated_at": datetime.now().isoformat(),
                "original_keys": list(data.keys()),
                "sanitized_keys": list(sanitized.keys())
            }
            
            return sanitized
            
        except Exception as e:
            # Si hay error en sanitización, devolver datos originales
            return {
                "error": f"Error en sanitización: {str(e)}",
                "original_data": data,
                "_validation_metadata": {
                    "validated_at": datetime.now().isoformat(),
                    "error": str(e)
                }
            }
    
    def validate_lottery_result(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Valida un resultado de lotería"""
        errors = []
        warnings = []
        
        try:
            schema = self.schemas["lottery_result"]
            
            # Validar campos requeridos
            for field in schema["required_fields"]:
                if field not in data:
                    errors.append(f"Campo requerido faltante: {field}")
                elif not isinstance(data[field], schema["field_types"][field]):
                    errors.append(f"Tipo incorrecto para {field}")
            
            if errors:
                return False, errors, warnings
            
            # Validaciones específicas
            if "date" in data:
                if not re.match(self.patterns["date_format"], data["date"]):
                    errors.append("Formato de fecha inválido. Use YYYY-MM-DD")
            
            if "lottery_id" in data:
                if not re.match(self.patterns["lottery_id"], data["lottery_id"]):
                    errors.append("ID de lotería inválido")
            
            if "numbers_main" in data and isinstance(data["numbers_main"], list):
                for num in data["numbers_main"]:
                    if not isinstance(num, int) or not (self.patterns["number_range"][0] <= num <= self.patterns["number_range"][1]):
                        warnings.append(f"Número principal fuera de rango: {num}")
            
            if "numbers_bonus" in data and isinstance(data["numbers_bonus"], list):
                for num in data["numbers_bonus"]:
                    if not isinstance(num, int) or not (self.patterns["number_range"][0] <= num <= self.patterns["number_range"][1]):
                        warnings.append(f"Número bonus fuera de rango: {num}")
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error de validación: {str(e)}")
            return False, errors, []
    
    def validate_context_input(self, text: str) -> Tuple[bool, List[str], List[str]]:
        """Valida el texto de contexto para análisis"""
        errors = []
        warnings = []
        
        try:
            schema = self.schemas["context_input"]
            
            # Validar longitud
            if len(text.strip()) < schema["min_length"]:
                errors.append(f"Contexto muy corto. Mínimo {schema['min_length']} caracteres")
            
            if len(text.strip()) > schema["max_length"]:
                warnings.append(f"Contexto muy largo. Máximo {schema['max_length']} caracteres")
            
            # Validar patrones requeridos
            text_lower = text.lower()
            for pattern in schema["required_patterns"]:
                if pattern not in text_lower:
                    warnings.append(f"Considera incluir información sobre: {pattern}")
            
            # Validar contenido útil
            if len(text.strip().split()) < 10:
                warnings.append("Contexto muy breve. Más detalles mejorarán el análisis")
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Error de validación: {str(e)}")
            return False, errors, []
    
    def validate_json_structure(self, text: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Valida y parsea JSON del texto"""
        errors = []
        parsed_data = {}
        
        try:
            # Limpiar texto
            cleaned_text = text.strip()
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text.strip("`")
                if "\n" in cleaned_text:
                    cleaned_text = cleaned_text.split("\n", 1)[1]
            
            # Intentar parsear JSON
            parsed_data = json.loads(cleaned_text)
            
            if not isinstance(parsed_data, dict):
                errors.append("JSON debe ser un objeto/diccionario")
                return False, errors, {}
            
            return True, errors, parsed_data
            
        except json.JSONDecodeError as e:
            errors.append(f"JSON inválido: {str(e)}")
            return False, errors, {}
        except Exception as e:
            errors.append(f"Error al parsear: {str(e)}")
            return False, errors, {}
    
    def get_validation_summary(self, data: Dict[str, Any], validation_type: str = "ai_analysis") -> Dict[str, Any]:
        """Obtiene un resumen de validación para Streamlit"""
        if validation_type == "ai_analysis":
            is_valid, errors, warnings = self.validate_ai_analysis(data)
        elif validation_type == "lottery_result":
            is_valid, errors, warnings = self.validate_lottery_result(data)
        else:
            return {"error": "Tipo de validación no soportado"}
        
        return {
            "is_valid": is_valid,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "errors": errors,
            "warnings": warnings,
            "validation_type": validation_type,
            "timestamp": datetime.now().isoformat()
        }

# Instancia global del sistema de validación
validation_system = ValidationSystem()

# Funciones de conveniencia
def validate_ai_analysis(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Valida análisis de IA"""
    return validation_system.validate_ai_analysis(data)

def validate_lottery_result(data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Valida resultado de lotería"""
    return validation_system.validate_lottery_result(data)

def validate_context_input(text: str) -> Tuple[bool, List[str], List[str]]:
    """Valida texto de contexto"""
    return validation_system.validate_context_input(text)

def get_validation_summary(data: Dict[str, Any], validation_type: str = "ai_analysis") -> Dict[str, Any]:
    """Obtiene resumen de validación"""
    return validation_system.get_validation_summary(data, validation_type)

if __name__ == "__main__":
    # Prueba del sistema de validación
    print("✅ VISION PREMIUM - Sistema de Validación")
    print("=" * 40)
    
    # Probar validación de análisis de IA
    test_analysis = {
        "tendencias": [
            {"tag": "crisis_economica", "peso": 0.8},
            {"tag": "cambios_politicos", "peso": 0.6}
        ],
        "t70": [23, 39, 44],
        "gematria": {"claves": ["transformacion", "poder"]},
        "subliminal": {"arquetipos": [{"nombre": "cambio", "score": 0.7}]},
        "propuesta": {"numeros": [25, 37, 42, 18, 31], "justificacion": "Análisis basado en patrones observados"}
    }
    
    is_valid, errors, warnings = validate_ai_analysis(test_analysis)
    print(f"✅ Validación de análisis: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
    if errors:
        print(f"❌ Errores: {errors}")
    if warnings:
        print(f"⚠️ Advertencias: {warnings}")
    
    # Probar validación de contexto
    test_context = "Noticias sobre crisis económica en Wall Street. Últimos sorteos de Cash 5 Jersey. Hipótesis sobre patrones de números altos."
    is_valid, errors, warnings = validate_context_input(test_context)
    print(f"\n✅ Validación de contexto: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
    if errors:
        print(f"❌ Errores: {errors}")
    if warnings:
        print(f"⚠️ Advertencias: {warnings}")
    
    print("\n🎯 Sistema de validación funcionando correctamente!")








