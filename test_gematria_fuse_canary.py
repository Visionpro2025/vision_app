#!/usr/bin/env python3
"""
Test Canario para GematriaPerCandadoStep y GuideMessageFuseStep
Verifica:
1) Al menos 3 candados entran al paso de gematría
2) La fusión devuelve topics y message no vacíos
3) El sistema rechaza dominios fuera de allowlist
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Añadir el directorio raíz del proyecto al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app_vision.engine.fsm import pipeline_executor, register_step
from app_vision.engine.contracts import StepContext, StepError
from app_vision.steps.step_gematria_per_candado import GematriaPerCandadoStep
from app_vision.steps.step_guide_message_fuse import GuideMessageFuseStep
from app_vision.modules.guardrails import apply_basic_guardrails

def create_test_candados():
    """Crea candados de prueba para el test"""
    base_date = datetime.now() - timedelta(days=1)
    
    return [
        {
            "slot": "AM",
            "date": base_date.strftime("%Y-%m-%d"),
            "block": "AM",
            "candado": ["81", "49", "21"],
            "fijo2d": "81",
            "pick3": [8, 8, 1],
            "source": "florida_lottery_api"
        },
        {
            "slot": "MID", 
            "date": base_date.strftime("%Y-%m-%d"),
            "block": "MID",
            "candado": ["98", "02"],
            "fijo2d": "98",
            "pick3": [9, 8, 7],
            "source": "florida_lottery_api"
        },
        {
            "slot": "EVE",
            "date": base_date.strftime("%Y-%m-%d"), 
            "block": "EVE",
            "candado": ["07", "39", "02"],
            "fijo2d": "07",
            "pick3": [0, 7, 4],
            "source": "florida_lottery_api"
        }
    ]

def test_gematria_per_candado():
    """Test 1: Verificar que GematriaPerCandadoStep procesa al menos 3 candados"""
    print("🔍 Test 1: GematriaPerCandadoStep con 3 candados...")
    
    step = GematriaPerCandadoStep()
    candados = create_test_candados()
    
    try:
        result = step.run(
            StepContext("test", "test", "test", "test"),
            {"candados": candados}
        )
        
        per_candado = result.get("per_candado", [])
        if len(per_candado) < 3:
            raise AssertionError(f"Esperaba al menos 3 candados procesados, obtuve {len(per_candado)}")
        
        # Verificar que cada candado tiene los campos requeridos
        for item in per_candado:
            required_fields = ["topics", "keywords", "poem", "families", "seed_trace"]
            for field in required_fields:
                if field not in item:
                    raise AssertionError(f"Campo requerido '{field}' faltante en {item}")
                if not item[field]:
                    raise AssertionError(f"Campo '{field}' está vacío en {item}")
        
        print(f"✅ Test 1 PASÓ: {len(per_candado)} candados procesados correctamente")
        return per_candado
        
    except Exception as e:
        print(f"❌ Test 1 FALLÓ: {e}")
        raise

def test_guide_message_fuse(per_candado):
    """Test 2: Verificar que GuideMessageFuseStep devuelve topics y message no vacíos"""
    print("🔍 Test 2: GuideMessageFuseStep con fusión de mensajes...")
    
    step = GuideMessageFuseStep()
    
    try:
        result = step.run(
            StepContext("test", "test", "test", "test"),
            {
                "per_candado": per_candado,
                "for_block": "MID",
                "top_topics": 6,
                "top_keywords": 10
            }
        )
        
        guide = result.get("guide", {})
        
        # Verificar campos requeridos
        required_fields = ["topics", "keywords", "message", "trace"]
        for field in required_fields:
            if field not in guide:
                raise AssertionError(f"Campo requerido '{field}' faltante en guide")
            if not guide[field]:
                raise AssertionError(f"Campo '{field}' está vacío en guide")
        
        # Verificar que topics y message no están vacíos
        if not guide["topics"]:
            raise AssertionError("Topics está vacío")
        if not guide["keywords"]:
            raise AssertionError("Keywords está vacío")
        if not guide["message"] or guide["message"].strip() == "":
            raise AssertionError("Message está vacío")
        
        print(f"✅ Test 2 PASÓ: Guide generado con {len(guide['topics'])} topics y {len(guide['keywords'])} keywords")
        print(f"   Message: {guide['message']}")
        return guide
        
    except Exception as e:
        print(f"❌ Test 2 FALLÓ: {e}")
        raise

def test_guardrails_allowlist():
    """Test 3: Verificar que el sistema rechaza dominios fuera de allowlist"""
    print("🔍 Test 3: Guardrails con allowlist de dominios...")
    
    try:
        # Test con dominio permitido
        apply_basic_guardrails(
            step_name="TestStep",
            input_data={"source": "https://flalottery.com/data"},
            output_data={"data": "test"},
            sources_allowlist=["flalottery.com", "floridalottery.com"]
        )
        print("✅ Dominio permitido (flalottery.com) aceptado correctamente")
        
        # Test con dominio no permitido (debería fallar)
        try:
            apply_basic_guardrails(
                step_name="TestStep",
                input_data={"source": "https://fake-lottery.com/data"},
                output_data={"data": "test"},
                sources_allowlist=["flalottery.com", "floridalottery.com"]
            )
            raise AssertionError("Debería haber fallado con dominio no permitido")
        except StepError as e:
            if "fuera de allowlist" in str(e):
                print("✅ Dominio no permitido (fake-lottery.com) rechazado correctamente")
            else:
                raise AssertionError(f"Error inesperado: {e}")
        
        print("✅ Test 3 PASÓ: Guardrails de allowlist funcionando correctamente")
        
    except Exception as e:
        print(f"❌ Test 3 FALLÓ: {e}")
        raise

def test_pipeline_integration():
    """Test 4: Verificar integración completa en pipeline"""
    print("🔍 Test 4: Integración completa en pipeline...")
    
    # Registrar steps
    register_step("GematriaPerCandadoStep")(GematriaPerCandadoStep)
    register_step("GuideMessageFuseStep")(GuideMessageFuseStep)
    
    # Pipeline de prueba
    pipeline_config = {
        "steps": [
            {
                "name": "step_gematria",
                "class": "GematriaPerCandadoStep",
                "inputs": {
                    "candados": create_test_candados()
                }
            },
            {
                "name": "step_fuse",
                "class": "GuideMessageFuseStep", 
                "inputs": {
                    "per_candado": "${step.step_gematria.per_candado}",
                    "for_block": "MID",
                    "top_topics": 6,
                    "top_keywords": 10
                }
            }
        ]
    }
    
    try:
        result = pipeline_executor.execute_pipeline(pipeline_config)
        
        if result["status"] != "completed":
            raise AssertionError(f"Pipeline falló con status: {result['status']}")
        
        # Verificar que ambos steps se ejecutaron
        if "step_gematria" not in result["step_results"]:
            raise AssertionError("step_gematria no se ejecutó")
        if "step_fuse" not in result["step_results"]:
            raise AssertionError("step_fuse no se ejecutó")
        
        # Verificar outputs
        gematria_output = result["step_results"]["step_gematria"]
        fuse_output = result["step_results"]["step_fuse"]
        
        if "per_candado" not in gematria_output:
            raise AssertionError("step_gematria no devolvió per_candado")
        if "guide" not in fuse_output:
            raise AssertionError("step_fuse no devolvió guide")
        
        print("✅ Test 4 PASÓ: Pipeline completo ejecutado correctamente")
        print(f"   Candados procesados: {len(gematria_output['per_candado'])}")
        print(f"   Topics en guide: {len(fuse_output['guide']['topics'])}")
        
    except Exception as e:
        print(f"❌ Test 4 FALLÓ: {e}")
        raise

def main():
    """Ejecutar todos los tests canarios"""
    print("🐤 CANARIO GEMATRIA + FUSE - VISION PREMIUM")
    print("=" * 50)
    
    try:
        # Test 1: GematriaPerCandadoStep
        per_candado = test_gematria_per_candado()
        
        # Test 2: GuideMessageFuseStep
        guide = test_guide_message_fuse(per_candado)
        
        # Test 3: Guardrails allowlist
        test_guardrails_allowlist()
        
        # Test 4: Integración pipeline
        test_pipeline_integration()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS LOS TESTS CANARIOS SUPERADOS")
        print("✅ GematriaPerCandadoStep: Funcionando")
        print("✅ GuideMessageFuseStep: Funcionando") 
        print("✅ Guardrails allowlist: Funcionando")
        print("✅ Integración pipeline: Funcionando")
        print("\n🚀 Sistema listo para producción")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ CANARIO FALLÓ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()




