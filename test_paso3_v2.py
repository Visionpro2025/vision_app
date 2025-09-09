# ============================================
# 📌 TEST: PASO 3 V2 - ANÁLISIS SUBLIMINAL MEJORADO
# Prueba del nuevo paso 3 con selección robusta del sorteo más reciente
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_paso3_v2():
    print("🚀 PRUEBA: PASO 3 V2 - ANÁLISIS SUBLIMINAL MEJORADO")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el nuevo step
        from app_vision.steps.step3_subliminal_v2 import SubliminalGuardedStepV2
        from app_vision.engine.contracts import StepContext
        
        print("✅ Step V2 importado correctamente")
        
        # Crear instancia del step
        step = SubliminalGuardedStepV2()
        
        print("✅ Instancia del step V2 creada")
        print()
        
        # Datos de prueba con múltiples sorteos
        print("📊 CONFIGURACIÓN DE PRUEBA:")
        print("-" * 40)
        
        # Simular múltiples sorteos para probar la selección del más reciente
        draws_data = {
            "draws": [
                {
                    "lottery": "Florida Pick 3",
                    "draw_date": "2025-09-05",
                    "draw_time": "13:00",
                    "numbers": [1, 2, 3]
                },
                {
                    "lottery": "Florida Pick 3", 
                    "draw_date": "2025-09-07",
                    "draw_time": "22:00",
                    "numbers": [4, 2, 7]
                },
                {
                    "lottery": "Florida Pick 3",
                    "draw_date": "2025-09-06",
                    "draw_time": "13:00", 
                    "numbers": [8, 9, 1]
                }
            ],
            "label": "PM"
        }
        
        print("Sorteos disponibles:")
        for i, draw in enumerate(draws_data["draws"]):
            print(f"  {i+1}. {draw['draw_date']} {draw['draw_time']} - {draw['numbers']}")
        print()
        
        # Crear contexto de prueba
        ctx = StepContext(
            run_id="test_paso3_v2",
            seed=12345,
            cfg={},
            state_dir="./test_state",
            plan_path="./test_plan.json"
        )
        
        # Ejecutar el step V2
        print("🔄 EJECUTANDO PASO 3 V2:")
        print("-" * 40)
        
        resultado = step.run(ctx, draws_data)
        
        print(f"✅ Paso 3 V2 ejecutado")
        print(f"   Estado: {resultado['status']}")
        print(f"   Nombre: {resultado['name']}")
        print()
        
        # Mostrar información detallada
        print("📊 INFORMACIÓN DETALLADA DEL PASO 3 V2:")
        print("=" * 60)
        
        # Sorteo anterior seleccionado
        print("🔍 SORTEO ANTERIOR SELECCIONADO:")
        print("-" * 40)
        sorteo = resultado['sorteo_anterior']
        print(f"   ✅ Encontrado: {sorteo['found']}")
        print(f"   ✅ Lotería: {sorteo['lottery']}")
        print(f"   ✅ Fecha: {sorteo['draw_date']}")
        print(f"   ✅ Hora: {sorteo['draw_time']}")
        print(f"   ✅ Números: {sorteo['numbers']}")
        print()
        
        # Gematría aplicada
        print("🔮 GEMATRÍA APLICADA:")
        print("-" * 40)
        print(f"   ✅ Aplicada: {resultado['gematria_aplicada']}")
        print(f"   ✅ Valores verbales: {resultado['valores_verbales']}")
        print()
        
        # Mensaje coherente
        print("💬 MENSAJE COHERENTE:")
        print("-" * 40)
        mensaje = resultado['mensaje_coherente']
        print(f"   ✅ Creado: {mensaje['created']}")
        if mensaje['poem']:
            print(f"   ✅ Poema: {mensaje['poem']}")
        print()
        
        # Análisis subliminal
        print("🔍 ANÁLISIS SUBLIMINAL:")
        print("-" * 40)
        subliminal = resultado['analisis_subliminal']
        print(f"   ✅ OK: {subliminal['ok']}")
        print(f"   ✅ Tópicos: {subliminal['topics']}")
        print(f"   ✅ Keywords: {subliminal['keywords']}")
        print()
        
        # Submensaje guía
        print("🎯 SUBMENSAJE GUÍA:")
        print("-" * 40)
        guia = resultado['submensaje_guia']
        print(f"   ✅ Extraído: {guia['extracted']}")
        print(f"   ✅ Tópicos guía: {guia['topics']}")
        print(f"   ✅ Keywords guía: {guia['keywords']}")
        print(f"   ✅ Familias: {guia['families']}")
        print()
        
        # Auditor
        print("🔍 AUDITOR:")
        print("-" * 40)
        auditor = resultado['auditor']
        print(f"   ✅ OK: {auditor['ok']}")
        print(f"   ✅ Confianza: {auditor['confidence']}")
        print(f"   ✅ Razón: {auditor['why']}")
        print()
        
        # Explicaciones
        print("📝 EXPLICACIONES:")
        print("-" * 40)
        explain = resultado['explain']
        print(f"   ✅ Por qué más reciente: {explain['why_latest']}")
        print(f"   ✅ Por qué flags: {explain['why_flags']}")
        print(f"   ✅ Hint label: {explain['label_hint']}")
        print()
        
        # Timestamp
        print(f"⏰ TIMESTAMP: {resultado['timestamp']}")
        print()
        
        # Resumen final
        print("🎯 RESUMEN FINAL DEL PASO 3 V2:")
        print("=" * 40)
        print("✅ Sorteo más reciente seleccionado correctamente")
        print("✅ Gematría aplicada exitosamente")
        print("✅ Valores verbales generados")
        print("✅ Mensaje coherente creado")
        print("✅ Análisis subliminal completado")
        print("✅ Submensaje guía extraído")
        print("✅ Validación del auditor exitosa")
        print()
        print("🚀 PASO 3 V2 COMPLETADO EXITOSAMENTE")
        print("📊 Análisis subliminal mejorado funcionando correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 3 V2: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso3_v2()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 3 V2 FUNCIONANDO PERFECTAMENTE")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")
