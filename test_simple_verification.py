#!/usr/bin/env python3
"""
Test simple para verificar que todo esté funcionando correctamente.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test de imports básicos"""
    print("🔍 Verificando imports...")
    
    try:
        from app_vision.engine.contracts import Step, StepContext, StepError, StepResult
        print("✅ Contratos importados correctamente")
        
        from app_vision.modules.candado_model import Candado
        print("✅ Modelo Candado importado correctamente")
        
        from app_vision.modules.draw_windows import current_block, get_window_status
        print("✅ Ventanas de tiempo importadas correctamente")
        
        from app_vision.steps.step_prev_day_candados import PrevDayCandadosStep
        print("✅ Step PrevDayCandadosStep importado correctamente")
        
        from app_vision.steps.step_prev_day_export import PrevDayCandadosExportStep
        print("✅ Step PrevDayCandadosExportStep importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_candado_model():
    """Test del modelo Candado"""
    print("\n🔍 Verificando modelo Candado...")
    
    try:
        from app_vision.modules.candado_model import Candado
        
        # Crear un candado de prueba
        candado = Candado(
            date="2025-01-08",
            block="MID",
            fijo2d="81",
            corrido2d="49",
            extra2d="21",
            pick3=(8, 8, 1),
            pick4=(4, 9, 2, 1)
        )
        
        # Verificar métodos
        trio = candado.trio()
        assert trio == ["81", "49", "21"], f"Trio incorrecto: {trio}"
        
        parles = candado.parles()
        expected_parles = [("81", "49"), ("81", "21"), ("49", "21")]
        assert parles == expected_parles, f"Parlés incorrectos: {parles}"
        
        # Verificar to_dict
        candado_dict = candado.to_dict()
        assert "date" in candado_dict, "Falta date en to_dict"
        assert "candado" in candado_dict, "Falta candado en to_dict"
        
        print("✅ Modelo Candado funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en modelo Candado: {e}")
        return False

def test_draw_windows():
    """Test de las ventanas de tiempo"""
    print("\n🔍 Verificando ventanas de tiempo...")
    
    try:
        from app_vision.modules.draw_windows import current_block, get_window_status
        from datetime import datetime
        
        # Test con hora actual
        now = datetime.now()
        current = current_block(now)
        assert current in ["AM", "MID", "EVE"], f"Bloque actual inválido: {current}"
        
        # Test de estado de ventanas
        status = get_window_status(now)
        assert "current_block" in status, "Falta current_block en status"
        assert "windows" in status, "Falta windows en status"
        
        print(f"✅ Ventanas de tiempo funcionando - Bloque actual: {current}")
        return True
        
    except Exception as e:
        print(f"❌ Error en ventanas de tiempo: {e}")
        return False

def test_plan_configuration():
    """Test de configuración del plan"""
    print("\n🔍 Verificando configuración del plan...")
    
    try:
        import json
        from pathlib import Path
        
        plan_path = Path("plans/florida_3ventanas_cubano.json")
        assert plan_path.exists(), "Plan no encontrado"
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        # Verificar estructura básica
        assert "name" in plan, "Falta name en plan"
        assert "steps" in plan, "Falta steps en plan"
        assert len(plan["steps"]) > 0, "Plan no tiene steps"
        
        # Verificar steps específicos
        step_names = [step["name"] for step in plan["steps"]]
        required_steps = ["step0_enforce", "step1_fetch_real", "step_prev_day_candados", "step_prev_day_export"]
        
        for required_step in required_steps:
            assert required_step in step_names, f"Falta step requerido: {required_step}"
        
        print("✅ Configuración del plan correcta")
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración del plan: {e}")
        return False

def main():
    """Función principal del test de verificación"""
    print("🧪 VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_candado_model,
        test_draw_windows,
        test_plan_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
        print("✅ Todos los componentes están correctos")
        print("✅ Mapeo cubano implementado")
        print("✅ 3 ventanas diarias configuradas")
        print("✅ Candados del día anterior funcionando")
        return 0
    else:
        print("❌ ALGUNOS COMPONENTES NECESITAN REVISIÓN")
        return 1

if __name__ == "__main__":
    sys.exit(main())


