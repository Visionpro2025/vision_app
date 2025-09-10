#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE DIAGNÓSTICO - VISION PREMIUM
Para identificar exactamente dónde falla la aplicación
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Prueba todas las importaciones paso a paso."""
    print("🔍 Probando importaciones...")
    
    try:
        print("1. Importando streamlit...")
        import streamlit as st
        print(f"   ✅ Streamlit {st.__version__} importado")
    except Exception as e:
        print(f"   ❌ Error en streamlit: {e}")
        return False
    
    try:
        print("2. Importando pathlib...")
        from pathlib import Path
        print("   ✅ Pathlib importado")
    except Exception as e:
        print(f"   ❌ Error en pathlib: {e}")
        return False
    
    try:
        print("3. Importando sys...")
        import sys
        print("   ✅ Sys importado")
    except Exception as e:
        print(f"   ❌ Error en sys: {e}")
        return False
    
    try:
        print("4. Importando os...")
        import os
        print("   ✅ Os importado")
    except Exception as e:
        print(f"   ❌ Error en os: {e}")
        return False
    
    return True

def test_config_imports():
    """Prueba las importaciones de configuración."""
    print("\n🔧 Probando importaciones de configuración...")
    
    try:
        print("1. Importando theme_config...")
        from config.theme_config import get_theme, apply_theme_config
        print("   ✅ Theme config importado")
    except Exception as e:
        print(f"   ❌ Error en theme_config: {e}")
        return False
    
    try:
        print("2. Importando performance_optimization...")
        from config.performance_optimization import PerformanceOptimizer, optimized_metric, CacheManager
        print("   ✅ Performance optimization importado")
    except Exception as e:
        print(f"   ❌ Error en performance_optimization: {e}")
        return False
    
    return True

def test_streamlit_config():
    """Prueba la configuración de Streamlit."""
    print("\n🌐 Probando configuración de Streamlit...")
    
    try:
        import streamlit as st
        
        print("1. Probando set_page_config...")
        st.set_page_config(
            page_title="TEST",
            page_icon="",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        print("   ✅ set_page_config funcionó")
        
        print("2. Probando título...")
        st.title("Test")
        print("   ✅ Título funcionó")
        
        print("3. Probando sidebar...")
        with st.sidebar:
            st.write("Test sidebar")
        print("   ✅ Sidebar funcionó")
        
        print("4. Probando métricas...")
        st.metric("Test", "Value")
        print("   ✅ Métricas funcionaron")
        
    except Exception as e:
        print(f"   ❌ Error en Streamlit: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_performance_functions():
    """Prueba las funciones de rendimiento."""
    print("\n⚡ Probando funciones de rendimiento...")
    
    try:
        from config.performance_optimization import monitor_performance, get_optimization_recommendations
        
        print("1. Probando monitor_performance...")
        metrics = monitor_performance()
        print(f"   ✅ Métricas obtenidas: {metrics}")
        
        print("2. Probando get_optimization_recommendations...")
        recommendations = get_optimization_recommendations()
        print(f"   ✅ Recomendaciones obtenidas: {recommendations}")
        
    except Exception as e:
        print(f"   ❌ Error en funciones de rendimiento: {e}")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Función principal de diagnóstico."""
    print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DE VISION PREMIUM")
    print("=" * 60)
    
    # Verificar directorio
    if not Path("app.py").exists():
        print("❌ Error: No estás en el directorio correcto")
        print("   Asegúrate de estar en la raíz del proyecto vision_app")
        return False
    
    print(f"📁 Directorio actual: {Path.cwd()}")
    print(f"📄 Archivo app.py encontrado: {Path('app.py').exists()}")
    
    # Pruebas paso a paso
    tests = [
        ("Importaciones básicas", test_imports),
        ("Importaciones de configuración", test_config_imports),
        ("Configuración de Streamlit", test_streamlit_config),
        ("Funciones de rendimiento", test_performance_functions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name}: EXITOSO")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"💥 {test_name}: ERROR CRÍTICO - {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Resultado general: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La aplicación debería funcionar.")
        print("💡 Intenta ejecutar: streamlit run app.py")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        print("🔧 La aplicación puede no funcionar correctamente.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)








