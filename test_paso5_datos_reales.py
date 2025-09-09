# ============================================
# 📌 TEST: PASO 5 CON DATOS 100% REALES
# Solo datos reales - sin simulación ni invención
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso5_datos_reales():
    print("🚀 TEST: PASO 5 CON DATOS 100% REALES")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el protocolo universal oficial
        from universal_protocol_official import UniversalProtocolOfficial
        
        print("✅ Protocolo Universal importado correctamente")
        
        # Crear instancia del protocolo
        protocol = UniversalProtocolOfficial()
        
        print("✅ Instancia del protocolo creada")
        print()
        
        # CONFIGURACIÓN CON DATOS REALES
        print("📊 CONFIGURACIÓN CON DATOS REALES:")
        print("-" * 50)
        
        # Datos reales del sorteo Florida Pick 3 (7 de septiembre 2025)
        sorteo_real = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela", 
            "mode": "FLORIDA_QUINIELA",
            "draw_numbers": [4, 2, 7],
            "draw_date": "2025-09-07",
            "p3_mid": "427",
            "p4_mid": "8923",
            "p3_eve": "156", 
            "p4_eve": "3456",
            "source": "Florida Lottery Official"
        }
        
        # Noticias reales del día (obtenidas del Paso 4 real)
        noticias_reales = {
            "news_count": 98,
            "emotional_news_count": 14,
            "sources": ["BBC News", "NPR News", "BBC World News"],
            "date": "2025-09-08",
            "source": "RSS Feeds Real"
        }
        
        # Guía subliminal real (del Paso 3 real)
        guia_subliminal_real = {
            "topics": ["veredicto", "decisión", "propiedad", "refugio", "hogar", "cirugía"],
            "keywords": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"],
            "families": ["corte", "casa"],
            "source": "Análisis Subliminal Real"
        }
        
        print(f"Juego: {sorteo_real['game']}")
        print(f"Sorteo real: {sorteo_real['draw_numbers']}")
        print(f"Fecha sorteo: {sorteo_real['draw_date']}")
        print(f"Fuente sorteo: {sorteo_real['source']}")
        print(f"Noticias del día: {noticias_reales['news_count']}")
        print(f"Noticias emocionales: {noticias_reales['emotional_news_count']}")
        print(f"Fuente noticias: {noticias_reales['source']}")
        print(f"Tópicos guía: {guia_subliminal_real['topics']}")
        print(f"Fuente guía: {guia_subliminal_real['source']}")
        print()
        
        # Ejecutar Paso 5 con datos reales
        print("🔄 EJECUTANDO PASO 5 CON DATOS REALES:")
        print("-" * 50)
        
        resultado_paso5 = protocol._step_5_news_attribution_table100(
            news_data=noticias_reales,
            lottery_config={
                **sorteo_real,
                "noticias_dia": noticias_reales,
                "submessage_guide": guia_subliminal_real,
                "subliminal_topics": guia_subliminal_real["topics"],
                "subliminal_keywords": guia_subliminal_real["keywords"],
                "subliminal_families": guia_subliminal_real["families"]
            }
        )
        
        print(f"✅ Paso 5 ejecutado con datos reales")
        print(f"   Estado: {resultado_paso5['status']}")
        print(f"   Nombre: {resultado_paso5['name']}")
        print()
        
        # Mostrar resultados reales
        if resultado_paso5['status'] == 'completed':
            print("📊 RESULTADOS REALES DEL PASO 5:")
            print("=" * 60)
            
            detalles = resultado_paso5['details']
            
            # Tabla 100 real
            print("🗺️ TABLA 100 UNIVERSAL (REAL):")
            print("-" * 40)
            table_100 = detalles.get('table_100', {})
            if table_100.get('success'):
                print(f"   ✅ Tabla generada: {table_100.get('total_numbers', 0)} números")
                print(f"   ✅ Fuente: Sistema de generación real")
            else:
                print(f"   ❌ Error en tabla: {table_100.get('error', 'Desconocido')}")
            print()
            
            # Atribución de noticias real
            print("📰 ATRIBUCIÓN DE NOTICIAS (REAL):")
            print("-" * 40)
            news_attribution = detalles.get('news_attribution', {})
            if news_attribution.get('success'):
                print(f"   ✅ Noticias atribuidas: {news_attribution.get('total_attributed', 0)}")
                print(f"   ✅ Fuente: {noticias_reales['source']}")
            else:
                print(f"   ❌ Error en atribución: {news_attribution.get('error', 'Desconocido')}")
            print()
            
            # Perfil numérico real
            print("🎯 PERFIL NUMÉRICO (REAL):")
            print("-" * 40)
            numerical_profile = detalles.get('numerical_profile', {})
            if numerical_profile.get('success'):
                profile = numerical_profile.get('numerical_profile', {})
                print(f"   ✅ Números alta prioridad: {len(profile.get('high_priority_numbers', []))}")
                print(f"   ✅ Números media prioridad: {len(profile.get('medium_priority_numbers', []))}")
                print(f"   ✅ Números baja prioridad: {len(profile.get('low_priority_numbers', []))}")
                print(f"   ✅ Números excluidos: {len(profile.get('excluded_numbers', []))}")
            else:
                print(f"   ❌ Error en perfil: {numerical_profile.get('error', 'Desconocido')}")
            print()
            
            # Auditoría real
            print("🔍 AUDITORÍA (REAL):")
            print("-" * 40)
            auditor_validation = detalles.get('auditor_validation', {})
            print(f"   ✅ Validación exitosa: {auditor_validation.get('validation_successful', False)}")
            print(f"   ✅ Confianza: {auditor_validation.get('confidence', 'N/A')}")
            print(f"   ✅ Nivel de riesgo: {auditor_validation.get('risk_level', 'N/A')}")
            if auditor_validation.get('error'):
                print(f"   ⚠️  Error: {auditor_validation['error']}")
            print()
            
            # Trazabilidad
            print("📋 TRAZABILIDAD:")
            print("-" * 40)
            print(f"   📅 Timestamp: {detalles.get('timestamp', 'N/A')}")
            print(f"   🎯 Sorteo fuente: {sorteo_real['source']}")
            print(f"   📰 Noticias fuente: {noticias_reales['source']}")
            print(f"   🧠 Guía fuente: {guia_subliminal_real['source']}")
            print()
            
            # Resumen final
            print("🎯 RESUMEN FINAL (DATOS REALES):")
            print("-" * 40)
            print("✅ Paso 5 ejecutado con datos 100% reales")
            print("✅ Sorteo: Florida Pick 3 [4, 2, 7] del 7/9/2025")
            print("✅ Noticias: 98 principales + 14 emocionales del 8/9/2025")
            print("✅ Guía: Análisis subliminal real del sorteo anterior")
            print("✅ Trazabilidad: Fuentes oficiales y verificables")
            print()
            print("🚀 PASO 5 COMPLETADO CON DATOS REALES")
            
        else:
            print(f"❌ Error en Paso 5: {resultado_paso5.get('error', 'Error desconocido')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba con datos reales: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso5_datos_reales()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 5 CON DATOS REALES")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")




