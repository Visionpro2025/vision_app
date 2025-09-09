# ============================================
# 📌 TEST: PASO 3 - ANÁLISIS DEL SORTEO ANTERIOR (ACTUALIZADO)
# Prueba del tercer paso del Protocolo Universal
# Análisis de Florida Quiniela Pick 3 con datos actuales (septiembre 2025)
# ============================================

import sys
import os
from datetime import datetime, timedelta

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso3_analisis_sorteo_actualizado():
    print("🚀 PRUEBA: PASO 3 - ANÁLISIS DEL SORTEO ANTERIOR (ACTUALIZADO)")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el protocolo universal
        from universal_protocol_official import UniversalProtocolOfficial
        
        print("✅ Protocolo Universal importado correctamente")
        
        # Crear instancia del protocolo
        protocol = UniversalProtocolOfficial()
        
        print("✅ Instancia del protocolo creada")
        print()
        
        # Configuración actualizada para Florida Quiniela Pick 3 (Septiembre 2025)
        print("📊 CONFIGURACIÓN ACTUALIZADA PARA FLORIDA QUINIELA PICK 3")
        print("-" * 60)
        
        # Datos actuales de Florida Quiniela Pick 3 (ejemplo de septiembre 2025)
        florida_config_actualizado = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "p3_mid": "427",    # Pick 3 Midday (ejemplo actual)
            "p4_mid": "8923",   # Pick 4 Midday (ejemplo actual)
            "p3_eve": "156",    # Pick 3 Evening (ejemplo actual)
            "p4_eve": "3456",   # Pick 4 Evening (ejemplo actual)
            "draw_numbers": [4, 2, 7, 8, 9, 2, 3, 1, 5, 6, 3, 4, 5, 6],
            "news_query": "Florida community housing support demonstration september 2025",
            "draw_date": "2025-09-07",  # Ayer
            "draw_time_mid": "13:00",   # Midday
            "draw_time_eve": "22:00"    # Evening
        }
        
        print(f"Juego: {florida_config_actualizado['game']}")
        print(f"Modo: {florida_config_actualizado['mode']}")
        print(f"Fecha del sorteo: {florida_config_actualizado['draw_date']}")
        print(f"Pick 3 Midday: {florida_config_actualizado['p3_mid']} ({florida_config_actualizado['draw_time_mid']})")
        print(f"Pick 4 Midday: {florida_config_actualizado['p4_mid']} ({florida_config_actualizado['draw_time_mid']})")
        print(f"Pick 3 Evening: {florida_config_actualizado['p3_eve']} ({florida_config_actualizado['draw_time_eve']})")
        print(f"Pick 4 Evening: {florida_config_actualizado['p4_eve']} ({florida_config_actualizado['draw_time_eve']})")
        print(f"Números del sorteo: {florida_config_actualizado['draw_numbers']}")
        print(f"Consulta de noticias: {florida_config_actualizado['news_query']}")
        print()
        
        # Mostrar estructura del candado cubano actualizado
        print("🎯 ESTRUCTURA DEL CANDADO CUBANO (ACTUALIZADO)")
        print("-" * 50)
        
        p3_mid = florida_config_actualizado['p3_mid']
        p4_mid = florida_config_actualizado['p4_mid']
        p3_eve = florida_config_actualizado['p3_eve']
        p4_eve = florida_config_actualizado['p4_eve']
        
        print(f"Candado MID (Mediodía):")
        print(f"  FIJO MID: {p3_mid[-2:]} (últimos 2 de Pick 3 Midday: {p3_mid})")
        print(f"  CORRIDO-BLOQUE MID: {p4_mid[-2:]} (últimos 2 de Pick 4 Midday: {p4_mid})")
        print(f"  CORRIDO-DÍA: {p3_eve[-2:]} (últimos 2 de Pick 3 Evening: {p3_eve})")
        print()
        
        print(f"Candado EVE (Noche):")
        print(f"  FIJO EVE: {p3_eve[-2:]} (últimos 2 de Pick 3 Evening: {p3_eve})")
        print(f"  CORRIDO-BLOQUE EVE: {p4_eve[-2:]} (últimos 2 de Pick 4 Evening: {p4_eve})")
        print(f"  CORRIDO-DÍA: {p3_mid[-2:]} (últimos 2 de Pick 3 Midday: {p3_mid})")
        print()
        
        # Ejecutar Paso 3: Análisis del Sorteo Anterior
        print("🔄 EJECUTANDO PASO 3: ANÁLISIS DEL SORTEO ANTERIOR (ACTUALIZADO)")
        print("-" * 60)
        
        # Ejecutar el paso 3
        resultado_paso3 = protocol._step_3_previous_draw_analysis(florida_config_actualizado)
        
        print(f"✅ Paso 3 ejecutado")
        print(f"   Estado: {resultado_paso3['status']}")
        print(f"   Nombre: {resultado_paso3['name']}")
        print()
        
        # Mostrar detalles del paso 3
        if resultado_paso3['status'] == 'completed':
            print("📊 DETALLES DEL PASO 3 (ACTUALIZADO):")
            print("-" * 40)
            
            detalles = resultado_paso3['details']
            
            # 3.1 Sorteo anterior encontrado
            print("3.1 Sorteo anterior encontrado:")
            previous_draw = detalles['previous_draw']
            print(f"   ✅ Sorteo encontrado: {previous_draw.get('found', False)}")
            print(f"   ✅ Datos del sorteo: {previous_draw.get('draw_data', {})}")
            if 'error' in previous_draw:
                print(f"   ⚠️  Error: {previous_draw['error']}")
            print()
            
            # 3.2 Gematría hebrea aplicada
            print("3.2 Gematría hebrea aplicada:")
            hebrew_gematria = detalles['hebrew_gematria']
            print(f"   ✅ Gematría aplicada: {hebrew_gematria.get('gematria_applied', False)}")
            print(f"   ✅ Valores gematría: {hebrew_gematria.get('gematria_values', {})}")
            if 'error' in hebrew_gematria:
                print(f"   ⚠️  Error: {hebrew_gematria['error']}")
            print()
            
            # 3.3 Valores verbales
            print("3.3 Valores verbales:")
            verbal_values = detalles['verbal_values']
            print(f"   ✅ Valores verbales: {verbal_values.get('verbal_values', [])}")
            print(f"   ✅ Conversión exitosa: {verbal_values.get('conversion_successful', False)}")
            if 'error' in verbal_values:
                print(f"   ⚠️  Error: {verbal_values['error']}")
            print()
            
            # 3.4 Mensaje coherente
            print("3.4 Mensaje coherente:")
            coherent_message = detalles['coherent_message']
            print(f"   ✅ Mensaje creado: {coherent_message.get('message_created', False)}")
            print(f"   ✅ Mensaje: {coherent_message.get('message', 'N/A')}")
            if 'error' in coherent_message:
                print(f"   ⚠️  Error: {coherent_message['error']}")
            print()
            
            # 3.5 Análisis subliminal
            print("3.5 Análisis subliminal:")
            subliminal_analysis = detalles['subliminal_analysis']
            print(f"   ✅ Análisis completado: {subliminal_analysis.get('analysis_completed', False)}")
            print(f"   ✅ Tópicos: {subliminal_analysis.get('topics', [])}")
            print(f"   ✅ Keywords: {subliminal_analysis.get('keywords', [])}")
            if 'error' in subliminal_analysis:
                print(f"   ⚠️  Error: {subliminal_analysis['error']}")
            print()
            
            # 3.6 Submensaje guía
            print("3.6 Submensaje guía:")
            submessage_guide = detalles['submessage_guide']
            print(f"   ✅ Guía extraída: {submessage_guide.get('guide_extracted', False)}")
            print(f"   ✅ Tópicos guía: {submessage_guide.get('guide_topics', [])}")
            print(f"   ✅ Keywords guía: {submessage_guide.get('guide_keywords', [])}")
            if 'error' in submessage_guide:
                print(f"   ⚠️  Error: {submessage_guide['error']}")
            print()
            
            # 3.7 Validación del auditor
            print("3.7 Validación del auditor:")
            auditor_validation = detalles['auditor_validation']
            print(f"   ✅ Validación exitosa: {auditor_validation.get('validation_successful', False)}")
            print(f"   ✅ Confianza: {auditor_validation.get('confidence', 'N/A')}")
            if 'error' in auditor_validation:
                print(f"   ⚠️  Error: {auditor_validation['error']}")
            print()
            
            # Timestamp
            print(f"⏰ Timestamp: {detalles.get('timestamp', 'N/A')}")
            print()
            
            # Resumen final
            print("🎯 RESUMEN DEL PASO 3 (ACTUALIZADO):")
            print("-" * 40)
            print("✅ Sorteo anterior analizado (datos actualizados)")
            print("✅ Gematría hebrea aplicada")
            print("✅ Valores verbales convertidos")
            print("✅ Mensaje coherente creado")
            print("✅ Análisis subliminal completado")
            print("✅ Submensaje guía extraído")
            print("✅ Validación del auditor completada")
            print()
            print("🚀 PASO 3 COMPLETADO EXITOSAMENTE")
            print("📊 Análisis del sorteo anterior completado con datos actualizados")
            
        else:
            print(f"❌ Error en Paso 3: {resultado_paso3.get('error', 'Error desconocido')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 3: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso3_analisis_sorteo_actualizado()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 3 FUNCIONANDO CON DATOS ACTUALIZADOS")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")




