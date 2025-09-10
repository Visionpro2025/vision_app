#!/usr/bin/env python3
"""
Script para verificar el estado de GitHub Actions
Verifica si el workflow build-image.yml se está ejecutando o ha terminado exitosamente
"""

import requests
import json
import time
from datetime import datetime, timedelta

def print_status(message, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{message}{colors['RESET']}")

def check_github_actions_status():
    """Verifica el estado de GitHub Actions usando la API pública"""
    print_status("🔍 Verificando estado de GitHub Actions...", "INFO")
    
    # URL de la API de GitHub para el workflow
    repo = "Visionpro2025/vision_app"
    workflow_name = "build-and-push-image"
    
    # URL para obtener los runs del workflow
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_name}.yml/runs"
    
    try:
        print_status(f"Consultando: {url}", "INFO")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get('workflow_runs', [])
            
            if runs:
                latest_run = runs[0]
                status = latest_run.get('status', 'unknown')
                conclusion = latest_run.get('conclusion', 'unknown')
                created_at = latest_run.get('created_at', 'unknown')
                
                print_status(f"✅ Último run encontrado:", "SUCCESS")
                print_status(f"   Estado: {status}", "INFO")
                print_status(f"   Conclusión: {conclusion}", "INFO")
                print_status(f"   Creado: {created_at}", "INFO")
                
                if status == 'completed' and conclusion == 'success':
                    print_status("🎉 Workflow ejecutado exitosamente!", "SUCCESS")
                    return True
                elif status == 'in_progress':
                    print_status("⏳ Workflow ejecutándose...", "WARNING")
                    return False
                elif status == 'completed' and conclusion == 'failure':
                    print_status("❌ Workflow falló", "ERROR")
                    return False
                else:
                    print_status(f"⚠️  Estado inesperado: {status} - {conclusion}", "WARNING")
                    return False
            else:
                print_status("❌ No se encontraron runs del workflow", "ERROR")
                return False
        else:
            print_status(f"❌ Error al consultar GitHub API: {response.status_code}", "ERROR")
            return False
            
    except requests.exceptions.RequestException as e:
        print_status(f"❌ Error de conexión: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Error inesperado: {e}", "ERROR")
        return False

def check_github_packages():
    """Verifica si la imagen está en GitHub Packages (requiere autenticación)"""
    print_status("🔍 Verificando GitHub Packages...", "INFO")
    print_status("⚠️  Esta verificación requiere autenticación", "WARNING")
    print_status("   Ve a https://github.com/Visionpro2025/vision_app/pkgs/container/vision_app", "INFO")
    print_status("   para verificar manualmente que la imagen esté publicada", "INFO")
    return True

def main():
    print_status("🚀 VERIFICACIÓN DE GITHUB ACTIONS", "INFO")
    print_status("=" * 50, "INFO")
    
    # Verificar estado del workflow
    workflow_ok = check_github_actions_status()
    
    print_status("\n" + "=" * 50, "INFO")
    
    # Verificar packages
    packages_ok = check_github_packages()
    
    print_status("\n" + "=" * 50, "INFO")
    print_status("📊 RESUMEN:", "INFO")
    
    if workflow_ok:
        print_status("✅ Workflow ejecutado exitosamente", "SUCCESS")
        print_status("✅ Imagen debería estar en GitHub Packages", "SUCCESS")
        print_status("\n🎯 PRÓXIMOS PASOS:", "INFO")
        print_status("1. Verifica que la imagen esté en GitHub Packages", "INFO")
        print_status("2. Configura el Agent de Dagster Cloud", "INFO")
        print_status("3. Recarga la code location en Dagster Cloud", "INFO")
    else:
        print_status("⚠️  Workflow no completado o falló", "WARNING")
        print_status("\n🔧 ACCIONES RECOMENDADAS:", "INFO")
        print_status("1. Ve a GitHub → Actions y revisa los logs", "INFO")
        print_status("2. Si falló, revisa el Dockerfile y dependencias", "INFO")
        print_status("3. Re-ejecuta el workflow si es necesario", "INFO")

if __name__ == "__main__":
    main()
