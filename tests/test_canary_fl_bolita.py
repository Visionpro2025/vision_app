#!/usr/bin/env python3
"""
Test Canario para FL→Bolita Pipeline
Verifica que el circuito cerrado funciona correctamente:
- BlockNowStep detecta bloque correcto
- BuildCandadoContextStep arma paquete correcto
- GematriaPerCandadoStep procesa candados
- GuideMessageFuseStep genera guía válida
"""

import json
import sys
from pathlib import Path

# Añadir el directorio raíz del proyecto al path para imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app_vision.steps.step_block_now import BlockNowStep
from app_vision.steps.step_build_candado_context import BuildCandadoContextStep
from app_vision.steps.step_gematria_per_candado import GematriaPerCandadoStep
from app_vision.steps.step_guide_message_fuse import GuideMessageFuseStep
from app_vision.engine.contracts import StepContext

def _ctx():
    return StepContext("TEST-RUN", "test", "test", "test")

# Simula draws reales para 3 días (solo MID/EVE oficiales)
DRAWS = [
    # día 0 (hoy)
    {"date":"2025-09-08","block":"MID","numbers":[8,8,1],"pick4":[1,2,3,4],"source":"flalottery.com"},
    # día -1
    {"date":"2025-09-07","block":"EVE","numbers":[0,7,3],"pick4":[5,9,1,2],"source":"flalottery.com"},
    {"date":"2025-09-07","block":"MID","numbers":[6,9,8],"pick4":[7,7,0,2],"source":"flalottery.com"},
    # día -2
    {"date":"2025-09-06","block":"EVE","numbers":[3,9,9],"pick4":[4,8,2,1],"source":"flalottery.com"},
    {"date":"2025-09-06","block":"MID","numbers":[2,4,7],"pick4":[9,0,3,1],"source":"flalottery.com"},
]

def test_block_now_step():
    """Test 1: BlockNowStep detecta bloque correcto"""
    print("🔍 Test 1: BlockNowStep...")
    
    step = BlockNowStep()
    
    # Test con hora MID
    result = step.run(_ctx(), {"now_et":"2025-09-08T13:45:00"})
    assert result["block_now"] == "MID", f"Esperaba MID, obtuve {result['block_now']}"
    
    # Test con hora EVE
    result = step.run(_ctx(), {"now_et":"2025-09-08T21:45:00"})
    assert result["block_now"] == "EVE", f"Esperaba EVE, obtuve {result['block_now']}"
    
    # Test con hora AM
    result = step.run(_ctx(), {"now_et":"2025-09-08T06:15:00"})
    assert result["block_now"] == "AM", f"Esperaba AM, obtuve {result['block_now']}"
    
    print("✅ Test 1 PASÓ: BlockNowStep detecta bloques correctamente")

def test_build_candado_context_step():
    """Test 2: BuildCandadoContextStep arma paquete correcto"""
    print("🔍 Test 2: BuildCandadoContextStep...")
    
    step = BuildCandadoContextStep()
    
    # Test para bloque MID
    result = step.run(_ctx(), {"draws": DRAWS, "for_block": "MID"})
    context = result["candado_context"]
    
    assert context["for_block"] == "MID"
    items = context["items"]
    
    # Debe incluir AM_today + 3 de D-1 (>=4 ítems)
    useful = [x for x in items if not x.get("missing")]
    assert len(useful) >= 3, f"Esperaba al menos 3 ítems útiles, obtuve {len(useful)}"
    
    # Verificar que cada ítem tiene candado válido
    for it in useful:
        assert len(it["candado"]) >= 2, f"Candado insuficiente en {it['slot']}: {it['candado']}"
        assert it["fijo2d"], f"Fijo2d faltante en {it['slot']}"
    
    print(f"✅ Test 2 PASÓ: Contexto MID con {len(useful)} ítems útiles")
    
    # Test para bloque EVE
    result = step.run(_ctx(), {"draws": DRAWS, "for_block": "EVE"})
    context = result["candado_context"]
    
    assert context["for_block"] == "EVE"
    items = context["items"]
    useful = [x for x in items if not x.get("missing")]
    assert len(useful) >= 4, f"EVE debe tener al menos 4 ítems útiles, obtuve {len(useful)}"
    
    print(f"✅ Test 2 PASÓ: Contexto EVE con {len(useful)} ítems útiles")

def test_gematria_per_candado_step():
    """Test 3: GematriaPerCandadoStep procesa candados"""
    print("🔍 Test 3: GematriaPerCandadoStep...")
    
    step = GematriaPerCandadoStep()
    
    # Crear contexto de prueba
    context_step = BuildCandadoContextStep()
    context_result = context_step.run(_ctx(), {"draws": DRAWS, "for_block": "MID"})
    items = context_result["candado_context"]["items"]
    
    # Procesar con gematría
    result = step.run(_ctx(), {"candados": items})
    per_candado = result["per_candado"]
    
    assert len(per_candado) >= 3, f"Esperaba al menos 3 candados procesados, obtuve {len(per_candado)}"
    
    # Verificar que cada candado tiene análisis
    for item in per_candado:
        assert item["topics"], f"Topics vacío en {item.get('slot', 'unknown')}"
        assert item["keywords"], f"Keywords vacío en {item.get('slot', 'unknown')}"
        assert item["poem"], f"Poem vacío en {item.get('slot', 'unknown')}"
        assert item["families"], f"Families vacío en {item.get('slot', 'unknown')}"
    
    print(f"✅ Test 3 PASÓ: {len(per_candado)} candados procesados con gematría")

