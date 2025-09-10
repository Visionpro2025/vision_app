#!/usr/bin/env python3
"""
Check de dependencias "lint" para verificar que todas las librerías necesarias estén disponibles
"""

import importlib
import sys

# Dependencias requeridas para Dagster Cloud
# Nota: beautifulsoup4 se importa como 'bs4', python-dotenv como 'dotenv'
REQUIRED = [
    ("dagster", "dagster"), 
    ("dagster_cloud", "dagster_cloud"), 
    ("pandas", "pandas"), 
    ("requests", "requests"), 
    ("feedparser", "feedparser"), 
    ("beautifulsoup4", "bs4"),
    ("numpy", "numpy"),
    ("openai", "openai"),
    ("python-dotenv", "dotenv")
]

def check_dependencies():
    """Verifica que todas las dependencias requeridas estén disponibles"""
    missing = []
    
    for package_name, import_name in REQUIRED:
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"❌ {package_name}")
    
    if missing:
        print(f"\n❌ Dependencias faltantes: {', '.join(missing)}")
        print("💡 Agrega las dependencias faltantes a requirements.txt o pyproject.toml")
        return False
    else:
        print(f"\n✅ Todas las {len(REQUIRED)} dependencias están disponibles")
        return True

if __name__ == "__main__":
    print("🔍 Verificando dependencias para Dagster Cloud...")
    print("=" * 50)
    
    success = check_dependencies()
    
    if success:
        print("\n🎯 Listo para despliegue en Dagster Cloud")
        sys.exit(0)
    else:
        print("\n⚠️  Corrige las dependencias faltantes antes de hacer push")
        sys.exit(1)
