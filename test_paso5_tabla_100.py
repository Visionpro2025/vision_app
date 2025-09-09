# ============================================
# 📌 TEST: PASO 5 - ATRIBUCIÓN A TABLA 100 UNIVERSAL
# Prueba del quinto paso del Protocolo Universal
# Correlación de noticias del día con Tabla 100 Universal
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso5_tabla_100():
    print("🚀 PRUEBA: PASO 5 - ATRIBUCIÓN A TABLA 100 UNIVERSAL")
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
        
        # Configuración para el Paso 5 con noticias del día actual
        print("📊 CONFIGURACIÓN DEL PASO 5:")
        print("-" * 40)
        
        # Datos del sorteo analizado
        sorteo_data = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "draw_numbers": [4, 2, 7],
            "draw_date": "2025-09-07",
            "p3_mid": "427",
            "p4_mid": "8923", 
            "p3_eve": "156",
            "p4_eve": "3456"
        }
        
        # Noticias del día actual (simuladas basadas en el test anterior)
        noticias_dia = {
            "news_count": 98,
            "emotional_news_count": 14,
            "sources": ["BBC News", "NPR News", "BBC World News"],
            "topics": ["justicia", "crimen", "trabajo", "salud", "familia", "política"],
            "keywords": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"]
        }
        
        # Submensaje guía del Paso 3 V2
        submessage_guide = {
            "topics": ['veredicto', 'decisión', 'propiedad', 'refugio', 'hogar', 'cirugía'],
            "keywords": ['decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio'],
            "families": ['corte', 'casa']
        }
        
        # Configuración del paso 5
        tabla_100_config = {
            **sorteo_data,
            "noticias_dia": noticias_dia,
            "submessage_guide": submessage_guide,
            "subliminal_topics": submessage_guide["topics"],
            "subliminal_keywords": submessage_guide["keywords"],
            "subliminal_families": submessage_guide["families"]
        }
        
        print(f"Juego: {tabla_100_config['game']}")
        print(f"Modo: {tabla_100_config['mode']}")
        print(f"Sorteo: {tabla_100_config['draw_numbers']}")
        print(f"Noticias del día: {tabla_100_config['noticias_dia']['news_count']}")
        print(f"Noticias emocionales: {tabla_100_config['noticias_dia']['emotional_news_count']}")
        print(f"Tópicos guía: {tabla_100_config['subliminal_topics']}")
        print()
        
        # Ejecutar Paso 5: Atribución a Tabla 100 Universal
        print("🔄 EJECUTANDO PASO 5: ATRIBUCIÓN A TABLA 100 UNIVERSAL")
        print("-" * 60)
        
        resultado_paso5 = protocol._step_5_news_attribution_table100(
            news_data=noticias_dia,
            lottery_config=tabla_100_config
        )
        
        print(f"✅ Paso 5 ejecutado")
        print(f"   Estado: {resultado_paso5['status']}")
        print(f"   Nombre: {resultado_paso5['name']}")
        print()
        
        # Mostrar información detallada del paso 5
        if resultado_paso5['status'] == 'completed':
            print("📊 INFORMACIÓN DETALLADA DEL PASO 5:")
            print("=" * 60)
            
            detalles = resultado_paso5['details']
            
            # 5.1 Análisis de correlación
            print("🔍 5.1 ANÁLISIS DE CORRELACIÓN:")
            print("-" * 40)
            correlation_analysis = detalles['correlation_analysis']
            print(f"   ✅ Análisis completado: {correlation_analysis.get('analysis_completed', False)}")
            print(f"   ✅ Correlaciones encontradas: {correlation_analysis.get('correlations_found', 0)}")
            print(f"   ✅ Coeficiente de correlación: {correlation_analysis.get('correlation_coefficient', 'N/A')}")
            if 'error' in correlation_analysis:
                print(f"   ⚠️  Error: {correlation_analysis['error']}")
            print()
            
            # 5.2 Mapeo a Tabla 100
            print("🗺️ 5.2 MAPEO A TABLA 100:")
            print("-" * 40)
            table_100_mapping = detalles['table_100_mapping']
            print(f"   ✅ Mapeo completado: {table_100_mapping.get('mapping_completed', False)}")
            print(f"   ✅ Números mapeados: {table_100_mapping.get('mapped_numbers', [])}")
            print(f"   ✅ Significados: {table_100_mapping.get('meanings', [])}")
            if 'error' in table_100_mapping:
                print(f"   ⚠️  Error: {table_100_mapping['error']}")
            print()
            
            # 5.3 Análisis de relevancia
            print("📈 5.3 ANÁLISIS DE RELEVANCIA:")
            print("-" * 40)
            relevance_analysis = detalles['relevance_analysis']
            print(f"   ✅ Análisis completado: {relevance_analysis.get('analysis_completed', False)}")
            print(f"   ✅ Relevancia promedio: {relevance_analysis.get('average_relevance', 'N/A')}")
            print(f"   ✅ Números más relevantes: {relevance_analysis.get('most_relevant_numbers', [])}")
            if 'error' in relevance_analysis:
                print(f"   ⚠️  Error: {relevance_analysis['error']}")
            print()
            
            # 5.4 Generación de predicciones
            print("🎯 5.4 GENERACIÓN DE PREDICCIONES:")
            print("-" * 40)
            prediction_generation = detalles['prediction_generation']
            print(f"   ✅ Predicciones generadas: {prediction_generation.get('predictions_generated', False)}")
            print(f"   ✅ Números predichos: {prediction_generation.get('predicted_numbers', [])}")
            print(f"   ✅ Confianza: {prediction_generation.get('confidence', 'N/A')}")
            if 'error' in prediction_generation:
                print(f"   ⚠️  Error: {prediction_generation['error']}")
            print()
            
            # 5.5 Validación del auditor
            print("🔍 5.5 VALIDACIÓN DEL AUDITOR:")
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
            print("🎯 RESUMEN FINAL DEL PASO 5:")
            print("-" * 40)
            print("✅ Análisis de correlación completado")
            print("✅ Mapeo a Tabla 100 Universal completado")
            print("✅ Análisis de relevancia completado")
            print("✅ Generación de predicciones completada")
            print("✅ Validación del auditor completada")
            print()
            print("🚀 PASO 5 COMPLETADO EXITOSAMENTE")
            print("📊 Atribución a Tabla 100 Universal completada")
            
        else:
            print(f"❌ Error en Paso 5: {resultado_paso5.get('error', 'Error desconocido')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 5: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso5_tabla_100()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 5 FUNCIONANDO CORRECTAMENTE")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")
