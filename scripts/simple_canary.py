#!/usr/bin/env python3
"""
Canary simplificado para VISION PREMIUM.
Verifica que el sistema cumple la política global sin dependencias complejas.
"""

import json
import sys
import os
from pathlib import Path

def test_policy_file():
    """Verifica que existe y es válida la política global"""
    print("🔍 Verificando política global...")
    
    policy_path = Path("plans/policy_app.yaml")
    if not policy_path.exists():
        print("❌ FALLO: Archivo de política no encontrado")
        return False
    
    try:
        import yaml
        with open(policy_path, 'r', encoding='utf-8') as f:
            policy = yaml.safe_load(f)
        
        # Verificar configuración requerida
        app_config = policy.get("app", {})
        if app_config.get("orchestrator") != "cursor_only":
            print("❌ FALLO: Orquestador no es 'cursor_only'")
            return False
        
        if app_config.get("allow_simulation") != False:
            print("❌ FALLO: allow_simulation no es False")
            return False
        
        if app_config.get("require_sources") != True:
            print("❌ FALLO: require_sources no es True")
            return False
        
        if app_config.get("abort_on_empty") != True:
            print("❌ FALLO: abort_on_empty no es True")
            return False
        
        print("✅ Política global válida")
        return True
        
    except Exception as e:
        print(f"❌ FALLO: Error cargando política: {e}")
        return False

def test_sentinel_step():
    """Verifica que existe el step sentinela"""
    print("🔍 Verificando step sentinela...")
    
    sentinel_path = Path("app_vision/steps/step0_enforce_orchestrator.py")
    if not sentinel_path.exists():
        print("❌ FALLO: Step sentinela no encontrado")
        return False
    
    # Verificar que contiene la clase correcta
    content = sentinel_path.read_text(encoding='utf-8')
    if "EnforceOrchestratorStep" not in content:
        print("❌ FALLO: Clase EnforceOrchestratorStep no encontrada")
        return False
    
    if "cursor_only" not in content:
        print("❌ FALLO: Validación cursor_only no encontrada")
        return False
    
    print("✅ Step sentinela válido")
    return True

def test_guardrails():
    """Verifica que existen los guardrails"""
    print("🔍 Verificando guardrails...")
    
    guardrails_path = Path("app_vision/modules/guardrails.py")
    if not guardrails_path.exists():
        print("❌ FALLO: Guardrails no encontrados")
        return False
    
    # Verificar funciones principales
    content = guardrails_path.read_text(encoding='utf-8')
    required_functions = [
        "require_keys", "forbid_sim_source", "assert_nonempty_list",
        "assert_allowlisted", "apply_basic_guardrails"
    ]
    
    for func in required_functions:
        if func not in content:
            print(f"❌ FALLO: Función {func} no encontrada")
            return False
    
    print("✅ Guardrails válidos")
    return True

def test_audit_step():
    """Verifica que existe el step de auditoría"""
    print("🔍 Verificando step de auditoría...")
    
    audit_path = Path("app_vision/steps/stepZ_audit_emit.py")
    if not audit_path.exists():
        print("❌ FALLO: Step de auditoría no encontrado")
        return False
    
    content = audit_path.read_text(encoding='utf-8')
    if "AuditEmitStep" not in content:
        print("❌ FALLO: Clase AuditEmitStep no encontrada")
        return False
    
    print("✅ Step de auditoría válido")
    return True

def test_app_integration():
    """Verifica que la app principal integra la orquestación"""
    print("🔍 Verificando integración en app principal...")
    
    app_path = Path("app.py")
    if not app_path.exists():
        print("❌ FALLO: App principal no encontrada")
        return False
    
    content = app_path.read_text(encoding='utf-8')
    
    # Verificar que contiene enforcement de política
    if "enforce_global_policy" not in content:
        print("❌ FALLO: Función enforce_global_policy no encontrada")
        return False
    
    if "cursor_only" not in content:
        print("❌ FALLO: Validación cursor_only no encontrada en app")
        return False
    
    print("✅ App principal integrada correctamente")
    return True

def test_template_plan():
    """Verifica que existe la plantilla de plan"""
    print("🔍 Verificando plantilla de plan...")
    
    template_path = Path("plans/template_with_enforcement.json")
    if not template_path.exists():
        print("❌ FALLO: Plantilla de plan no encontrada")
        return False
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        # Verificar que contiene step0_enforce
        steps = template.get("steps", [])
        enforce_step = None
        for step in steps:
            if step.get("name") == "step0_enforce":
                enforce_step = step
                break
        
        if not enforce_step:
            print("❌ FALLO: step0_enforce no encontrado en plantilla")
            return False
        
        if enforce_step.get("class") != "EnforceOrchestratorStep":
            print("❌ FALLO: Clase incorrecta en step0_enforce")
            return False
        
        print("✅ Plantilla de plan válida")
        return True
        
    except Exception as e:
        print(f"❌ FALLO: Error cargando plantilla: {e}")
        return False

def main():
    """Función principal del canary simplificado"""
    print("🐤 CANARY SIMPLIFICADO - VISION PREMIUM")
    print("=" * 50)
    
    tests = [
        test_policy_file,
        test_sentinel_step,
        test_guardrails,
        test_audit_step,
        test_app_integration,
        test_template_plan
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ ERROR en {test.__name__}: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("🎉 CANARY SIMPLIFICADO SUPERADO")
        print("✅ Sistema cumple política global de orquestación")
        return 0
    else:
        print("❌ CANARY SIMPLIFICADO FALLÓ")
        print("⚠️  Sistema no cumple política global de orquestación")
        return 1

if __name__ == "__main__":
    sys.exit(main())


