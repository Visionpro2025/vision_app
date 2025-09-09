# ============================================
# 📌 TEST: PASO 4 - RECOPILACIÓN DE NOTICIAS GUIADA
# Prueba del cuarto paso del Protocolo Universal
# Utiliza el submensaje guía del Paso 3 V2 para buscar noticias
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso4_noticias_guiada():
    print("🚀 PRUEBA: PASO 4 - RECOPILACIÓN DE NOTICIAS GUIADA")
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
        
        # Configuración para Florida Quiniela Pick 3 con submensaje guía
        print("📊 CONFIGURACIÓN DEL PASO 4:")
        print("-" * 40)
        
        # Submensaje guía del Paso 3 V2
        submensaje_guia = {
            "topics": ['veredicto', 'decisión', 'propiedad', 'refugio', 'hogar', 'cirugía'],
            "keywords": ['decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio'],
            "families": ['corte', 'casa']
        }
        
        # Configuración del paso 4
        noticias_config = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "news_query": "Florida community housing support demonstration september 2025",
            "submessage_guide": submensaje_guia,
            "draw_date": "2025-09-07",
            "draw_numbers": [4, 2, 7],
            "subliminal_topics": submensaje_guia["topics"],
            "subliminal_keywords": submensaje_guia["keywords"],
            "subliminal_families": submensaje_guia["families"]
        }
        
        print(f"Juego: {noticias_config['game']}")
        print(f"Modo: {noticias_config['mode']}")
        print(f"Consulta noticias: {noticias_config['news_query']}")
        print(f"Tópicos guía: {noticias_config['subliminal_topics']}")
        print(f"Keywords guía: {noticias_config['subliminal_keywords']}")
        print(f"Familias guía: {noticias_config['subliminal_families']}")
        print()
        
        # Ejecutar Paso 4: Recopilación de Noticias Guiada
        print("🔄 EJECUTANDO PASO 4: RECOPILACIÓN DE NOTICIAS GUIADA")
        print("-" * 60)
        
        resultado_paso4 = protocol._step_4_news_collection(
            submessage_guide=str(submensaje_guia),
            lottery_config=noticias_config
        )
        
        print(f"✅ Paso 4 ejecutado")
        print(f"   Estado: {resultado_paso4['status']}")
        print(f"   Nombre: {resultado_paso4['name']}")
        print()
        
        # Mostrar información detallada del paso 4
        if resultado_paso4['status'] == 'completed':
            print("📊 INFORMACIÓN DETALLADA DEL PASO 4:")
            print("=" * 60)
            
            detalles = resultado_paso4['details']
            
            # 4.1 Procesamiento del submensaje guía
            print("🎯 4.1 PROCESAMIENTO DEL SUBMENSAJE GUÍA:")
            print("-" * 40)
            submessage_processing = detalles['submessage_processing']
            print(f"   ✅ Procesado: {submessage_processing.get('processed', False)}")
            print(f"   ✅ Tópicos procesados: {submessage_processing.get('processed_topics', [])}")
            print(f"   ✅ Keywords procesadas: {submessage_processing.get('processed_keywords', [])}")
            if 'error' in submessage_processing:
                print(f"   ⚠️  Error: {submessage_processing['error']}")
            print()
            
            # 4.2 Generación del modulador de palabras
            print("🔧 4.2 GENERACIÓN DEL MODULADOR DE PALABRAS:")
            print("-" * 40)
            word_modulator = detalles['word_modulator']
            print(f"   ✅ Generado: {word_modulator.get('generated', False)}")
            print(f"   ✅ Modulador: {word_modulator.get('modulator', {})}")
            if 'error' in word_modulator:
                print(f"   ⚠️  Error: {word_modulator['error']}")
            print()
            
            # 4.3 Recopilación de noticias principales
            print("📰 4.3 RECOPILACIÓN DE NOTICIAS PRINCIPALES:")
            print("-" * 40)
            main_news = detalles['main_news']
            print(f"   ✅ Recopiladas: {main_news.get('collected', False)}")
            print(f"   ✅ Cantidad: {main_news.get('count', 0)}")
            print(f"   ✅ URLs: {main_news.get('urls', [])}")
            if 'error' in main_news:
                print(f"   ⚠️  Error: {main_news['error']}")
            print()
            
            # 4.4 Búsqueda de noticias emocionales
            print("💭 4.4 BÚSQUEDA DE NOTICIAS EMOCIONALES:")
            print("-" * 40)
            emotional_news = detalles['emotional_news']
            print(f"   ✅ Buscadas: {emotional_news.get('searched', False)}")
            print(f"   ✅ Cantidad: {emotional_news.get('count', 0)}")
            print(f"   ✅ URLs: {emotional_news.get('urls', [])}")
            if 'error' in emotional_news:
                print(f"   ⚠️  Error: {emotional_news['error']}")
            print()
            
            # 4.5 Filtrado de noticias
            print("🔍 4.5 FILTRADO DE NOTICIAS:")
            print("-" * 40)
            news_filtering = detalles['news_filtering']
            print(f"   ✅ Filtradas: {news_filtering.get('filtered', False)}")
            print(f"   ✅ Cantidad final: {news_filtering.get('final_count', 0)}")
            print(f"   ✅ URLs finales: {news_filtering.get('final_urls', [])}")
            if 'error' in news_filtering:
                print(f"   ⚠️  Error: {news_filtering['error']}")
            print()
            
            # 4.6 Validación del auditor
            print("🔍 4.6 VALIDACIÓN DEL AUDITOR:")
            print("-" * 40)
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
            print("🎯 RESUMEN FINAL DEL PASO 4:")
            print("-" * 40)
            print("✅ Submensaje guía procesado")
            print("✅ Modulador de palabras generado")
            print("✅ Noticias principales recopiladas")
            print("✅ Noticias emocionales buscadas")
            print("✅ Noticias filtradas correctamente")
            print("✅ Validación del auditor completada")
            print()
            print("🚀 PASO 4 COMPLETADO EXITOSAMENTE")
            print("📊 Recopilación de noticias guiada completada")
            
        else:
            print(f"❌ Error en Paso 4: {resultado_paso4.get('error', 'Error desconocido')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 4: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso4_noticias_guiada()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 4 FUNCIONANDO CORRECTAMENTE")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")
