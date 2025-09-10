#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIAGNÓSTICO ULTRA PROFUNDO - VISION PREMIUM
Para identificar EXACTAMENTE qué está bloqueando la aplicación
"""

import sys
import os
import time
import traceback
from pathlib import Path

def print_section(title):
    """Imprime una sección del diagnóstico."""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def check_system_info():
    """Verifica información del sistema."""
    print_section("INFORMACIÓN DEL SISTEMA")
    
    print(f"📁 Directorio actual: {Path.cwd()}")
    print(f"🐍 Python ejecutable: {sys.executable}")
    print(f"📦 Python version: {sys.version}")
    print(f"🖥️  Sistema operativo: {os.name}")
    print(f"📂 Archivos en directorio:")
    
    for file in Path.cwd().iterdir():
        if file.is_file():
            print(f"   📄 {file.name}")
        elif file.is_dir():
            print(f"   📁 {file.name}")

def check_imports_step_by_step():
    """Verifica importaciones paso a paso."""
    print_section("VERIFICACIÓN DE IMPORTACIONES PASO A PASO")
    
    # 1. Verificar módulos básicos
    basic_modules = ['os', 'sys', 'pathlib', 'time', 'traceback']
    for module in basic_modules:
        try:
            __import__(module)
            print(f"✅ {module}: OK")
        except Exception as e:
            print(f"❌ {module}: ERROR - {e}")
    
    # 2. Verificar Streamlit
    try:
        print("\n🌐 Probando Streamlit...")
        import streamlit as st
        print(f"   ✅ Streamlit importado: {st.__version__}")
        
        # Probar funciones básicas
        print("   🔧 Probando funciones básicas...")
        st.set_page_config(page_title="TEST", layout="wide")
        print("   ✅ set_page_config: OK")
        
        st.title("Test")
        print("   ✅ title: OK")
        
        st.write("Test")
        print("   ✅ write: OK")
        
    except Exception as e:
        print(f"   ❌ Error en Streamlit: {e}")
        traceback.print_exc()
        return False
    
    return True

def check_config_modules():
    """Verifica módulos de configuración."""
    print_section("VERIFICACIÓN DE MÓDULOS DE CONFIGURACIÓN")
    
    config_modules = [
        ('config.theme_config', 'get_theme'),
        ('config.performance_optimization', 'PerformanceOptimizer')
    ]
    
    for module_path, function_name in config_modules:
        try:
            print(f"🔧 Probando {module_path}...")
            module = __import__(module_path, fromlist=[function_name])
            function = getattr(module, function_name)
            print(f"   ✅ {module_path}.{function_name}: OK")
        except Exception as e:
            print(f"   ❌ {module_path}.{function_name}: ERROR - {e}")
            traceback.print_exc()

def check_file_permissions():
    """Verifica permisos de archivos."""
    print_section("VERIFICACIÓN DE PERMISOS DE ARCHIVOS")
    
    critical_files = ['app.py', 'app_working.py', 'app_ultra_simple.py']
    
    for file_name in critical_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                # Intentar leer el archivo
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(100)  # Leer solo los primeros 100 caracteres
                print(f"✅ {file_name}: Lectura OK")
                
                # Verificar si es ejecutable
                if os.access(file_path, os.R_OK):
                    print(f"   📖 Permiso de lectura: OK")
                else:
                    print(f"   ❌ Permiso de lectura: DENEGADO")
                    
            except Exception as e:
                print(f"❌ {file_name}: ERROR - {e}")
        else:
            print(f"❌ {file_name}: NO EXISTE")

def check_streamlit_installation():
    """Verifica la instalación de Streamlit."""
    print_section("VERIFICACIÓN DE INSTALACIÓN DE STREAMLIT")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit instalado: {st.__version__}")
        
        # Verificar ubicación
        streamlit_path = Path(st.__file__).parent
        print(f"📁 Ubicación: {streamlit_path}")
        
        # Verificar si está en el entorno virtual
        venv_path = Path("venv/Scripts")
        if venv_path.exists():
            print(f"🐍 Entorno virtual encontrado: {venv_path}")
            
            # Verificar streamlit.exe en venv
            streamlit_exe = venv_path / "streamlit.exe"
            if streamlit_exe.exists():
                print(f"✅ streamlit.exe en venv: OK")
            else:
                print(f"❌ streamlit.exe en venv: NO ENCONTRADO")
        else:
            print(f"❌ Entorno virtual no encontrado")
            
    except Exception as e:
        print(f"❌ Error verificando Streamlit: {e}")
        traceback.print_exc()

def test_minimal_streamlit():
    """Prueba una aplicación Streamlit mínima."""
    print_section("PRUEBA DE APLICACIÓN STREAMLIT MÍNIMA")
    
    try:
        import streamlit as st
        
        # Crear una aplicación mínima
        st.set_page_config(page_title="MINI TEST", layout="wide")
        st.title("🚀 TEST MÍNIMO")
        st.write("Si ves esto, Streamlit funciona")
        
        # Crear un botón
        if st.button("Probar Botón"):
            st.success("¡Botón funcionando!")
        
        print("✅ Aplicación mínima creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando aplicación mínima: {e}")
        traceback.print_exc()
        return False

def check_network_and_ports():
    """Verifica configuración de red y puertos."""
    print_section("VERIFICACIÓN DE RED Y PUERTOS")
    
    import socket
    
    # Verificar puertos comunes
    ports_to_check = [8501, 8502, 8503, 8504]
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"❌ Puerto {port}: OCUPADO")
            else:
                print(f"✅ Puerto {port}: DISPONIBLE")
                
        except Exception as e:
            print(f"❌ Error verificando puerto {port}: {e}")

def main():
    """Función principal de diagnóstico profundo."""
    print("🚀 INICIANDO DIAGNÓSTICO ULTRA PROFUNDO DE VISION PREMIUM")
    print("=" * 80)
    
    start_time = time.time()
    
    try:
        # Ejecutar todas las verificaciones
        check_system_info()
        check_imports_step_by_step()
        check_config_modules()
        check_file_permissions()
        check_streamlit_installation()
        test_minimal_streamlit()
        check_network_and_ports()
        
        # Resumen final
        print_section("RESUMEN DEL DIAGNÓSTICO")
        elapsed_time = time.time() - start_time
        print(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
        print("✅ Diagnóstico completado")
        
        print("\n🎯 RECOMENDACIONES:")
        print("1. Si todas las verificaciones pasaron, el problema está en la ejecución")
        print("2. Si hay errores de importación, reinstala las dependencias")
        print("3. Si hay problemas de permisos, ejecuta como administrador")
        print("4. Si hay conflictos de puertos, usa un puerto diferente")
        
    except Exception as e:
        print(f"💥 ERROR CRÍTICO EN EL DIAGNÓSTICO: {e}")
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🔍 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()








