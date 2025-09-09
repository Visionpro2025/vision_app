#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step1Initialization - Paso de inicialización del sistema
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app_vision.engine.contracts import Step, StepContext, StepError, StepResult
from app_vision.engine.fsm import register_step
import gc
import psutil

@register_step("step1_initialization")
class Step1Initialization(Step):
    name = "step1_initialization"
    description = "Inicialización y limpieza del sistema"
    version = "1.0"
    
    def validate_inputs(self, data):
        """Valida los datos de entrada (opcional para este paso)."""
        return True
    
    def run(self, ctx: StepContext, data) -> StepResult:
        """Ejecuta la inicialización del sistema."""
        
        try:
            # Limpieza de memoria
            gc.collect()
            
            # Verificar salud del sistema
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Crear directorio de estado si no existe
            os.makedirs(ctx.state_dir, exist_ok=True)
            
            # Inicializar archivo de estado
            state_file = os.path.join(ctx.state_dir, f"state_{ctx.run_id}.json")
            
            initialization_data = {
                "memory_cleanup": "completed",
                "memory_usage": memory_info.percent,
                "cpu_usage": cpu_percent,
                "state_dir": ctx.state_dir,
                "run_id": ctx.run_id,
                "timestamp": ctx.timestamp.isoformat()
            }
            
            return StepResult(
                success=True,
                data=initialization_data,
                metadata={
                    "step_name": self.name,
                    "version": self.version,
                    "memory_available": memory_info.available,
                    "cpu_cores": psutil.cpu_count()
                }
            )
            
        except Exception as e:
            raise StepError("InitializationError", f"Error en inicialización: {str(e)}")
    
    def cleanup(self, ctx: StepContext):
        """Limpieza de recursos."""
        gc.collect()
