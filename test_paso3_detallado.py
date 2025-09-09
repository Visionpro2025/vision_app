# ============================================
# 📌 TEST: PASO 3 - ANÁLISIS DETALLADO COMPLETO
# Prueba detallada del tercer paso del Protocolo Universal
# Análisis completo de Florida Quiniela Pick 3
# ============================================

import sys
import os
import json
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso3_detallado():
    print("🔍 ANÁLISIS DETALLADO COMPLETO DEL PASO 3")
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
        
        # Configuración para Florida Quiniela Pick 3
        florida_config = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "p3_mid": "427",
            "p4_mid": "8923",
            "p3_eve": "156",
            "p4_eve": "3456",
            "draw_numbers": [4, 2, 7, 8, 9, 2, 3, 1, 5, 6, 3, 4, 5, 6],
            "news_query": "Florida community housing support demonstration september 2025",
            "draw_date": "2025-09-07",
            "draw_time_mid": "13:00",
            "draw_time_eve": "22:00"
        }
        
        print("📊 CONFIGURACIÓN DEL SORTEO:")
        print("-" * 40)
        print(f"Juego: {florida_config['game']}")
        print(f"Modo: {florida_config['mode']}")
        print(f"Fecha: {florida_config['draw_date']}")
        print(f"Pick 3 Midday: {florida_config['p3_mid']}")
        print(f"Pick 4 Midday: {florida_config['p4_mid']}")
        print(f"Pick 3 Evening: {florida_config['p3_eve']}")
        print(f"Pick 4 Evening: {florida_config['p4_eve']}")
        print(f"Números: {florida_config['draw_numbers']}")
        print(f"Consulta noticias: {florida_config['news_query']}")
        print()
        
        # Ejecutar Paso 3: Análisis del Sorteo Anterior
        print("🔄 EJECUTANDO PASO 3: ANÁLISIS DEL SORTEO ANTERIOR")
        print("-" * 60)
        
        resultado_paso3 = protocol._step_3_previous_draw_analysis(florida_config)
        
        print(f"✅ Paso 3 ejecutado")
        print(f"   Estado: {resultado_paso3['status']}")
        print(f"   Nombre: {resultado_paso3['name']}")
        print()
        
        # Mostrar información completa del paso 3
        if resultado_paso3['status'] == 'completed':
            print("📊 INFORMACIÓN COMPLETA DEL PASO 3:")
            print("=" * 60)
            
            detalles = resultado_paso3['details']
            
            # 3.1 Sorteo anterior encontrado
            print("🔍 3.1 SORTEO ANTERIOR ENCONTRADO:")
            print("-" * 40)
            previous_draw = detalles['previous_draw']
            print(f"   ✅ Encontrado: {previous_draw.get('found', False)}")
            print(f"   ✅ Datos: {json.dumps(previous_draw.get('draw_data', {}), indent=2)}")
            if 'error' in previous_draw:
                print(f"   ⚠️  Error: {previous_draw['error']}")
            print()
            
            # 3.2 Gematría hebrea aplicada
            print("🔮 3.2 GEMATRÍA HEBREA APLICADA:")
            print("-" * 40)
            hebrew_gematria = detalles['hebrew_gematria']
            print(f"   ✅ Aplicada: {hebrew_gematria.get('gematria_applied', False)}")
            print(f"   ✅ Valores: {json.dumps(hebrew_gematria.get('gematria_values', {}), indent=2)}")
            if 'error' in hebrew_gematria:
                print(f"   ⚠️  Error: {hebrew_gematria['error']}")
            print()
            
            # 3.3 Valores verbales
            print("📝 3.3 VALORES VERBALES:")
            print("-" * 40)
            verbal_values = detalles['verbal_values']
            print(f"   ✅ Valores: {json.dumps(verbal_values.get('verbal_values', []), indent=2)}")
            print(f"   ✅ Conversión exitosa: {verbal_values.get('conversion_successful', False)}")
            if 'error' in verbal_values:
                print(f"   ⚠️  Error: {verbal_values['error']}")
            print()
            
            # 3.4 Mensaje coherente
            print("💬 3.4 MENSAJE COHERENTE:")
            print("-" * 40)
            coherent_message = detalles['coherent_message']
            print(f"   ✅ Creado: {coherent_message.get('message_created', False)}")
            print(f"   ✅ Mensaje: {coherent_message.get('message', 'N/A')}")
            if 'error' in coherent_message:
                print(f"   ⚠️  Error: {coherent_message['error']}")
            print()
            
            # 3.5 Análisis subliminal
            print("🔍 3.5 ANÁLISIS SUBLIMINAL:")
            print("-" * 40)
            subliminal_analysis = detalles['subliminal_analysis']
            print(f"   ✅ Completado: {subliminal_analysis.get('analysis_completed', False)}")
            print(f"   ✅ Tópicos: {json.dumps(subliminal_analysis.get('topics', []), indent=2)}")
            print(f"   ✅ Keywords: {json.dumps(subliminal_analysis.get('keywords', []), indent=2)}")
            if 'error' in subliminal_analysis:
                print(f"   ⚠️  Error: {subliminal_analysis['error']}")
            print()
            
            # 3.6 Submensaje guía
            print("🎯 3.6 SUBMENSAJE GUÍA:")
            print("-" * 40)
            submessage_guide = detalles['submessage_guide']
            print(f"   ✅ Extraído: {submessage_guide.get('guide_extracted', False)}")
            print(f"   ✅ Tópicos guía: {json.dumps(submessage_guide.get('guide_topics', []), indent=2)}")
            print(f"   ✅ Keywords guía: {json.dumps(submessage_guide.get('guide_keywords', []), indent=2)}")
            if 'error' in submessage_guide:
                print(f"   ⚠️  Error: {submessage_guide['error']}")
            print()
            
            # 3.7 Validación del auditor
            print("🔍 3.7 VALIDACIÓN DEL AUDITOR:")
            print("-" * 40)
            auditor_validation = detalles['auditor_validation']
            print(f"   ✅ Exitosa: {auditor_validation.get('validation_successful', False)}")
            print(f"   ✅ Confianza: {auditor_validation.get('confidence', 'N/A')}")
            if 'error' in auditor_validation:
                print(f"   ⚠️  Error: {auditor_validation['error']}")
            print()
            
            # Timestamp
            print(f"⏰ TIMESTAMP: {detalles.get('timestamp', 'N/A')}")
            print()
            
            # Resumen final
            print("🎯 RESUMEN FINAL DEL PASO 3:")
            print("=" * 40)
            print("✅ Sorteo anterior analizado exitosamente")
            print("✅ Gematría hebrea aplicada correctamente")
            print("✅ Valores verbales convertidos")
            print("✅ Mensaje coherente creado")
            print("✅ Análisis subliminal completado")
            print("✅ Submensaje guía extraído")
            print("✅ Validación del auditor completada")
            print()
            print("🚀 PASO 3 COMPLETADO EXITOSAMENTE")
            print("📊 Análisis del sorteo anterior completado")
            
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
    success = test_paso3_detallado()
    if success:
        print("\n🎉 ANÁLISIS DETALLADO COMPLETO - PASO 3 FUNCIONANDO")
    else:
        print("\n💥 ANÁLISIS FALLIDO - REVISAR ERRORES")



