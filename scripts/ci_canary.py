#!/usr/bin/env python3
"""
Canary de salud para VISION PREMIUM.
Verifica que el sistema cumple la política global: sin simulaciones, datos reales, enforcement correcto.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, List

# Configuración del canary
ORDER_FILE = "orders/pick3-SELFTEST.json"
EXPECTED_POLICY_CHECKS = [
    '"cursor_role": "orchestrator_only"',
    '"allow_simulation": false',
    '"require_sources": true',
    '"abort_on_empty": true'
]
FORBIDDEN_PATTERNS = [
    "simul", "dummy", "test", "mock", "fake", "example",
    "placeholder", "sample", "demo", "trial"
]

def sh(cmd: List[str]) -> Tuple[int, str, str]:
    """Ejecuta comando y retorna (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Timeout: comando excedió 60 segundos"
    except Exception as e:
        return 1, "", f"Error ejecutando comando: {e}"

def create_test_order() -> None:
    """Crea un order de prueba mínimo para el canary"""
    orders_dir = Path("orders")
    orders_dir.mkdir(exist_ok=True)
    
    test_order = {
        "order_id": "pick3-SELFTEST",
        "description": "Test canary para verificar enforcement de política",
        "plan": "plans/pick3-basic.json",
        "inputs": {
            "test_mode": True,
            "validate_policy": True
        },
        "expected_outputs": [
            "policy_enforced",
            "guardrails_applied",
            "audit_generated"
        ]
    }
    
    with open(ORDER_FILE, "w", encoding="utf-8") as f:
        json.dump(test_order, f, indent=2)

def create_test_plan() -> None:
    """Crea un plan de prueba mínimo para el canary"""
    plans_dir = Path("plans")
    plans_dir.mkdir(exist_ok=True)
    
    test_plan = {
        "name": "pick3-basic-test",
        "description": "Plan básico para canary de salud",
        "steps": [
            {
                "name": "step0_enforce",
                "class": "EnforceOrchestratorStep",
                "inputs": {
                    "policy": {
                        "allow_simulation": False,
                        "require_sources": True,
                        "abort_on_empty": True
                    }
                },
                "timeout_s": 5
            },
            {
                "name": "step1_test",
                "class": "TestStep",
                "inputs": {
                    "test_data": "real_data_only",
                    "source": "https://flalottery.com"
                },
                "timeout_s": 10
            },
            {
                "name": "stepZ_audit",
                "class": "AuditEmitStep",
                "inputs": {
                    "summary": {
                        "test_completed": True,
                        "policy_enforced": True
                    }
                },
                "timeout_s": 5
            }
        ]
    }
    
    with open("plans/pick3-basic.json", "w", encoding="utf-8") as f:
        json.dump(test_plan, f, indent=2)

def check_policy_enforcement(output: str) -> bool:
    """Verifica que la política global fue aplicada correctamente"""
    print("🔍 Verificando enforcement de política...")
    
    for check in EXPECTED_POLICY_CHECKS:
        if check not in output:
            print(f"❌ FALLO: No se encontró '{check}' en la salida")
            return False
        print(f"✅ Encontrado: {check}")
    
    return True

def check_no_simulations(output: str, error: str) -> bool:
    """Verifica que no hay rastros de simulaciones en la salida"""
    print("🔍 Verificando ausencia de simulaciones...")
    
    combined_output = (output + error).lower()
    
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in combined_output:
            print(f"❌ FALLO: Se detectó patrón de simulación '{pattern}' en la salida")
            return False
    
    print("✅ No se detectaron simulaciones")
    return True

def check_guardrails_applied(output: str) -> bool:
    """Verifica que los guardrails fueron aplicados"""
    print("🔍 Verificando aplicación de guardrails...")
    
    guardrail_indicators = [
        "[GUARDRAIL]",
        "guardrails_applied",
        "policy_enforced",
        "sources_validated"
    ]
    
    found_indicators = [indicator for indicator in guardrail_indicators if indicator in output]
    
    if not found_indicators:
        print("❌ FALLO: No se detectaron indicadores de guardrails aplicados")
        return False
    
    print(f"✅ Guardrails aplicados: {found_indicators}")
    return True

def check_audit_generated() -> bool:
    """Verifica que se generaron archivos de auditoría"""
    print("🔍 Verificando generación de auditoría...")
    
    reports_dir = Path("reports")
    if not reports_dir.exists():
        print("❌ FALLO: Directorio de reportes no existe")
        return False
    
    audit_files = list(reports_dir.glob("audit_*.json"))
    if not audit_files:
        print("❌ FALLO: No se generaron archivos de auditoría")
        return False
    
    print(f"✅ Archivos de auditoría generados: {len(audit_files)}")
    return True

def main():
    """Función principal del canary"""
    print("🐤 INICIANDO CANARY DE SALUD - VISION PREMIUM")
    print("=" * 50)
    
    # Crear archivos de prueba si no existen
    if not Path(ORDER_FILE).exists():
        print("📝 Creando order de prueba...")
        create_test_order()
    
    if not Path("plans/pick3-basic.json").exists():
        print("📝 Creando plan de prueba...")
        create_test_plan()
    
    # Ejecutar el sistema con el order de prueba
    print(f"🚀 Ejecutando sistema con order: {ORDER_FILE}")
    
    # Comando para ejecutar el sistema (ajustar según tu implementación)
    cmd = [sys.executable, "-m", "app_vision", "run", "--order", ORDER_FILE]
    
    # Si no existe el módulo app_vision, usar streamlit como fallback
    if not Path("app_vision").exists():
        print("⚠️  Módulo app_vision no encontrado, usando streamlit como fallback")
        cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"]
    
    returncode, stdout, stderr = sh(cmd)
    
    print(f"📊 Código de salida: {returncode}")
    print(f"📝 Salida: {stdout[:500]}...")
    if stderr:
        print(f"⚠️  Errores: {stderr[:500]}...")
    
    # Verificaciones del canary
    checks_passed = 0
    total_checks = 4
    
    print("\n🔍 EJECUTANDO VERIFICACIONES...")
    print("-" * 30)
    
    # Check 1: Política aplicada
    if check_policy_enforcement(stdout):
        checks_passed += 1
    
    # Check 2: Sin simulaciones
    if check_no_simulations(stdout, stderr):
        checks_passed += 1
    
    # Check 3: Guardrails aplicados
    if check_guardrails_applied(stdout):
        checks_passed += 1
    
    # Check 4: Auditoría generada
    if check_audit_generated():
        checks_passed += 1
    
    # Resultado final
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {checks_passed}/{total_checks} verificaciones pasaron")
    
    if checks_passed == total_checks:
        print("🎉 CANARY SUPERADO - Sistema cumple política global")
        return 0
    else:
        print("❌ CANARY FALLÓ - Sistema no cumple política global")
        return 1

if __name__ == "__main__":
    sys.exit(main())




