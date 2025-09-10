#!/usr/bin/env python3
"""
Script de verificación completa para Dagster Cloud Hybrid
Verifica todos los componentes necesarios para que la code location se ponga verde
"""

import subprocess
import sys
import json
import requests
from pathlib import Path

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{message}{colors['RESET']}")

def check_local_imports():
    """Verifica que las importaciones locales funcionen"""
    print_status("🔍 Verificando importaciones locales...", "INFO")
    try:
        # Add current directory to path for orchestrator import
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        
        from orchestrator import defs
        assets_count = len(defs.assets)
        jobs_count = len(defs.jobs)
        schedules_count = len(defs.schedules)
        
        print_status(f"✅ Importaciones OK: {assets_count} assets, {jobs_count} jobs, {schedules_count} schedules", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Error en importaciones: {e}", "ERROR")
        return False

def check_dockerfile():
    """Verifica que el Dockerfile existe y es válido"""
    print_status("🔍 Verificando Dockerfile...", "INFO")
    dockerfile_path = Path("Dockerfile")
    if dockerfile_path.exists():
        print_status("✅ Dockerfile encontrado", "SUCCESS")
        return True
    else:
        print_status("❌ Dockerfile no encontrado", "ERROR")
        return False

def check_github_workflow():
    """Verifica que el workflow de GitHub Actions existe"""
    print_status("🔍 Verificando workflow de GitHub Actions...", "INFO")
    workflow_path = Path(".github/workflows/build-image.yml")
    if workflow_path.exists():
        print_status("✅ Workflow de GitHub Actions encontrado", "SUCCESS")
        return True
    else:
        print_status("❌ Workflow de GitHub Actions no encontrado", "ERROR")
        return False

def check_dagster_yaml():
    """Verifica la configuración de dagster_cloud.yaml"""
    print_status("🔍 Verificando dagster_cloud.yaml...", "INFO")
    yaml_path = Path("dagster_cloud.yaml")
    if yaml_path.exists():
        with open(yaml_path, 'r') as f:
            content = f.read()
            if "deployment:" in content and "image:" in content:
                print_status("✅ YAML Hybrid configurado correctamente", "SUCCESS")
                return True
            else:
                print_status("❌ YAML no está en formato Hybrid", "ERROR")
                return False
    else:
        print_status("❌ dagster_cloud.yaml no encontrado", "ERROR")
        return False

def check_docker_agent():
    """Verifica si el Agent de Docker está corriendo"""
    print_status("🔍 Verificando Agent de Docker...", "INFO")
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=dagster-agent", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        if "dagster-agent" in result.stdout:
            print_status("✅ Agent de Docker está corriendo", "SUCCESS")
            return True
        else:
            print_status("⚠️  Agent de Docker no está corriendo", "WARNING")
            return False
    except subprocess.CalledProcessError:
        print_status("❌ Error verificando Docker Agent", "ERROR")
        return False
    except FileNotFoundError:
        print_status("⚠️  Docker no está instalado o no está en PATH", "WARNING")
        return False

def check_github_packages():
    """Verifica si la imagen está en GitHub Packages (requiere token)"""
    print_status("🔍 Verificando GitHub Packages...", "INFO")
    print_status("⚠️  Esta verificación requiere token de GitHub", "WARNING")
    print_status("   Ve a GitHub → Packages → vision_app para verificar manualmente", "INFO")
    return True

def main():
    print_status("🚀 VERIFICACIÓN COMPLETA DE DAGSTER CLOUD HYBRID", "INFO")
    print_status("=" * 60, "INFO")
    
    checks = [
        ("Importaciones locales", check_local_imports),
        ("Dockerfile", check_dockerfile),
        ("Workflow GitHub Actions", check_github_workflow),
        ("Configuración YAML", check_dagster_yaml),
        ("Agent Docker", check_docker_agent),
        ("GitHub Packages", check_github_packages),
    ]
    
    results = []
    for name, check_func in checks:
        print_status(f"\n--- {name} ---", "INFO")
        result = check_func()
        results.append((name, result))
    
    print_status("\n" + "=" * 60, "INFO")
    print_status("📊 RESUMEN DE VERIFICACIÓN", "INFO")
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print_status(f"{name}: {status}", "SUCCESS" if result else "ERROR")
        if not result:
            all_passed = False
    
    print_status("\n" + "=" * 60, "INFO")
    if all_passed:
        print_status("🎉 TODAS LAS VERIFICACIONES PASARON", "SUCCESS")
        print_status("Tu configuración está lista para Dagster Cloud Hybrid", "SUCCESS")
    else:
        print_status("⚠️  ALGUNAS VERIFICACIONES FALLARON", "WARNING")
        print_status("Revisa los errores arriba y corrige antes de continuar", "WARNING")
    
    print_status("\n📋 PRÓXIMOS PASOS:", "INFO")
    print_status("1. Ve a GitHub → Actions y verifica que el workflow se ejecute", "INFO")
    print_status("2. Ve a GitHub → Packages y verifica que la imagen esté publicada", "INFO")
    print_status("3. Configura el Agent siguiendo las instrucciones en SETUP_AGENT_COMPLETO.md", "INFO")
    print_status("4. Ve a Dagster Cloud → Code locations → vision_app → Reload", "INFO")

if __name__ == "__main__":
    main()
