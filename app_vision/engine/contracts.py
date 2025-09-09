from __future__ import annotations
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime

@dataclass
class StepContext:
    """Contexto de ejecución para un paso"""
    step_name: str
    step_id: str
    pipeline_id: str
    execution_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed

@dataclass
class StepResult:
    """Resultado de ejecución de un paso"""
    status: str  # success, failure
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_type: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class StepError(Exception):
    """Error específico de un paso"""
    def __init__(self, error_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        super().__init__(f"[{error_type}] {message}")

class Step(ABC):
    """Clase base para todos los pasos del pipeline"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta el paso con el contexto y datos dados"""
        pass
    
    def validate_inputs(self, data: Dict[str, Any]) -> bool:
        """Valida los inputs del paso (opcional)"""
        return True
    
    def get_required_inputs(self) -> list[str]:
        """Retorna los inputs requeridos para este paso"""
        return []