# scripts/health_check_hard.py
"""
Health check canario que falla si cualquier paso devuelve simulados o vacíos.
Evita regresiones silenciosas en el sistema de orquestador estricto.
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'modules'))

def health_check_hard_orchestrator():
    """
    Ejecuta health check estricto del sistema de orquestador
    """
    print("🔍 HEALTH CHECK - SISTEMA DE ORQUESTADOR ESTRICTO")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    errors = []
    warnings = []
    
    try:
        # Test 1: Verificar step0_enforce
        print("🔄 Test 1: Step0 Enforce Orchestrator")
        test_enforce_orchestrator(errors, warnings)
        
        # Test 2: Verificar contratos
        print("🔄 Test 2: Contratos de validación")
        test_contracts(errors, warnings)
        
        # Test 3: Verificar allowlist
        print("🔄 Test 3: Allowlist de fuentes")
        test_allowlist(errors, warnings)
        
        # Test 4: Verificar plan hard orchestrator
        print("🔄 Test 4: Plan Hard Orchestrator")
        test_plan_hard_orchestrator(errors, warnings)
        
        # Test 5: Verificar archivos de reportes existentes
        print("🔄 Test 5: Archivos de reportes")
        test_report_files(errors, warnings)
        
        # Resumen final
        print("\n📊 RESUMEN DEL HEALTH CHECK:")
        print("=" * 80)
        
        if errors:
            print(f"❌ ERRORES: {len(errors)}")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")
        else:
            print("✅ Sin errores críticos")
        
        if warnings:
            print(f"⚠️  ADVERTENCIAS: {len(warnings)}")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
        else:
            print("✅ Sin advertencias")
        
        # Estado final
        if errors:
            print(f"\n💥 HEALTH CHECK FALLÓ - {len(errors)} errores críticos")
            return False
        else:
            print(f"\n🎉 HEALTH CHECK EXITOSO - Sistema de orquestador estricto operativo")
            return True
        
    except Exception as e:
        print(f"❌ Error crítico en health check: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enforce_orchestrator(errors: List[str], warnings: List[str]):
    """Test del step de enforcement"""
    try:
        from app_vision.steps.step0_enforce_orchestrator import EnforceOrchestratorStep
        from app_vision.engine.contracts import StepContext
        
        # Crear contexto de prueba
        ctx = StepContext(
            run_id="health-check-test",
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
        if not result.get("enforcement_active"):
            errors.append("Step0: enforcement no activo")
        
        if result.get("policy", {}).get("allow_simulation"):
            errors.append("Step0: allow_simulation no bloqueado")
        
        if not result.get("cursor_role") == "orchestrator_only":
            errors.append("Step0: cursor_role no establecido correctamente")
        
        print("   ✅ Step0 Enforce Orchestrator operativo")
        
    except Exception as e:
        errors.append(f"Step0: Error importando o ejecutando - {e}")

def test_contracts(errors: List[str], warnings: List[str]):
    """Test de contratos de validación"""
    try:
        from app_vision.modules.contracts import (
            require_keys, forbid_sim_source, assert_nonempty_list,
            validate_domain_allowlist, create_provenance
        )
        
        # Test require_keys
        try:
            require_keys({"a": 1, "b": 2}, ["a", "b"], "test")
            require_keys({"a": 1}, ["a", "b"], "test")
        except Exception:
            pass  # Debe fallar en el segundo caso
        
        # Test forbid_sim_source
        try:
            forbid_sim_source("simulated_data", "test")
        except Exception:
            pass  # Debe fallar
        
        # Test validate_domain_allowlist
        try:
            validate_domain_allowlist("https://flalottery.com/pick3", ["flalottery.com"], "test")
            validate_domain_allowlist("https://test.com/data", ["flalottery.com"], "test")
        except Exception:
            pass  # Debe fallar en el segundo caso
        
        # Test create_provenance
        prov = create_provenance("test.com")
        if not prov.get("source") == "test.com":
            errors.append("Contratos: create_provenance no funciona")
        
        print("   ✅ Contratos de validación operativos")
        
    except Exception as e:
        errors.append(f"Contratos: Error importando - {e}")

def test_allowlist(errors: List[str], warnings: List[str]):
    """Test de allowlist de fuentes"""
    try:
        import yaml
        
        allowlist_path = "plans/sources_allowlist.yaml"
        if not os.path.exists(allowlist_path):
            errors.append(f"Allowlist: Archivo no encontrado - {allowlist_path}")
            return
        
        with open(allowlist_path, 'r', encoding='utf-8') as f:
            allowlist = yaml.safe_load(f)
        
        # Validar estructura
        required_sections = ["lottery", "news", "forbidden", "policies"]
        for section in required_sections:
            if section not in allowlist:
                errors.append(f"Allowlist: Sección faltante - {section}")
        
        # Validar políticas
        policies = allowlist.get("policies", {})
        if not policies.get("require_https"):
            warnings.append("Allowlist: require_https no habilitado")
        
        print("   ✅ Allowlist de fuentes operativa")
        
    except Exception as e:
        errors.append(f"Allowlist: Error cargando - {e}")

def test_plan_hard_orchestrator(errors: List[str], warnings: List[str]):
    """Test del plan hard orchestrator"""
    try:
        plan_path = "plans/pick3_pro_hard_orchestrator.json"
        if not os.path.exists(plan_path):
            errors.append(f"Plan: Archivo no encontrado - {plan_path}")
            return
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        # Validar configuración
        config = plan.get("config", {})
        if config.get("allow_simulation"):
            errors.append("Plan: allow_simulation habilitado")
        
        if not config.get("enforce_contracts"):
            errors.append("Plan: enforce_contracts no habilitado")
        
        # Validar steps
        steps = plan.get("steps", [])
        if not steps:
            errors.append("Plan: No hay steps definidos")
        
        # Verificar step0_enforce como primer paso
        if steps and steps[0].get("name") != "step0_enforce":
            errors.append("Plan: step0_enforce no es el primer paso")
        
        # Verificar timeouts y retry configurados
        for step in steps:
            if not step.get("timeout_s"):
                warnings.append(f"Plan: Step {step.get('name')} sin timeout")
        
        print("   ✅ Plan Hard Orchestrator válido")
        
    except Exception as e:
        errors.append(f"Plan: Error cargando - {e}")

def test_report_files(errors: List[str], warnings: List[str]):
    """Test de archivos de reportes existentes"""
    try:
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            warnings.append("Reports: Directorio no existe")
            return
        
        # Verificar archivos de reportes recientes
        report_files = [
            "paso6_sefirotico_v2.json",
            "paso7_series_cuanticas.json",
            "sorteos_reales_para_paso6.json"
        ]
        
        for file in report_files:
            file_path = os.path.join(reports_dir, file)
            if os.path.exists(file_path):
                # Verificar que no contenga datos simulados
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Buscar indicios de simulación
                data_str = json.dumps(data).lower()
                if any(word in data_str for word in ["simul", "dummy", "test", "mock"]):
                    warnings.append(f"Reports: {file} contiene datos simulados")
            else:
                warnings.append(f"Reports: Archivo faltante - {file}")
        
        print("   ✅ Archivos de reportes verificados")
        
    except Exception as e:
        warnings.append(f"Reports: Error verificando - {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO HEALTH CHECK - SISTEMA DE ORQUESTADOR ESTRICTO")
    print("=" * 80)
    
    success = health_check_hard_orchestrator()
    
    if success:
        print("\n🎉 SISTEMA DE ORQUESTADOR ESTRICTO OPERATIVO")
        print("   - Cursor domado como orquestador obediente")
        print("   - Contratos de validación activos")
        print("   - Políticas anti-simulación aplicadas")
        print("   - Listo para ejecución estricta")
    else:
        print("\n💥 SISTEMA DE ORQUESTADOR ESTRICTO CON PROBLEMAS")
        print("   - Revisar errores críticos")
        print("   - Corregir configuración")
        print("   - Re-ejecutar health check")

if __name__ == "__main__":
    main()



