#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTENT ROUTER - Enrutador de intenciones para App.Vision
Mapea comandos cortos a intenciones específicas usando regex
"""

import re
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

class IntentRouter:
    """Enrutador de intenciones para comandos cortos"""
    
    def __init__(self):
        # Patrones regex para detectar intenciones
        self.patterns = {
            # Comandos de protocolo
            "START_PROTOCOL": [
                r"inicia\s+protocolo",
                r"comenzar\s+protocolo",
                r"arrancar\s+protocolo",
                r"empezar\s+protocolo",
                r"protocolo\s+mega",
                r"mega\s+millions"
            ],
            
            "NEXT_STEP": [
                r"continuar",
                r"siguiente",
                r"next",
                r"avanzar",
                r"proceder"
            ],
            
            "STATUS": [
                r"estado",
                r"status",
                r"qué\s+haces",
                r"dónde\s+estamos",
                r"progreso"
            ],
            
            "STOP": [
                r"detener",
                r"stop",
                r"parar",
                r"terminar",
                r"cerrar"
            ],
            
            # Comandos de herramientas
            "GEMATRIA_PASS": [
                r"gematria",
                r"gematría",
                r"números\s+esotéricos"
            ],
            
            "SUBLIMINAL_PASS": [
                r"subliminal",
                r"pistas\s+ocultas",
                r"mensaje\s+secreto"
            ],
            
            # Búsqueda de sorteos con rango de fechas
            "SEARCH_DRAWS": [
                r"buscar\s+sorteos\s+(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})",
                r"sorteos\s+(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})",
                r"resultados\s+(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})"
            ],
            
            # Búsqueda de sorteos por fecha simple
            "SEARCH_DRAWS_SIMPLE": [
                r"buscar\s+sorteos\s+(\d{4}-\d{2}-\d{2})",
                r"sorteos\s+(\d{4}-\d{2}-\d{2})",
                r"resultados\s+(\d{4}-\d{2}-\d{2})"
            ],
            
            # Cambio de modelo
            "SET_MODEL_MINI": [
                r"cambia\s+a\s+mini",
                r"modelo\s+mini",
                r"usar\s+mini",
                r"gpt-4o-mini"
            ],
            
            "SET_MODEL_NANO": [
                r"cambia\s+a\s+nano",
                r"modelo\s+nano",
                r"usar\s+nano",
                r"gpt-5-nano"
            ],
            
            # Comandos de gestión
            "SAVE_SERIES": [
                r"guardar\s+serie",
                r"guardar\s+guía",
                r"persistir\s+serie",
                r"salvar\s+resultado"
            ],
            
            "RESTART": [
                r"reinicia",
                r"restart",
                r"reset",
                r"empezar\s+de\s+nuevo",
                r"borrar\s+estado"
            ],
            
            # Comandos de ayuda
            "HELP": [
                r"ayuda",
                r"help",
                r"comandos",
                r"qué\s+puedo\s+hacer"
            ]
        }
        
        # Compilar patrones regex
        self.compiled_patterns = {}
        for intent, patterns in self.patterns.items():
            self.compiled_patterns[intent] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def route(self, text: str) -> Dict[str, Any]:
        """
        Enruta el texto a una intención específica
        
        Args:
            text: Texto del usuario
            
        Returns:
            Dict con intent, args y metadata
        """
        text = text.strip()
        
        # Si el texto está vacío, es fallback
        if not text:
            return {
                "intent": "FALLBACK_CHAT",
                "args": {},
                "original_text": text,
                "confidence": 0.0,
                "is_short_command": False
            }
        
        # Determinar si es comando corto (< 50 chars)
        is_short_command = len(text) < 50
        
        # Buscar coincidencias en orden de prioridad
        for intent, compiled_patterns in self.compiled_patterns.items():
            for pattern in compiled_patterns:
                match = pattern.search(text)
                if match:
                    args = {}
                    
                    # Extraer argumentos específicos según la intención
                    if intent == "SEARCH_DRAWS" and len(match.groups()) >= 2:
                        args = {
                            "fecha_inicio": match.group(1),
                            "fecha_fin": match.group(2)
                        }
                    elif intent == "SEARCH_DRAWS_SIMPLE" and len(match.groups()) >= 1:
                        args = {
                            "fecha": match.group(1)
                        }
                    elif intent in ["SET_MODEL_MINI", "SET_MODEL_NANO"]:
                        args = {
                            "model": "gpt-4o-mini" if intent == "SET_MODEL_MINI" else "gpt-5-nano"
                        }
                    
                    return {
                        "intent": intent,
                        "args": args,
                        "original_text": text,
                        "confidence": 1.0,
                        "is_short_command": is_short_command,
                        "matched_pattern": pattern.pattern
                    }
        
        # Si no se encontró coincidencia, es fallback
        return {
            "intent": "FALLBACK_CHAT",
            "args": {},
            "original_text": text,
            "confidence": 0.0,
            "is_short_command": is_short_command
        }
    
    def get_supported_commands(self) -> Dict[str, List[str]]:
        """Obtiene la lista de comandos soportados"""
        commands = {}
        for intent, patterns in self.patterns.items():
            commands[intent] = [pattern.replace(r"\s+", " ") for pattern in patterns]
        return commands
    
    def get_command_examples(self) -> List[str]:
        """Obtiene ejemplos de comandos"""
        examples = [
            "Inicia protocolo",
            "Continuar",
            "Estado",
            "Detener",
            "Gematria",
            "Subliminal",
            "Buscar sorteos 2025-08-20..2025-09-05",
            "Buscar sorteos 2025-09-01",
            "Cambia a mini",
            "Cambia a nano",
            "Guardar serie guía",
            "Reinicia",
            "Ayuda"
        ]
        return examples

def route(text: str) -> Dict[str, Any]:
    """
    Función de conveniencia para enrutar texto
    
    Args:
        text: Texto del usuario
        
    Returns:
        Dict con intent, args y metadata
    """
    router = IntentRouter()
    return router.route(text)

if __name__ == "__main__":
    print("🔧 VISION PREMIUM - Enrutador de Intenciones")
    print("=" * 50)
    
    router = IntentRouter()
    
    # Pruebas de comandos
    test_commands = [
        "Inicia protocolo",
        "Continuar",
        "Estado",
        "Detener",
        "Gematria",
        "Subliminal",
        "Buscar sorteos 2025-08-20..2025-09-05",
        "Buscar sorteos 2025-09-01",
        "Cambia a mini",
        "Cambia a nano",
        "Guardar serie guía",
        "Reinicia",
        "Ayuda",
        "Hola, ¿cómo estás?",  # Fallback
        ""  # Vacío
    ]
    
    print("🧪 Probando comandos:")
    print("-" * 30)
    
    for cmd in test_commands:
        result = router.route(cmd)
        print(f"'{cmd}' -> {result['intent']} {result['args']}")
    
    print("\n📋 Comandos soportados:")
    print("-" * 30)
    commands = router.get_supported_commands()
    for intent, patterns in commands.items():
        print(f"{intent}: {patterns[0] if patterns else 'N/A'}")
    
    print("\n💡 Ejemplos de uso:")
    print("-" * 30)
    examples = router.get_command_examples()
    for example in examples:
        print(f"  - {example}")
