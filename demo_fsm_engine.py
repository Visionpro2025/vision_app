#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo del motor FSM con pasos del protocolo universal
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Importar pasos para registrarlos
import steps.step1_initialization
import steps.step2_lottery_config
import steps.step6_artifacts

from app_vision.engine.contracts import StepRegistry, FSMEngine
from app_vision.engine.fsm import create_engine

def demo_fsm_engine():
    """Demostración del motor FSM."""
    
    print("🎯 DEMO DEL MOTOR FSM - PROTOCOLO UNIVERSAL")
    print("="*60)
    
    # Crear motor FSM
    engine = create_engine(".state")
    
    # Iniciar ejecución
    run_id = engine.start_run()
    print(f"🆔 Run ID: {run_id}")
    
    # Mostrar pasos registrados
    print(f"\n📋 Pasos registrados: {len(StepRegistry.list_steps())}")
    for name, step_class in StepRegistry.list_steps().items():
        print(f"   • {name}: {step_class.description}")
    
    # Definir secuencia de pasos
    sequence = [
        {
            "name": "step1_initialization",
            "data": {}
        },
        {
            "name": "step2_lottery_config", 
            "data": {
                "lottery_type": "Florida Pick 3",
                "number_range": "00-99",
                "frequency": "twice_daily"
            }
        },
        {
            "name": "step6_artifacts",
            "data": {
                "poem": "En la danza cuántica de los números,\nLos sefirot revelan su verdad,\nTres, siete, nueve en armonía,\nManifiestan la realidad.",
                "topics": {
                    "sefirot": ["Binah", "Netzach", "Yesod"],
                    "numeros": [3, 7, 9],
                    "energia": 0.8,
                    "categoria": "espiritual"
                }
            }
        }
    ]
    
    print(f"\n🔄 Ejecutando secuencia de {len(sequence)} pasos...")
    
    # Ejecutar secuencia
    results = engine.execute_sequence(sequence)
    
    print(f"\n📊 RESULTADOS DE LA EJECUCIÓN:")
    print("="*60)
    
    for step_name, result in results.items():
        if result.success:
            print(f"✅ {step_name}: EXITOSO")
            if result.data:
                print(f"   📊 Datos: {list(result.data.keys())}")
        else:
            print(f"❌ {step_name}: ERROR - {result.error}")
    
    print(f"\n💾 Estado guardado en: .state/")
    print(f"🆔 Run ID: {run_id}")
    
    return results

if __name__ == "__main__":
    demo_fsm_engine()




