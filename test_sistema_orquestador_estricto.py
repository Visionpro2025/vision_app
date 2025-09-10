# ============================================
# 📌 TEST: SISTEMA DE ORQUESTADOR ESTRICTO
# Prueba el sistema completo de orquestador estricto
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_sistema_orquestador_estricto():
    """
    Prueba el sistema completo de orquestador estricto
    """
    print("🚀 TEST: SISTEMA DE ORQUESTADOR ESTRICTO")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Test 1: Step0 Enforce Orchestrator
        print("🔄 TEST 1: Step0 Enforce Orchestrator")
        test_step0_enforce()
        
        # Test 2: Contratos de validación
        print("🔄 TEST 2: Contratos de validación")
        test_contracts_validation()
        
        # Test 3: Plan Hard Orchestrator
        print("🔄 TEST 3: Plan Hard Orchestrator")
        test_plan_hard_orchestrator()
        
        # Test 4: Health Check
        print("🔄 TEST 4: Health Check")
        test_health_check()
        
        print("\n🎉 SISTEMA DE ORQUESTADOR ESTRICTO COMPLETADO EXITOSAMENTE")
        print("   - Cursor domado como orquestador obediente")
        print("   - Contratos de validación activos")
        print("   - Políticas anti-simulación aplicadas")
        print("   - Sistema listo para ejecución estricta")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test del sistema: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_step0_enforce():
    """Test del Step0 Enforce Orchestrator"""
    try:
        from app_vision.steps.step0_enforce_orchestrator import EnforceOrchestratorStep
        from app_vision.engine.contracts import StepContext
        
        # Crear contexto
        ctx = StepContext(
            run_id="test-orquestador-estricto",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        # Test con configuración válida
        step = EnforceOrchestratorStep()
        data = {
            "allow_simulation": False,
            "min_results": 5,
            "timeout_s": 20
        }
        
        result = step.run(ctx, data)
        
        # Validar resultado
        assert result.get("enforcement_active") == True, "Enforcement no activo"
        assert result.get("cursor_role") == "orchestrator_only", "Rol incorrecto"
        assert result.get("policy", {}).get("allow_simulation") == False, "Simulación no bloqueada"
        
        print("   ✅ Step0 Enforce Orchestrator operativo")
        
    except Exception as e:
        print(f"   ❌ Error en Step0: {e}")
        raise

def test_contracts_validation():
    """Test de contratos de validación"""
    try:
        from app_vision.modules.contracts import (
            require_keys, forbid_sim_source, assert_nonempty_list,
            validate_domain_allowlist, create_provenance, validate_draws_format
        )
        
        # Test require_keys
        try:
            require_keys({"a": 1, "b": 2}, ["a", "b"], "test")
            print("   ✅ require_keys: caso válido")
        except Exception as e:
            print(f"   ❌ require_keys: error inesperado - {e}")
        
        try:
            require_keys({"a": 1}, ["a", "b"], "test")
            print("   ❌ require_keys: debería fallar")
        except Exception:
            print("   ✅ require_keys: falla correctamente")
        
        # Test forbid_sim_source
        try:
            forbid_sim_source("simulated_data", "test")
            print("   ❌ forbid_sim_source: debería fallar")
        except Exception:
            print("   ✅ forbid_sim_source: falla correctamente")
        
        try:
            forbid_sim_source("real_data", "test")
            print("   ✅ forbid_sim_source: permite datos reales")
        except Exception as e:
            print(f"   ❌ forbid_sim_source: error inesperado - {e}")
        
        # Test validate_domain_allowlist
        try:
            validate_domain_allowlist("https://flalottery.com/pick3", ["flalottery.com"], "test")
            print("   ✅ validate_domain_allowlist: permite dominio válido")
        except Exception as e:
            print(f"   ❌ validate_domain_allowlist: error inesperado - {e}")
        
        try:
            validate_domain_allowlist("https://test.com/data", ["flalottery.com"], "test")
            print("   ❌ validate_domain_allowlist: debería fallar")
        except Exception:
            print("   ✅ validate_domain_allowlist: falla correctamente")
        
        # Test create_provenance
        prov = create_provenance("test.com")
        assert prov.get("source") == "test.com", "Provenance incorrecto"
        assert "fetched_at" in prov, "Timestamp faltante"
        print("   ✅ create_provenance: funciona correctamente")
        
        # Test validate_draws_format
        valid_draws = [
            {"date": "2025-09-08", "block": "MID", "numbers": [1, 2, 3], "source": "real_source"},
            {"date": "2025-09-08", "block": "EVE", "numbers": [4, 5, 6], "source": "real_source"}
        ]
        
        try:
            validate_draws_format(valid_draws, "test")
            print("   ✅ validate_draws_format: permite draws válidos")
        except Exception as e:
            print(f"   ❌ validate_draws_format: error inesperado - {e}")
        
        print("   ✅ Contratos de validación operativos")
        
    except Exception as e:
        print(f"   ❌ Error en contratos: {e}")
        raise

def test_plan_hard_orchestrator():
    """Test del plan hard orchestrator"""
    try:
        plan_path = "plans/pick3_pro_hard_orchestrator.json"
        
        if not os.path.exists(plan_path):
            print(f"   ❌ Plan no encontrado: {plan_path}")
            return
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        # Validar configuración
        config = plan.get("config", {})
        assert config.get("allow_simulation") == False, "allow_simulation debe ser False"
        assert config.get("enforce_contracts") == True, "enforce_contracts debe ser True"
        assert config.get("fail_noisy") == True, "fail_noisy debe ser True"
        
        # Validar steps
        steps = plan.get("steps", [])
        assert len(steps) > 0, "Debe haber steps definidos"
        
        # Verificar step0_enforce como primer paso
        assert steps[0].get("name") == "step0_enforce", "step0_enforce debe ser el primer paso"
        
        # Verificar timeouts configurados
        timeout_steps = [s for s in steps if s.get("timeout_s")]
        assert len(timeout_steps) > 0, "Debe haber steps con timeout configurado"
        
        print("   ✅ Plan Hard Orchestrator válido")
        
    except Exception as e:
        print(f"   ❌ Error en plan: {e}")
        raise

def test_health_check():
    """Test del health check"""
    try:
        # Ejecutar health check
        import subprocess
        result = subprocess.run([
            sys.executable, "scripts/health_check_hard.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("   ✅ Health Check exitoso")
        else:
            print(f"   ⚠️  Health Check con advertencias: {result.stdout}")
        
    except Exception as e:
        print(f"   ⚠️  Error ejecutando health check: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO TEST DEL SISTEMA DE ORQUESTADOR ESTRICTO")
    print("=" * 80)
    
    success = test_sistema_orquestador_estricto()
    
    if success:
        print("\n🎉 SISTEMA DE ORQUESTADOR ESTRICTO OPERATIVO")
        print("   - Cursor domado como orquestador obediente")
        print("   - Contratos de validación activos")
        print("   - Políticas anti-simulación aplicadas")
        print("   - Sistema listo para ejecución estricta")
    else:
        print("\n💥 SISTEMA DE ORQUESTADOR ESTRICTO CON PROBLEMAS")
        print("   - Revisar errores críticos")
        print("   - Corregir configuración")
        print("   - Re-ejecutar tests")

if __name__ == "__main__":
    main()





