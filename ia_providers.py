#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA PROVIDERS - Motor de IA para VISION PREMIUM
Solo OpenAI API - Integrado con caché y validación
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar sistemas de caché y validación
try:
    from cache_manager import cache_ai_analysis, get_cached_ai_analysis
    from validation_system import validate_ai_analysis, validate_context_input
    CACHE_AND_VALIDATION_AVAILABLE = True
except ImportError:
    CACHE_AND_VALIDATION_AVAILABLE = False
    print("⚠️ Sistemas de caché y validación no disponibles")

def _ensure_json(text: str) -> Dict[str, Any]:
    """Asegura que el texto sea JSON válido"""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if "\n" in text:
            text = text.split("\n", 1)[1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: intentar extraer JSON del texto
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        # Si todo falla, crear estructura básica
        return {
            "error": "No se pudo parsear JSON",
            "raw_text": text[:200] + "..." if len(text) > 200 else text
        }

# Esquema JSON para el prompt de análisis
PROMPT_JSON_SCHEMA = (
    "Devuelve SOLO JSON válido con el esquema: "
    '{"tendencias":[{"tag":str,"peso":float}],"t70":[int],'
    '"gematria":{"claves":[str]},"subliminal":{"arquetipos":[{"nombre":str,"score":float}]},'
    '"propuesta":{"numeros":[int],"justificacion":str}}'
)

class OpenAIClient:
    """Cliente para OpenAI API con caché y validación"""

    def __init__(self):
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "sk-tu-clave-api-aqui":
            raise ValueError("❌ OPENAI_API_KEY no configurada. Edita el archivo .env")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "2000"))

    def analyze(self, contexto: str) -> Dict[str, Any]:
        """Analiza contexto usando OpenAI con caché y validación"""
        try:
            # VALIDACIÓN DE ENTRADA
            if CACHE_AND_VALIDATION_AVAILABLE:
                is_valid, errors, warnings = validate_context_input(contexto)
                if not is_valid:
                    return {
                        "error": f"Contexto inválido: {'; '.join(errors)}",
                        "warnings": warnings,
                        "provider": "openai",
                        "model": self.model
                    }

            # VERIFICAR CACHÉ
            if CACHE_AND_VALIDATION_AVAILABLE:
                # Generar clave de caché basada en el contexto
                import hashlib
                context_hash = hashlib.md5(contexto.encode()).hexdigest()
                cache_key = f"openai_{self.model}_{context_hash}"

                # Intentar obtener del caché
                cached_result = get_cached_ai_analysis(cache_key)
                if cached_result:
                    cached_result["_cached"] = True
                    cached_result["_cache_source"] = "openai_cache"
                    return cached_result

            # ANÁLISIS CON IA
            system_prompt = (
                "Eres el analista de Visión Premium, un sistema experto en análisis de loterías "
                "que combina noticias, gematría hebrea, patrones subliminales y algoritmos cuánticos. "
                "Analiza el contexto proporcionado y devuelve un análisis estructurado. "
                + PROMPT_JSON_SCHEMA
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": contexto}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result = response.choices[0].message.content
            parsed_result = _ensure_json(result)

            # VALIDACIÓN DE SALIDA
            if CACHE_AND_VALIDATION_AVAILABLE and "error" not in parsed_result:
                is_valid, errors, warnings = validate_ai_analysis(parsed_result)
                if not is_valid:
                    parsed_result["validation_errors"] = errors
                    parsed_result["validation_warnings"] = warnings
                    parsed_result["_validation_status"] = "failed"
                else:
                    parsed_result["_validation_status"] = "passed"
                    parsed_result["validation_warnings"] = warnings

                    # GUARDAR EN CACHÉ
                    cache_ai_analysis(parsed_result, cache_key)
                    parsed_result["_cached"] = False
                    parsed_result["_cache_key"] = cache_key

            parsed_result["provider"] = "openai"
            parsed_result["model"] = self.model
            return parsed_result

        except Exception as e:
            return {
                "error": f"Error en OpenAI API: {str(e)}",
                "provider": "openai",
                "model": self.model
            }

def get_ai() -> OpenAIClient:
    """Obtiene el cliente de OpenAI"""
    return OpenAIClient()

def get_available_models() -> Dict[str, list]:
    """Obtiene modelos disponibles de OpenAI"""
    return {
        "openai": [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "gpt-5-nano"
        ]
    }

def get_provider_info() -> Dict[str, Any]:
    """Obtiene información del proveedor actual"""
    return {
        "name": "OpenAI API",
        "type": "cloud",
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "status": "✅ Configurado" if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-tu-clave-api-aqui" else "❌ API Key faltante",
        "cache_enabled": CACHE_AND_VALIDATION_AVAILABLE,
        "validation_enabled": CACHE_AND_VALIDATION_AVAILABLE
    }

# Funciones de conveniencia
def analyze_with_ai(contexto: str) -> Dict[str, Any]:
    """Función de conveniencia para análisis directo con caché y validación"""
    ai = get_ai()
    return ai.analyze(contexto)

if __name__ == "__main__":
    # Prueba del sistema
    print("🧠 VISION PREMIUM - Motor de IA (Solo OpenAI)")
    print("=" * 60)

    try:
        info = get_provider_info()
        print(f"Proveedor: {info['name']}")
        print(f"Estado: {info['status']}")
        print(f"Modelo: {info.get('model', 'N/A')}")
        print(f"Caché habilitado: {'✅' if info.get('cache_enabled', False) else '❌'}")
        print(f"Validación habilitada: {'✅' if info.get('validation_enabled', False) else '❌'}")

    except Exception as e:
        print(f"❌ Error: {e}")

    if CACHE_AND_VALIDATION_AVAILABLE:
        print("\n✅ Sistemas de caché y validación disponibles")
    else:
        print("\n⚠️ Sistemas de caché y validación no disponibles")