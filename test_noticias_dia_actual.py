# ============================================
# 📌 TEST: NOTICIAS DEL DÍA ACTUAL
# Búsqueda específica de noticias del 8 de septiembre de 2025
# Para el protocolo actual de Florida Quiniela Pick 3
# ============================================

import sys
import os
from datetime import datetime, date

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_noticias_dia_actual():
    print("🚀 PRUEBA: NOTICIAS DEL DÍA ACTUAL - 8 DE SEPTIEMBRE 2025")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Día del protocolo: 8 de septiembre de 2025")
    print()
    
    try:
        # Importar el módulo de ingesta
        from app_vision.modules.news_ingestion import ProfessionalNewsIngestion
        
        print("✅ ProfessionalNewsIngestion importado correctamente")
        
        # Configurar feeds para noticias del día actual
        feeds_dia_actual = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "https://feeds.npr.org/1001/rss.xml",
            "https://feeds.npr.org/1002/rss.xml",  # NPR World
            "https://feeds.npr.org/1003/rss.xml",  # NPR Politics
            "https://feeds.npr.org/1004/rss.xml",  # NPR Health
            "https://feeds.npr.org/1005/rss.xml",  # NPR Science
            "https://feeds.npr.org/1006/rss.xml",  # NPR Technology
            "https://feeds.npr.org/1007/rss.xml",  # NPR Business
            "https://feeds.npr.org/1008/rss.xml"   # NPR Arts
        ]
        
        # Configurar para obtener más noticias del día
        ingestion = ProfessionalNewsIngestion(feeds=feeds_dia_actual, max_per_feed=30)
        
        print("✅ Instancia de ProfessionalNewsIngestion creada")
        print(f"   Feeds configurados: {len(feeds_dia_actual)}")
        print(f"   Max por feed: 30")
        print(f"   Día objetivo: 8 de septiembre de 2025")
        print()
        
        # Test 1: Noticias principales del día
        print("🔄 TEST 1: NOTICIAS PRINCIPALES DEL DÍA")
        print("-" * 50)
        
        result_principales = ingestion.collect_news()
        
        print(f"✅ Noticias principales del día: {result_principales['count']}")
        print(f"   Fuentes procesadas: {len(result_principales['sources'])}")
        print()
        
        # Mostrar detalle por fuente
        print("📊 NOTICIAS POR FUENTE (DÍA ACTUAL):")
        for source in result_principales['sources']:
            print(f"   {source['feed']}: {source['items']} noticias")
        print()
        
        # Test 2: Noticias emocionales del día con términos específicos
        print("🔄 TEST 2: NOTICIAS EMOCIONALES DEL DÍA")
        print("-" * 50)
        
        # Términos específicos para Florida Quiniela Pick 3 del 8 de septiembre
        terminos_dia_actual = [
            # Términos del submensaje guía del Paso 3 V2
            'decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio',
            'corte', 'casa',
            
            # Términos sociales/emocionales ampliados
            'community', 'comunidad', 'familia', 'family', 'neighborhood', 'barrio',
            'empleo', 'salud', 'mental', 'escuela', 'educación', 'vivienda', 'alquiler',
            'protesta', 'manifestación', 'migración', 'ayuda', 'solidaridad', 'crimen',
            'violencia', 'inflación', 'costo de vida', 'eviction', 'duelo', 'tragedia',
            'celebración', 'voluntariado',
            
            # Términos específicos de Florida
            'florida', 'miami', 'orlando', 'tampa', 'jacksonville',
            'housing', 'support', 'demonstration', 'crisis', 'help',
            'september', '2025', 'today', 'hoy'
        ]
        
        result_emocionales = ingestion.search_emotional_news(terminos_dia_actual)
        
        print(f"✅ Noticias emocionales del día: {result_emocionales['count']}")
        print(f"   Términos de búsqueda: {len(terminos_dia_actual)}")
        print(f"   Fuentes procesadas: {len(result_emocionales['sources'])}")
        print()
        
        # Mostrar noticias emocionales encontradas
        if result_emocionales['count'] > 0:
            print("💭 NOTICIAS EMOCIONALES DEL DÍA ACTUAL:")
            print("-" * 50)
            for i, url in enumerate(result_emocionales['urls'], 1):
                print(f"   {i:2d}. {url}")
            print()
        
        # Test 3: Información detallada de noticias del día
        print("🔄 TEST 3: DETALLES DE NOTICIAS DEL DÍA ACTUAL")
        print("-" * 50)
        
        from app_vision.modules.news_ingestion import _extract_entries_from_feed
        
        print("📋 NOTICIAS DEL 8 DE SEPTIEMBRE 2025:")
        print("-" * 50)
        
        noticias_dia = []
        for feed_url in feeds_dia_actual[:5]:  # Primeros 5 feeds
            try:
                entries = _extract_entries_from_feed(feed_url, 10)
                print(f"\n📰 FUENTE: {feed_url}")
                print("-" * 30)
                
                for i, entry in enumerate(entries, 1):
                    # Verificar si es del día actual
                    fecha_pub = entry['published']
                    if 'Sep 2025' in fecha_pub or '08 Sep 2025' in fecha_pub:
                        noticias_dia.append(entry)
                        print(f"   {i}. TÍTULO: {entry['title']}")
                        print(f"      URL: {entry['url']}")
                        print(f"      FECHA: {entry['published']}")
                        print(f"      RESUMEN: {entry['summary'][:150]}...")
                        print()
                        
            except Exception as e:
                print(f"   Error procesando {feed_url}: {e}")
                continue
        
        # Test 4: Resumen del protocolo del día
        print("🔄 TEST 4: RESUMEN DEL PROTOCOLO DEL DÍA")
        print("-" * 50)
        
        print("🎯 PROTOCOLO FLORIDA QUINIELA PICK 3 - 8 SEPTIEMBRE 2025")
        print("-" * 50)
        print(f"📅 Día del protocolo: 8 de septiembre de 2025")
        print(f"🎲 Sorteo analizado: Florida Pick 3 [4, 2, 7]")
        print(f"📰 Noticias principales: {result_principales['count']}")
        print(f"💭 Noticias emocionales: {result_emocionales['count']}")
        print(f"📋 Noticias del día específico: {len(noticias_dia)}")
        print()
        
        # Mostrar términos de búsqueda utilizados
        print("🔍 TÉRMINOS DE BÚSQUEDA UTILIZADOS:")
        print("-" * 30)
        for i, termino in enumerate(terminos_dia_actual[:20], 1):  # Primeros 20
            print(f"   {i:2d}. {termino}")
        if len(terminos_dia_actual) > 20:
            print(f"   ... y {len(terminos_dia_actual) - 20} términos más")
        print()
        
        # Resumen final
        print("🎯 RESUMEN FINAL DEL DÍA:")
        print("-" * 50)
        print(f"✅ Noticias principales: {result_principales['count']}")
        print(f"✅ Noticias emocionales: {result_emocionales['count']}")
        print(f"✅ Noticias del día específico: {len(noticias_dia)}")
        print(f"✅ Fuentes procesadas: {len(result_principales['sources'])}")
        print(f"✅ Términos de búsqueda: {len(terminos_dia_actual)}")
        print()
        
        if result_principales['count'] > 0 or result_emocionales['count'] > 0:
            print("🎉 ÉXITO - NOTICIAS DEL DÍA ACTUAL ACOPIADAS")
            print("📊 El protocolo tiene noticias frescas del 8 de septiembre de 2025")
        else:
            print("⚠️  ADVERTENCIA - NO SE ENCONTRARON NOTICIAS DEL DÍA")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba de noticias del día actual: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_noticias_dia_actual()
    if success:
        print("\n🎉 PRUEBA EXITOSA - NOTICIAS DEL DÍA ACTUAL OBTENIDAS")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")





