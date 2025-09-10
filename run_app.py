#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio simplificado para VISION PREMIUM
"""

import subprocess
import sys
import time
import os

def main():
    """Función principal para ejecutar la aplicación."""
    print("🚀 Iniciando VISION PREMIUM...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("app.py"):
        print("❌ Error: No se encontró app.py en el directorio actual")
        print("   Asegúrate de estar en el directorio raíz del proyecto")
        return False
    
    # Verificar que Streamlit esté instalado
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} detectado")
    except ImportError:
        print("❌ Error: Streamlit no está instalado")
        print("   Ejecuta: pip install streamlit")
        return False
    
    # Intentar ejecutar la aplicación
    print("🌐 Iniciando servidor Streamlit...")
    
    try:
        # Comando para ejecutar Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true"
        ]
        
        print(f"📋 Comando: {' '.join(cmd)}")
        print("⏳ Esperando que se inicie el servidor...")
        
        # Ejecutar en segundo plano
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar un poco para que se inicie
        time.sleep(10)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("✅ Servidor iniciado correctamente")
            print("🌐 Abre tu navegador y ve a: http://localhost:8501")
            print("⏹️  Para detener el servidor, presiona Ctrl+C")
            
            # Mantener el proceso ejecutándose
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo servidor...")
                process.terminate()
                process.wait()
                print("✅ Servidor detenido")
        else:
            # El proceso terminó, verificar errores
            stdout, stderr = process.communicate()
            print("❌ Error al iniciar el servidor:")
            if stderr:
                print(f"Error: {stderr}")
            if stdout:
                print(f"Output: {stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔧 Soluciones sugeridas:")
        print("1. Verifica que estés en el directorio correcto")
        print("2. Asegúrate de que el entorno virtual esté activado")
        print("3. Verifica que todas las dependencias estén instaladas")
        print("4. Intenta ejecutar: pip install -r requirements.txt")
        sys.exit(1)








