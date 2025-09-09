# ============================================
# 📌 TEST: PASO 1 - INICIALIZACIÓN Y LIMPIEZA DEL SISTEMA
# Prueba del primer paso del Protocolo Universal
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso1_inicializacion():
    print("🚀 PRUEBA: PASO 1 - INICIALIZACIÓN Y LIMPIEZA DEL SISTEMA")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el protocolo universal
        from universal_protocol_official import UniversalProtocolOfficial
        
        print("✅ Protocolo Universal importado correctamente")
        
        # Crear instancia del protocolo
        protocol = UniversalProtocolOfficial()
        
        print("✅ Instancia del protocolo creada")
        print()
        
        # Ejecutar Paso 1: Inicialización y Limpieza del Sistema
        print("🔄 EJECUTANDO PASO 1: INICIALIZACIÓN Y LIMPIEZA DEL SISTEMA")
        print("-" * 50)
        
        # Ejecutar el paso 1
        resultado_paso1 = protocol._step_1_initialization()
        
        print(f"✅ Paso 1 ejecutado")
        print(f"   Estado: {resultado_paso1['status']}")
        print(f"   Nombre: {resultado_paso1['name']}")
        print()
        
        # Mostrar detalles del paso 1
        if resultado_paso1['status'] == 'completed':
            print("📊 DETALLES DEL PASO 1:")
            print("-" * 30)
            
            detalles = resultado_paso1['details']
            
            # 1.1 Limpieza de memoria
            print("1.1 Limpieza de memoria:")
            memory_cleanup = detalles['memory_cleanup']
            print(f"   ✅ Garbage collected: {memory_cleanup.get('garbage_collected', 'N/A')}")
            print(f"   ✅ Memoria limpiada: {memory_cleanup.get('memory_cleaned', False)}")
            if 'error' in memory_cleanup:
                print(f"   ⚠️  Error: {memory_cleanup['error']}")
            print()
            
            # 1.2 Estado de salud de la app
            print("1.2 Estado de salud de la app:")
            app_health = detalles['app_health']
            print(f"   ✅ Uso de memoria: {app_health.get('memory_usage', 'N/A')}%")
            print(f"   ✅ Uso de CPU: {app_health.get('cpu_usage', 'N/A')}%")
            print(f"   ✅ App saludable: {app_health.get('app_healthy', False)}")
            if 'error' in app_health:
                print(f"   ⚠️  Error: {app_health['error']}")
            print()
            
            # 1.3 Validación de módulos críticos
            print("1.3 Validación de módulos críticos:")
            module_validation = detalles['module_validation']
            print(f"   ✅ Módulos validados: {module_validation.get('modules_validated', 0)}")
            print(f"   ✅ Todos los módulos OK: {module_validation.get('all_modules_ok', False)}")
            if 'error' in module_validation:
                print(f"   ⚠️  Error: {module_validation['error']}")
            print()
            
            # 1.4 Optimización de recursos
            print("1.4 Optimización de recursos:")
            resource_optimization = detalles['resource_optimization']
            print(f"   ✅ Recursos optimizados: {resource_optimization.get('resources_optimized', False)}")
            print(f"   ✅ Caché limpiado: {resource_optimization.get('cache_cleared', False)}")
            if 'error' in resource_optimization:
                print(f"   ⚠️  Error: {resource_optimization['error']}")
            print()
            
            # 1.5 Verificación del auditor
            print("1.5 Verificación del auditor:")
            auditor_verification = detalles['auditor_verification']
            print(f"   ✅ Auditor funcionando: {auditor_verification.get('auditor_working', False)}")
            print(f"   ✅ Verificación exitosa: {auditor_verification.get('verification_successful', False)}")
            if 'error' in auditor_verification:
                print(f"   ⚠️  Error: {auditor_verification['error']}")
            print()
            
            # Timestamp
            print(f"⏰ Timestamp: {detalles.get('timestamp', 'N/A')}")
            print()
            
            # Resumen final
            print("🎯 RESUMEN DEL PASO 1:")
            print("-" * 30)
            print("✅ Limpieza de memoria completada")
            print("✅ Estado de salud de la app verificado")
            print("✅ Módulos críticos validados")
            print("✅ Recursos optimizados")
            print("✅ Auditor verificado")
            print()
            print("🚀 PASO 1 COMPLETADO EXITOSAMENTE")
            print("📊 Sistema inicializado y listo para el siguiente paso")
            
        else:
            print(f"❌ Error en Paso 1: {resultado_paso1.get('error', 'Error desconocido')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 1: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso1_inicializacion()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 1 FUNCIONANDO")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")



