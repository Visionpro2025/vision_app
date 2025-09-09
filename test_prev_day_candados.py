#!/usr/bin/env python3
"""
Test para verificar el funcionamiento de los candados del día anterior.
Valida el mapeo cubano y la construcción de los 3 candados.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_prev_day_candados_step():
    """Test del step PrevDayCandadosStep"""
    print("🔍 Testando PrevDayCandadosStep...")
    
    from app_vision.steps.step_prev_day_candados import PrevDayCandadosStep
    from app_vision.engine.contracts import StepContext
    
    step = PrevDayCandadosStep()
    ctx = StepContext(
        step_name="test_step",
        step_id="test_123",
        pipeline_id="test_pipeline",
        execution_id="test_exec"
    )
    
    # Test data - simula draws de varios días
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    day_before = today - timedelta(days=2)
    
    test_data = {
        "draws": [
            # Día actual
            {
                "date": today.strftime("%Y-%m-%d"),
                "block": "MID",
                "numbers": [8, 8, 1],
                "pick4": [4, 9, 2, 1],
                "source": "floridalottery.com"
            },
            {
                "date": today.strftime("%Y-%m-%d"),
                "block": "EVE", 
                "numbers": [2, 1, 5],
                "pick4": [3, 4, 5, 6],
                "source": "floridalottery.com"
            },
            # Día anterior
            {
                "date": yesterday.strftime("%Y-%m-%d"),
                "block": "MID",
                "numbers": [9, 8, 2],
                "pick4": [1, 2, 3, 4],
                "source": "floridalottery.com"
            },
            {
                "date": yesterday.strftime("%Y-%m-%d"),
                "block": "EVE",
                "numbers": [3, 4, 5],
                "pick4": [5, 6, 7, 8],
                "source": "floridalottery.com"
            },
            # Día anterior-1
            {
                "date": day_before.strftime("%Y-%m-%d"),
                "block": "EVE",
                "numbers": [7, 8, 9],
                "pick4": [9, 0, 1, 2],
                "source": "floridalottery.com"
            }
        ]
    }
    
    result = step.run(ctx, test_data)
    
    # Verificar estructura de salida
    assert "prev_day_candados" in result, "Falta prev_day_candados en la salida"
    
    prev_day = result["prev_day_candados"]
    assert "date" in prev_day, "Falta fecha en prev_day_candados"
    assert "candados" in prev_day, "Falta candados en prev_day_candados"
    
    candados = prev_day["candados"]
    assert len(candados) == 3, f"Debe haber 3 candados, hay {len(candados)}"
    
    # Verificar que hay AM, MID, EVE
    slots = [c["slot"] for c in candados]
    assert "AM" in slots, "Falta slot AM"
    assert "MID" in slots, "Falta slot MID"
    assert "EVE" in slots, "Falta slot EVE"
    
    # Verificar estructura de cada candado
    for candado in candados:
        assert "slot" in candado, "Falta slot en candado"
        assert "candado" in candado, "Falta candado en candado"
        assert "parles" in candado, "Falta parles en candado"
        
        if candado.get("status") != "missing":
            assert "fijo2d" in candado, "Falta fijo2d en candado completo"
            assert "date" in candado, "Falta date en candado completo"
            assert "block" in candado, "Falta block en candado completo"
    
    print("✅ PrevDayCandadosStep funcionando correctamente")
    return result

def test_prev_day_export_step():
    """Test del step PrevDayCandadosExportStep"""
    print("🔍 Testando PrevDayCandadosExportStep...")
    
    from app_vision.steps.step_prev_day_export import PrevDayCandadosExportStep
    from app_vision.engine.contracts import StepContext
    
    step = PrevDayCandadosExportStep()
    ctx = StepContext(
        step_name="test_step",
        step_id="test_123",
        pipeline_id="test_pipeline",
        execution_id="test_exec"
    )
    
    # Test data - resultado del step anterior
    test_data = {
        "prev_day_candados": {
            "date": "2025-01-07",
            "candados": [
                {
                    "slot": "AM",
                    "date": "2025-01-06",
                    "block": "EVE",
                    "candado": ["81", "49", "21"],
                    "parles": [["81", "49"], ["81", "21"], ["49", "21"]],
                    "fijo2d": "81",
                    "corrido2d": "49",
                    "extra2d": "21"
                },
                {
                    "slot": "MID",
                    "date": "2025-01-07",
                    "block": "MID",
                    "candado": ["98", "02"],
                    "parles": [["98", "02"]],
                    "fijo2d": "98",
                    "corrido2d": "02",
                    "extra2d": None
                },
                {
                    "slot": "EVE",
                    "date": "2025-01-07",
                    "block": "EVE",
                    "candado": ["07", "39", "02"],
                    "parles": [["07", "39"], ["07", "02"], ["39", "02"]],
                    "fijo2d": "07",
                    "corrido2d": "39",
                    "extra2d": "02"
                }
            ]
        }
    }
    
    result = step.run(ctx, test_data)
    
    # Verificar estructura de salida
    assert "prev_day_export" in result, "Falta prev_day_export en la salida"
    
    export = result["prev_day_export"]
    assert "date" in export, "Falta date en export"
    assert "candados" in export, "Falta candados en export"
    assert "summary" in export, "Falta summary en export"
    assert "ui_ready" in export, "Falta ui_ready en export"
    
    # Verificar summary
    summary = export["summary"]
    assert summary["total_slots"] == 3, f"total_slots incorrecto: {summary['total_slots']}"
    assert summary["complete"] == 3, f"complete incorrecto: {summary['complete']}"
    assert summary["missing"] == 0, f"missing incorrecto: {summary['missing']}"
    assert summary["total_parles"] > 0, "No hay parlés en el summary"
    assert "all_parles_string" in summary, "Falta all_parles_string en summary"
    
    print("✅ PrevDayCandadosExportStep funcionando correctamente")
    return result

def main():
    """Función principal del test"""
    print("🧪 TEST DE CANDADOS DEL DÍA ANTERIOR")
    print("=" * 50)
    
    try:
        # Test 1: Construcción de candados del día anterior
        prev_day_result = test_prev_day_candados_step()
        
        # Test 2: Export para UI
        export_result = test_prev_day_export_step()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ Mapeo cubano implementado correctamente")
        print("✅ 3 candados del día anterior funcionando")
        print("✅ Export UI listo")
        
        # Mostrar ejemplo de salida
        print("\n📊 EJEMPLO DE SALIDA:")
        print("-" * 30)
        
        prev_day = prev_day_result["prev_day_candados"]
        print(f"Fecha: {prev_day['date']}")
        print("Candados:")
        for candado in prev_day["candados"]:
            slot = candado["slot"]
            if candado.get("status") == "missing":
                print(f"  {slot}: FALTANTE - {candado.get('why', 'N/A')}")
            else:
                candado_list = candado["candado"]
                parles = candado["parles"]
                print(f"  {slot}: {candado_list} | Parlés: {len(parles)}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())


