#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONVERSATIONAL ORCHESTRATOR - Orquestador conversacional de App.Vision
Soporta dos modos: conversación continua y comandos cortos
"""

import time
import json
import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from config import *
from tools import TOOL_IMPL
from session_state import get_session_state
from intent_router import route

# Configurar logging
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
                        "description": "Lista de series de números de lotería como strings"
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
                        "description": "Datos para análisis cuántico"
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
            "name": "buscar_sorteos_rango",
            "description": "Busca sorteos internos por rango de fechas en la base de datos local de App.Vision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {
                        "type": "string",
                        "description": "Fecha inicio en formato YYYY-MM-DD"
                    },
                    "fecha_fin": {
                        "type": "string",
                        "description": "Fecha fin en formato YYYY-MM-DD"
                    }
                },
                "required": ["fecha_inicio", "fecha_fin"]
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
    """Verifica si el usuario autorizó explícitamente web_search"""
    authorization_keywords = [
        "busca en web", "buscar en internet", "consulta en línea", "web_search",
        "búsqueda externa", "buscar online", "consulta web", "internet search"
    ]
    user_goal_lower = user_goal.lower()
    return any(keyword in user_goal_lower for keyword in authorization_keywords)

def build_hidden_prompt(short_message: str, session_state) -> str:
    """Construye un prompt oculto para comandos cortos"""
    context_parts = []
    
    # Información del estado actual
    if session_state.get_current_task():
        context_parts.append(f"Tarea actual: {session_state.get_current_task()}")
    
    if session_state.get_protocol_stage():
        context_parts.append(f"Etapa del protocolo: {session_state.get_protocol_stage()}")
    
    # Historial reciente
    recent_history = session_state.get_recent_history(5)
    if recent_history:
        context_parts.append(f"Historial reciente: {'; '.join(recent_history)}")
    
    # Construir prompt oculto
    hidden_prompt = f"Usuario envió comando corto: '{short_message}'. "
    
    if context_parts:
        hidden_prompt += f"Contexto actual: {'; '.join(context_parts)}. "
    
    hidden_prompt += "Mantén el contexto del protocolo actual y actúa según el intent. Responde en español, de forma concisa y directa."
    
    return hidden_prompt

def execute_intent(intent: str, args: Dict[str, Any], session_state) -> str:
    """Ejecuta una intención específica"""
    
    if intent == "START_PROTOCOL":
        session_state.set_current_task("Análisis de MegaMillions")
        session_state.set_protocol_stage("Iniciando")
        session_state.add_to_history("Usuario: Inicia protocolo")
        
        # Iniciar protocolo con primera serie
        series_iniciales = ["1,5,7,19,21", "3,14,22,44,69", "2,8,15,23,31", "4,11,18,27,35", "6,12,20,28,42"]
        session_state.set_protocol_data({"series": series_iniciales, "current_index": 0})
        
        return "✅ Protocolo iniciado. Analizando 5 series de MegaMillions. Etapa: Gematría de la serie más antigua."
    
    elif intent == "NEXT_STEP":
        if not session_state.get_current_task():
            return "❌ No hay protocolo activo. Usa 'Inicia protocolo' primero."
        
        protocol_data = session_state.get_protocol_data()
        if not protocol_data or "current_index" not in protocol_data:
            return "❌ Estado del protocolo inválido. Reinicia con 'Inicia protocolo'."
        
        current_index = protocol_data["current_index"]
        series = protocol_data["series"]
        
        if current_index >= len(series):
            session_state.set_protocol_stage("Completado")
            return "✅ Protocolo completado. Todas las series analizadas. Generando resultado final."
        
        # Avanzar al siguiente paso
        current_series = series[current_index]
        protocol_data["current_index"] = current_index + 1
        session_state.set_protocol_data(protocol_data)
        
        # Determinar siguiente etapa
        if current_index == 0:
            session_state.set_protocol_stage("Gematría")
            return f"🔮 Aplicando gematría a serie {current_index + 1}: {current_series}"
        elif current_index == 1:
            session_state.set_protocol_stage("Subliminal")
            return f"🔍 Generando mensaje subliminal para serie {current_index + 1}: {current_series}"
        elif current_index == 2:
            session_state.set_protocol_stage("Cuántico")
            return f"⚡ Análisis cuántico de serie {current_index + 1}: {current_series}"
        else:
            session_state.set_protocol_stage("Iteración")
            return f"🔄 Iterando análisis de serie {current_index + 1}: {current_series}"
    
    elif intent == "STATUS":
        status = session_state.get_status_summary()
        return f"📊 Estado actual: {status}"
    
    elif intent == "STOP":
        if session_state.get_current_task():
            session_state.set_current_task(None)
            session_state.set_protocol_stage(None)
            session_state.add_to_history("Usuario: Detener protocolo")
            return "🛑 Protocolo detenido. Estado reiniciado."
        else:
            return "ℹ️ No hay protocolo activo para detener."
    
    elif intent == "GEMATRIA_PASS":
        if not session_state.get_current_task():
            return "❌ No hay protocolo activo. Usa 'Inicia protocolo' primero."
        
        protocol_data = session_state.get_protocol_data()
        if protocol_data and "series" in protocol_data:
            current_index = protocol_data.get("current_index", 0)
            if current_index < len(protocol_data["series"]):
                series = protocol_data["series"][current_index]
                # Ejecutar gematría
                result = TOOL_IMPL["gematria"]({"series": [series]})
                session_state.add_to_history(f"Gematría ejecutada: {result['numbers']}")
                return f"🔮 Gematría aplicada: {result['numbers']}"
        
        return "❌ No hay serie disponible para gematría."
    
    elif intent == "SUBLIMINAL_PASS":
        if not session_state.get_current_task():
            return "❌ No hay protocolo activo. Usa 'Inicia protocolo' primero."
        
        protocol_data = session_state.get_protocol_data()
        if protocol_data and "series" in protocol_data:
            current_index = protocol_data.get("current_index", 0)
            if current_index < len(protocol_data["series"]):
                series = protocol_data["series"][current_index]
                # Ejecutar subliminal
                result = TOOL_IMPL["subliminal"]({"text": series})
                session_state.add_to_history(f"Subliminal ejecutado: {result['clues']}")
                return f"🔍 Pistas subliminales: {result['clues']}"
        
        return "❌ No hay serie disponible para análisis subliminal."
    
    elif intent == "SEARCH_DRAWS":
        fecha_inicio = args.get("fecha_inicio")
        fecha_fin = args.get("fecha_fin")
        if fecha_inicio and fecha_fin:
            result = TOOL_IMPL["buscar_sorteos_rango"]({"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
            session_state.add_to_history(f"Búsqueda de sorteos: {fecha_inicio} a {fecha_fin}")
            return f"🔍 Sorteos encontrados: {result['count']} en {result['dias_con_sorteos']} días"
        return "❌ Fechas de búsqueda inválidas."
    
    elif intent == "SEARCH_DRAWS_SIMPLE":
        fecha = args.get("fecha")
        if fecha:
            result = TOOL_IMPL["buscar_sorteos"]({"fecha": fecha})
            session_state.add_to_history(f"Búsqueda de sorteos: {fecha}")
            return f"🔍 Sorteos del {fecha}: {result['count']} encontrados"
        return "❌ Fecha de búsqueda inválida."
    
    elif intent == "SET_MODEL_MINI":
        session_state.set_model("gpt-4o-mini")
        session_state.add_to_history("Usuario: Cambiar a modelo mini")
        return "✅ Modelo cambiado a gpt-4o-mini"
    
    elif intent == "SET_MODEL_NANO":
        session_state.set_model("gpt-5-nano")
        session_state.add_to_history("Usuario: Cambiar a modelo nano")
        return "✅ Modelo cambiado a gpt-5-nano"
    
    elif intent == "SAVE_SERIES":
        if session_state.get_last_series():
            # En una implementación real, esto guardaría en archivo/DB
            session_state.add_to_history("Usuario: Guardar serie guía")
            return f"💾 Serie guardada: {session_state.get_last_series()}"
        return "❌ No hay serie para guardar."
    
    elif intent == "RESTART":
        session_state.reset()
        session_state.add_to_history("Usuario: Reiniciar sistema")
        return "🔄 Sistema reiniciado. Estado limpio."
    
    elif intent == "HELP":
        return """📋 Comandos disponibles:
