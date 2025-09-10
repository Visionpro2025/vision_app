#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SESSION STATE - Gestión de estado de sesión para App.Vision
Mantiene el estado mínimo del orquestador conversacional
"""

from typing import Optional, List, Dict, Any
import json
import os
from datetime import datetime

class SessionState:
    """Estado de sesión del orquestador conversacional"""
    
    def __init__(self):
        self.current_task: Optional[str] = None
        self.protocol_stage: Optional[str] = None
        self.history: List[str] = []
        self.mode: str = "chat"  # "chat" | "cmd"
        self.current_model: str = "gpt-4o-mini"
        self.protocol_data: Dict[str, Any] = {}
        self.last_series: Optional[List[int]] = None
        self.created_at: str = datetime.now().isoformat()
        self.updated_at: str = datetime.now().isoformat()
    
    def set_current_task(self, task: str) -> None:
        """Establece la tarea actual"""
        self.current_task = task
        self.updated_at = datetime.now().isoformat()
    
    def get_current_task(self) -> Optional[str]:
        """Obtiene la tarea actual"""
        return self.current_task
    
    def set_protocol_stage(self, stage: str) -> None:
        """Establece la etapa del protocolo"""
        self.protocol_stage = stage
        self.updated_at = datetime.now().isoformat()
    
    def get_protocol_stage(self) -> Optional[str]:
        """Obtiene la etapa del protocolo"""
        return self.protocol_stage
    
    def add_to_history(self, message: str) -> None:
        """Añade mensaje al historial"""
        self.history.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        # Mantener solo los últimos 50 mensajes
        if len(self.history) > 50:
            self.history = self.history[-50:]
        self.updated_at = datetime.now().isoformat()
    
    def get_history(self) -> List[str]:
        """Obtiene el historial completo"""
        return self.history.copy()
    
    def get_recent_history(self, count: int = 10) -> List[str]:
        """Obtiene los últimos N mensajes del historial"""
        return self.history[-count:] if self.history else []
    
    def set_mode(self, mode: str) -> None:
        """Establece el modo (chat | cmd)"""
        if mode in ["chat", "cmd"]:
            self.mode = mode
            self.updated_at = datetime.now().isoformat()
    
    def get_mode(self) -> str:
        """Obtiene el modo actual"""
        return self.mode
    
    def set_model(self, model: str) -> None:
        """Establece el modelo actual"""
        self.current_model = model
        self.updated_at = datetime.now().isoformat()
    
    def get_model(self) -> str:
        """Obtiene el modelo actual"""
        return self.current_model
    
    def set_protocol_data(self, data: Dict[str, Any]) -> None:
        """Establece datos del protocolo"""
        self.protocol_data = data
        self.updated_at = datetime.now().isoformat()
    
    def get_protocol_data(self) -> Dict[str, Any]:
        """Obtiene datos del protocolo"""
        return self.protocol_data.copy()
    
    def set_last_series(self, series: List[int]) -> None:
        """Establece la última serie analizada"""
        self.last_series = series
        self.updated_at = datetime.now().isoformat()
    
    def get_last_series(self) -> Optional[List[int]]:
        """Obtiene la última serie analizada"""
        return self.last_series
    
    def reset(self) -> None:
        """Reinicia el estado de sesión"""
        self.current_task = None
        self.protocol_stage = None
        self.history = []
        self.mode = "chat"
        self.current_model = "gpt-4o-mini"
        self.protocol_data = {}
        self.last_series = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el estado a diccionario"""
        return {
            "current_task": self.current_task,
            "protocol_stage": self.protocol_stage,
            "history": self.history,
            "mode": self.mode,
            "current_model": self.current_model,
            "protocol_data": self.protocol_data,
            "last_series": self.last_series,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Carga el estado desde diccionario"""
        self.current_task = data.get("current_task")
        self.protocol_stage = data.get("protocol_stage")
        self.history = data.get("history", [])
        self.mode = data.get("mode", "chat")
        self.current_model = data.get("current_model", "gpt-4o-mini")
        self.protocol_data = data.get("protocol_data", {})
        self.last_series = data.get("last_series")
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.updated_at = data.get("updated_at", datetime.now().isoformat())
    
    def save_to_file(self, filename: str = "session_state.json") -> None:
        """Guarda el estado en archivo"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando estado: {e}")
    
    def load_from_file(self, filename: str = "session_state.json") -> bool:
        """Carga el estado desde archivo"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.from_dict(data)
                    return True
        except Exception as e:
            print(f"Error cargando estado: {e}")
        return False
    
    def get_status_summary(self) -> str:
        """Obtiene un resumen del estado actual"""
        status_parts = []
        
        if self.current_task:
            status_parts.append(f"Tarea: {self.current_task}")
        
        if self.protocol_stage:
            status_parts.append(f"Etapa: {self.protocol_stage}")
        
        status_parts.append(f"Modo: {self.mode}")
        status_parts.append(f"Modelo: {self.current_model}")
        status_parts.append(f"Mensajes: {len(self.history)}")
        
        if self.last_series:
            status_parts.append(f"Última serie: {self.last_series}")
        
        return " | ".join(status_parts)

# Instancia global del estado de sesión
session_state = SessionState()

def get_session_state() -> SessionState:
    """Obtiene la instancia global del estado de sesión"""
    return session_state

def reset_session() -> None:
    """Reinicia la sesión global"""
    session_state.reset()

def save_session() -> None:
    """Guarda la sesión global"""
    session_state.save_to_file()

def load_session() -> bool:
    """Carga la sesión global"""
    return session_state.load_from_file()

if __name__ == "__main__":
    print("🔧 VISION PREMIUM - Gestión de Estado de Sesión")
    print("=" * 50)
    
    # Prueba básica
    state = get_session_state()
    print(f"Estado inicial: {state.get_status_summary()}")
    
    # Simular uso
    state.set_current_task("Análisis de MegaMillions")
    state.set_protocol_stage("Gematría")
    state.add_to_history("Usuario: Inicia protocolo")
    state.add_to_history("Sistema: Protocolo iniciado")
    state.set_mode("cmd")
    state.set_model("gpt-4o-mini")
    
    print(f"Estado después de cambios: {state.get_status_summary()}")
    
    # Guardar y cargar
    state.save_to_file("test_session.json")
    print("✅ Estado guardado en test_session.json")
    
    # Crear nueva instancia y cargar
    new_state = SessionState()
    if new_state.load_from_file("test_session.json"):
        print(f"✅ Estado cargado: {new_state.get_status_summary()}")
    
    # Limpiar archivo de prueba
    try:
        os.remove("test_session.json")
        print("✅ Archivo de prueba eliminado")
    except:
        pass








