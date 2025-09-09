#!/usr/bin/env python3
"""
Test específico para verificar la regla fija de CANDADO.
Valida que el sistema sigue la regla determinista sin inventos.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_bolita_transform_fixed():
    """Test de la función derive_bolita con regla fija"""
    print("🔍 Testando derive_bolita con regla fija...")
    
    from modules.bolita_transform import FLDraw, derive_bolita
    
    # Test case 1: Pick3 + Pick4 del mismo bloque
    focus = FLDraw(
        date="2025-01-08",
        block="MID",
        pick3=(8, 8, 1),
        pick4=(4, 9, 2, 1)
    )
    
    result = derive_bolita(
        focus=focus,
        other_block_pick3_last2="21",
        force_min_candado=True
    )
    
    # Verificar regla fija
    assert result["fijo"]["2d"] == "81", f"FIJO 2D incorrecto: {result['fijo']['2d']}"
    assert "49" in result["corridos"], f"CORRIDO del Pick4 no encontrado: {result['corridos']}"
    assert "21" in result["corridos"], f"CORRIDO del otro bloque no encontrado: {result['corridos']}"
    assert result["candado"] == ["81", "49", "21"], f"CANDADO incorrecto: {result['candado']}"
    
    print("✅ Test case 1 pasado: Pick3 + Pick4 + otro bloque")
    
    # Test case 2: Solo Pick3 (sin Pick4)
    focus2 = FLDraw(
        date="2025-01-08",
        block="EVE",
        pick3=(3, 2, 1),
        pick4=None
    )
    
    result2 = derive_bolita(
        focus=focus2,
        other_block_pick3_last2="45",
        force_min_candado=True
    )
    
    assert result2["fijo"]["2d"] == "21", f"FIJO 2D incorrecto: {result2['fijo']['2d']}"
    assert "45" in result2["corridos"], f"CORRIDO del otro bloque no encontrado: {result2['corridos']}"
    assert result2["candado"] == ["21", "45"], f"CANDADO incorrecto: {result2['candado']}"
    
    print("✅ Test case 2 pasado: Solo Pick3 + otro bloque")
    
    # Test case 3: Candado insuficiente (debe fallar)
    focus3 = FLDraw(
        date="2025-01-08",
        block="MID",
        pick3=(1, 2, 3),
        pick4=None
    )
    
    try:
        derive_bolita(
            focus=focus3,
            other_block_pick3_last2=None,
            force_min_candado=True
        )
        assert False, "Debería haber fallado con candado insuficiente"
    except ValueError as e:
        assert "Candado insuficiente" in str(e), f"Error incorrecto: {e}"
        print("✅ Test case 3 pasado: Candado insuficiente detectado correctamente")
    
    print("✅ Todos los tests de derive_bolita pasaron")

def test_last2_other_block_step():
    """Test del step Last2OtherBlockStep"""
    print("🔍 Testando Last2OtherBlockStep...")
    
    from app_vision.steps.step_last2_other_block import Last2OtherBlockStep
    from app_vision.engine.contracts import StepContext
    
    step = Last2OtherBlockStep()
    ctx = StepContext(
        step_name="test_step",
        step_id="test_123",
        pipeline_id="test_pipeline",
        execution_id="test_exec"
    )
    
    # Test data
    test_data = {
        "draws": [
            {
                "date": "2025-01-08",
                "block": "MID",
                "numbers": [8, 8, 1],
                "pick4": [4, 9, 2, 1]
            },
            {
                "date": "2025-01-08",
                "block": "EVE",
                "numbers": [2, 1, 5],
                "pick4": [3, 4, 5, 6]
            }
        ],
        "current_block": "MID"
    }
    
    result = step.run(ctx, test_data)
    
    assert result["last2"] == "15", f"Last2 incorrecto: {result['last2']}"
    assert result["other_block"] == "EVE", f"Otro bloque incorrecto: {result['other_block']}"
    
    print("✅ Last2OtherBlockStep funcionando correctamente")

def test_bolita_from_florida_step():
    """Test del step BolitaFromFloridaStep con regla fija"""
    print("🔍 Testando BolitaFromFloridaStep con regla fija...")
    
    from app_vision.steps.florida_lottery_steps import BolitaFromFloridaStep
    from app_vision.engine.contracts import StepContext
    
    step = BolitaFromFloridaStep()
    ctx = StepContext(
        step_name="test_step",
        step_id="test_123",
        pipeline_id="test_pipeline",
        execution_id="test_exec"
    )
    
    # Test data
    test_data = {
        "focus": {
            "date": "2025-01-08",
            "block": "MID",
            "pick3": [8, 8, 1],
            "pick4": [4, 9, 2, 1]
        },
        "other_pick3_last2": "21",
        "force_min_candado": True
    }
    
    result = step.run(ctx, test_data)
    
    bolita = result["bolita"]
    assert bolita["fijo"]["2d"] == "81", f"FIJO 2D incorrecto: {bolita['fijo']['2d']}"
    assert "49" in bolita["corridos"], f"CORRIDO del Pick4 no encontrado: {bolita['corridos']}"
    assert "21" in bolita["corridos"], f"CORRIDO del otro bloque no encontrado: {bolita['corridos']}"
    assert bolita["candado"] == ["81", "49", "21"], f"CANDADO incorrecto: {bolita['candado']}"
    
    print("✅ BolitaFromFloridaStep funcionando correctamente")

def main():
    """Función principal del test"""
    print("🧪 TEST DE REGLA FIJA DE CANDADO")
    print("=" * 50)
    
    try:
        test_bolita_transform_fixed()
        test_last2_other_block_step()
        test_bolita_from_florida_step()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS LOS TESTS PASARON")
        print("✅ Regla fija de CANDADO implementada correctamente")
        print("✅ Sistema determinista sin inventos")
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FALLÓ: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())