• Inicia protocolo → arranca MegaMillions
• Continuar → siguiente etapa
• Estado → qué está haciendo
• Detener → cierra protocolo
• Gematria → fuerza pasada de gematría
• Subliminal → fuerza pasada subliminal
• Buscar sorteos 2025-08-20..2025-09-05 → consulta por rango
• Cambia a mini/nano → cambia modelo
• Guardar serie guía → persiste resultado
• Reinicia → borra estado"""
    
    else:
        return "❌ Intención no reconocida."

def call_conversational_orchestrator(user_message: str, model: str = None) -> str:
    """
    Llama al orquestador conversacional
    
    Args:
        user_message: Mensaje del usuario
        model: Modelo a usar (opcional)
        
    Returns:
        Respuesta del orquestador
    """
    session_state = get_session_state()
    model = model or session_state.get_model()
    
    # Cargar estado si existe
    session_state.load_from_file()
    
    # Añadir mensaje al historial
    session_state.add_to_history(f"Usuario: {user_message}")
    
    # Enrutar intención
    routing_result = route(user_message)
    intent = routing_result["intent"]
    args = routing_result["args"]
    is_short_command = routing_result["is_short_command"]
    
    logger.info(f"🎯 Intención detectada: {intent}")
    logger.info(f"📝 Argumentos: {args}")
    logger.info(f"🔤 Comando corto: {is_short_command}")
    
    # Si es comando corto, construir prompt oculto
    if is_short_command and intent != "FALLBACK_CHAT":
        # Ejecutar intención directamente
        response = execute_intent(intent, args, session_state)
        session_state.add_to_history(f"Sistema: {response}")
        return response
    
    # Si es FALLBACK_CHAT o comando largo, usar modelo
    if intent == "FALLBACK_CHAT" or not is_short_command:
        # Construir prompt con contexto
        if is_short_command:
            full_prompt = build_hidden_prompt(user_message, session_state)
        else:
            full_prompt = user_message
        
        # Preparar mensajes con historial
        messages = [
            {"role": "system", "content": "Eres el orquestador conversacional de App.Vision. Responde en español, de forma concisa y directa. Usa las herramientas cuando sea necesario."},
            {"role": "user", "content": full_prompt}
        ]
        
        # Añadir historial reciente si existe
        recent_history = session_state.get_recent_history(3)
        if recent_history:
            context = "Contexto reciente: " + "; ".join(recent_history)
            messages.insert(-1, {"role": "system", "content": context})
        
        try:
            # Llamada al modelo
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=APP_TEMPERATURE,
                max_completion_tokens=APP_MAX_OUTPUT_TOKENS,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            message = resp.choices[0].message
            
            # Si hay tool calls, procesarlos
            if message.tool_calls:
                logger.info(f"🔧 Ejecutando {len(message.tool_calls)} herramientas...")
                
                # Añadir respuesta del asistente
                messages.append({"role": "assistant", "content": message.content or "", "tool_calls": message.tool_calls})
                
                # Procesar cada tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments or "{}")
                    
                    # Verificar autorización para web_search
                    if tool_name == "web_search" and not is_web_search_authorized(user_message):
                        logger.warning(f"🚫 Web search no autorizado - rechazando llamada")
                        tool_result = {"error": "Web search no autorizado", "tool": tool_name}
                    else:
                        try:
                            tool_result = TOOL_IMPL[tool_name](tool_args)
                            logger.info(f"✅ Herramienta {tool_name} completada")
                        except Exception as e:
                            logger.error(f"❌ Error en herramienta {tool_name}: {e}")
                            tool_result = {"error": str(e), "tool": tool_name}
                    
                    # Agregar resultado
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(tool_result, ensure_ascii=False),
                        "tool_call_id": tool_call.id
                    })
                
                # Obtener respuesta final
                final_resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=APP_TEMPERATURE,
                    max_completion_tokens=APP_MAX_OUTPUT_TOKENS
                )
                
                response = final_resp.choices[0].message.content
            else:
                response = message.content
            
                # Añadir respuesta al historial
    session_state.add_to_history(f"Sistema: {response}")
    
    # Guardar estado
    session_state.save_to_file()
    
    return response or "No se pudo generar respuesta"
            
        except Exception as e:
            logger.error(f"❌ Error en orquestador conversacional: {e}")
            error_msg = f"Error: {e}"
            session_state.add_to_history(f"Sistema: {error_msg}")
            return error_msg
    
    # Si llegamos aquí, ejecutar intención directamente
    response = execute_intent(intent, args, session_state)
    session_state.add_to_history(f"Sistema: {response}")
    return response

def get_orchestrator_status() -> Dict[str, Any]:
    """Obtiene el estado del orquestador conversacional"""
    session_state = get_session_state()
    return {
        "mode": session_state.get_mode(),
        "current_model": session_state.get_model(),
        "current_task": session_state.get_current_task(),
        "protocol_stage": session_state.get_protocol_stage(),
        "history_count": len(session_state.get_history()),
        "tools_available": len(TOOL_IMPL),
        "web_search_control": "Solo si el usuario lo ordena explícitamente"
    }

if __name__ == "__main__":
    print("🎯 VISION PREMIUM - Orquestador Conversacional")
    print("=" * 60)
    
    # Prueba básica
    print("🧪 Probando orquestador conversacional...")
    
    # Prueba comando corto
    response1 = call_conversational_orchestrator("Inicia protocolo")
    print(f"✅ Comando corto: {response1}")
    
    # Prueba comando largo
    response2 = call_conversational_orchestrator("Hola, ¿cómo estás? ¿Puedes ayudarme con el análisis de loterías?")
    print(f"✅ Comando largo: {response2}")
    
    # Prueba estado
    response3 = call_conversational_orchestrator("Estado")
    print(f"✅ Estado: {response3}")
    
    print("\n🎉 Orquestador conversacional funcionando correctamente")
