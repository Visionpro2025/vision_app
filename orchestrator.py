#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCHESTRATOR - Orquestador controlado de App.Vision
Usa OpenAI Responses API con function-calling controlado
Solo ejecuta web_search si el usuario lo ordena explícitamente
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config import *
from tools import TOOL_IMPL

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Definición de herramientas para function-calling (schema JSON)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "gematria",
            "description": "Analiza series de sorteos con gematría y sugiere números basados en patrones numéricos esotéricos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "series": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de series de números de lotería como strings (ej: ['1,5,7,19,21', '3,14,22,44,69'])"
                    }
                },
                "required": ["series"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subliminal",
            "description": "Extrae pistas subliminales y patrones ocultos de un texto corto para análisis de loterías.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto a analizar para extraer pistas subliminales"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "quantum_analyzer",
            "description": "Evalúa correlaciones 'cuánticas' internas y patrones probabilísticos en datos de lotería.",
            "parameters": {
                "type": "object",
                "properties": {
                    "payload": {
                        "type": "object",
                        "description": "Datos para análisis cuántico (puede incluir números, fechas, contextos)"
                    }
                },
                "required": ["payload"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_sorteos",
            "description": "Busca sorteos internos por fecha en la base de datos local de App.Vision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha": {
                        "type": "string",
                        "description": "Fecha en formato YYYY-MM-DD para buscar sorteos"
                    }
                },
                "required": ["fecha"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Realiza búsqueda externa en web. SOLO usar si el usuario lo ordena explícitamente en su prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta de búsqueda para obtener información externa"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def is_web_search_authorized(user_goal: str) -> bool:
    """
    Verifica si el usuario autorizó explícitamente web_search en su prompt.
    
    Args:
        user_goal: Prompt del usuario
        
    Returns:
        True si web_search está autorizado, False en caso contrario
    """
    # Palabras clave que indican autorización explícita para búsqueda web
    authorization_keywords = [
        "busca en web",
        "buscar en internet",
        "consulta en línea",
        "web_search",
        "búsqueda externa",
        "buscar online",
        "consulta web",
        "internet search"
    ]
    
    user_goal_lower = user_goal.lower()
    return any(keyword in user_goal_lower for keyword in authorization_keywords)

def call_orchestrator(user_goal: str, context: Dict[str, Any] = None, model: str = None) -> str:
    """
    Llama al orquestador controlado con function-calling.
    
    Args:
        user_goal: Objetivo o consulta del usuario
        context: Contexto adicional (opcional)
        model: Modelo a usar (por defecto APP_MODEL)
        
    Returns:
        Respuesta del orquestador
    """
    model = model or APP_MODEL
    context = context or {}
    
    # Guardrail de presupuesto (aproximado por tokens de salida)
    max_tokens = APP_MAX_OUTPUT_TOKENS
    
    # Ajustar temperatura según el modelo
    if model == "gpt-5-nano":
        temperature = 1.0  # Valor por defecto para gpt-5-nano
    else:
        temperature = APP_TEMPERATURE
    
    logger.info(f"🎯 Iniciando orquestador controlado con modelo: {model}")
    logger.info(f"📝 Objetivo: {user_goal[:100]}...")
    
    # Verificar autorización para web_search
    web_search_authorized = is_web_search_authorized(user_goal)
    logger.info(f"🌐 Web search autorizado: {web_search_authorized}")
    
    # Reintentos básicos
    for attempt in range(APP_MAX_RETRIES):
        try:
            logger.info(f"🔄 Intento {attempt + 1}/{APP_MAX_RETRIES}")
            
            # Preparar input con contexto
            full_input = user_goal
            if context:
                full_input += f"\n\nContexto adicional: {json.dumps(context, ensure_ascii=False)}"
            
            # Llamada inicial con herramientas
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres el orquestador controlado de App.Vision. Solo usa herramientas internas (gematria, subliminal, quantum_analyzer, buscar_sorteos). Solo puedes usar web_search si el usuario lo ordena explícitamente en su prompt."},
                    {"role": "user", "content": full_input}
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                tools=TOOLS,
                tool_choice="auto"  # Permite que el modelo decida
            )
            
            # Procesar respuesta
            message = resp.choices[0].message
            
            # Si hay tool calls, procesarlos
            if message.tool_calls:
                logger.info(f"🔧 Ejecutando {len(message.tool_calls)} herramientas...")
                
                # Preparar mensajes para el bucle de tool-calling
                messages = [
                    {"role": "system", "content": "Eres el orquestador controlado de App.Vision. Procesa los resultados de las herramientas y continúa con el análisis."},
                    {"role": "user", "content": full_input},
                    {"role": "assistant", "content": message.content or "", "tool_calls": message.tool_calls}
                ]
                
                # Procesar cada tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments or "{}")
                    
                    logger.info(f"🔨 Ejecutando herramienta: {tool_name}")
                    logger.debug(f"📋 Argumentos: {tool_args}")
                    
                    # Verificar autorización para web_search
                    if tool_name == "web_search" and not web_search_authorized:
                        logger.warning(f"🚫 Web search no autorizado - rechazando llamada")
                        messages.append({
                            "role": "tool",
                            "content": json.dumps({
                                "error": "Web search no autorizado",
                                "message": "Solo puedo hacer búsquedas web si me lo ordenas explícitamente en tu prompt",
                                "tool": tool_name
                            }, ensure_ascii=False),
                            "tool_call_id": tool_call.id
                        })
                        continue
                    
                    try:
                        # Ejecutar herramienta
                        tool_result = TOOL_IMPL[tool_name](tool_args)
                        logger.info(f"✅ Herramienta {tool_name} completada")
                        logger.debug(f"📊 Resultado: {tool_result}")
                        
                        # Agregar resultado al contexto
                        messages.append({
                            "role": "tool",
                            "content": json.dumps(tool_result, ensure_ascii=False),
                            "tool_call_id": tool_call.id
                        })
                        
                    except Exception as e:
                        logger.error(f"❌ Error en herramienta {tool_name}: {e}")
                        messages.append({
                            "role": "tool",
                            "content": json.dumps({"error": str(e), "tool": tool_name}, ensure_ascii=False),
                            "tool_call_id": tool_call.id
                        })
                
                # Obtener respuesta final después de tool calls
                final_resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_completion_tokens=max_tokens
                )
                
                result = final_resp.choices[0].message.content
                logger.info("✅ Análisis completado con herramientas")
                
            else:
                result = message.content
                logger.info("✅ Análisis completado sin herramientas")
            
            # Verificar presupuesto (aproximado)
            estimated_cost = (max_tokens / 1000) * 0.002  # Aproximación
            if estimated_cost > APP_BUDGET_USD_PER_CALL:
                logger.warning(f"⚠️ Costo estimado ${estimated_cost:.4f} excede presupuesto ${APP_BUDGET_USD_PER_CALL}")
            
            return result or "No se pudo generar respuesta"
            
        except Exception as e:
            logger.error(f"❌ Error en intento {attempt + 1}: {e}")
            if attempt + 1 >= APP_MAX_RETRIES:
                raise Exception(f"Error después de {APP_MAX_RETRIES} intentos: {e}")
            
            # Esperar antes del siguiente intento
            wait_time = 0.8 * (attempt + 1)
            logger.info(f"⏳ Esperando {wait_time}s antes del siguiente intento...")
            time.sleep(wait_time)

def get_orchestrator_status() -> Dict[str, Any]:
    """Obtiene el estado del orquestador"""
    return {
        "model": APP_MODEL,
        "model_test": APP_MODEL_TEST,
        "max_tokens": APP_MAX_OUTPUT_TOKENS,
        "temperature": APP_TEMPERATURE,
        "budget_per_call": APP_BUDGET_USD_PER_CALL,
        "max_retries": APP_MAX_RETRIES,
        "tools_available": len(TOOL_IMPL),
        "tools_internas": ["gematria", "subliminal", "quantum_analyzer", "buscar_sorteos"],
        "tools_externas": ["web_search"],
        "web_search_control": "Solo si el usuario lo ordena explícitamente"
    }

if __name__ == "__main__":
    print("🎯 VISION PREMIUM - Orquestador Controlado")
    print("=" * 50)
    
    status = get_orchestrator_status()
    print(f"Modelo principal: {status['model']}")
    print(f"Modelo test: {status['model_test']}")
    print(f"Herramientas internas: {len(status['tools_internas'])}")
    print(f"Herramientas externas: {len(status['tools_externas'])}")
    print(f"Control web search: {status['web_search_control']}")
    
    # Prueba básica
    print("\n🧪 Prueba básica del orquestador...")
    try:
        result = call_orchestrator("Dime 'App.Vision orquestador controlado listo' y confirma que las herramientas internas están disponibles.")
        print(f"✅ Respuesta: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")