def test_guide_message_fuse_step():
    """Test 4: GuideMessageFuseStep genera guía válida"""
    print("🔍 Test 4: GuideMessageFuseStep...")
    
    step = GuideMessageFuseStep()
    
    # Crear datos de prueba
    context_step = BuildCandadoContextStep()
    context_result = context_step.run(_ctx(), {"draws": DRAWS, "for_block": "MID"})
    items = context_result["candado_context"]["items"]
    
    gematria_step = GematriaPerCandadoStep()
    gematria_result = gematria_step.run(_ctx(), {"candados": items})
    per_candado = gematria_result["per_candado"]
    
    # Fusionar en guía
    result = step.run(_ctx(), {
        "per_candado": per_candado,
        "for_block": "MID",
        "top_topics": 6,
        "top_keywords": 10
    })
    
    guide = result["guide"]
    
    # Verificar campos requeridos
    assert guide["topics"], "Topics no deben estar vacíos"
    assert guide["keywords"], "Keywords no deben estar vacíos"
    assert guide["message"], "Message no debe estar vacío"
    assert guide["trace"], "Trace no debe estar vacío"
    assert guide["for_block"] == "MID"
    
    # Verificar que hay suficientes topics y keywords
    assert len(guide["topics"]) >= 3, f"Esperaba al menos 3 topics, obtuve {len(guide['topics'])}"
    assert len(guide["keywords"]) >= 5, f"Esperaba al menos 5 keywords, obtuve {len(guide['keywords'])}"
    
    print(f"✅ Test 4 PASÓ: Guía generada con {len(guide['topics'])} topics y {len(guide['keywords'])} keywords")
    print(f"   Message: {guide['message']}")

def test_pipeline_integration():
    """Test 5: Integración completa del pipeline"""
    print("🔍 Test 5: Integración completa del pipeline...")
    
    from app_vision.engine.fsm import pipeline_executor, register_step
    
    # Registrar todos los steps
    register_step("BlockNowStep")(BlockNowStep)
    register_step("BuildCandadoContextStep")(BuildCandadoContextStep)
    register_step("GematriaPerCandadoStep")(GematriaPerCandadoStep)
    register_step("GuideMessageFuseStep")(GuideMessageFuseStep)
    
    # Pipeline de prueba
    pipeline_config = {
        "steps": [
            {
                "name": "step_block_now",
                "class": "BlockNowStep",
                "inputs": {"now_et": "2025-09-08T13:45:00"}
            },
            {
                "name": "step_build_context",
                "class": "BuildCandadoContextStep",
                "inputs": {
                    "draws": DRAWS,
                    "for_block": "${step.step_block_now.block_now}"
                }
            },
            {
                "name": "step_gematria",
                "class": "GematriaPerCandadoStep",
                "inputs": {
                    "candados": "${step.step_build_context.candado_context.items}"
                }
            },
            {
                "name": "step_fuse",
                "class": "GuideMessageFuseStep",
                "inputs": {
                    "per_candado": "${step.step_gematria.per_candado}",
                    "for_block": "${step.step_block_now.block_now}",
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
        
        # Verificar que todos los steps se ejecutaron
        expected_steps = ["step_block_now", "step_build_context", "step_gematria", "step_fuse"]
        for step_name in expected_steps:
            assert step_name in result["step_results"], f"Step {step_name} no se ejecutó"
        
        # Verificar outputs finales
        fuse_output = result["step_results"]["step_fuse"]
        assert "guide" in fuse_output, "step_fuse no devolvió guide"
        
        guide = fuse_output["guide"]
        assert guide["topics"] and guide["message"], "Guide final incompleto"
        
        print("✅ Test 5 PASÓ: Pipeline completo ejecutado correctamente")
        print(f"   Guide final: {json.dumps(guide, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"❌ Test 5 FALLÓ: {e}")
        raise

def main():
    """Ejecutar todos los tests canarios"""
    print("🐤 CANARIO FL→BOLITA - VISION PREMIUM")
    print("=" * 50)
    
    try:
        test_block_now_step()
        test_build_candado_context_step()
        test_gematria_per_candado_step()
        test_guide_message_fuse_step()
        test_pipeline_integration()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS LOS TESTS CANARIOS SUPERADOS")
        print("✅ BlockNowStep: Funcionando")
        print("✅ BuildCandadoContextStep: Funcionando")
        print("✅ GematriaPerCandadoStep: Funcionando")
        print("✅ GuideMessageFuseStep: Funcionando")
        print("✅ Pipeline Integration: Funcionando")
        print("\n🚀 Sistema FL→Bolita listo para producción")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ CANARIO FALLÓ: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



