# ============================================
# 📌 TEST: NOTICIAS COMPLETAS CON FUENTE Y FECHA
# Prueba mejorada para obtener más noticias con información detallada
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_noticias_completas():
    print("🚀 PRUEBA: NOTICIAS COMPLETAS CON FUENTE Y FECHA")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el módulo de ingesta
        from app_vision.modules.news_ingestion import ProfessionalNewsIngestion
        
        print("✅ ProfessionalNewsIngestion importado correctamente")
        
        # Configurar más feeds para obtener más noticias
        feeds = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss", 
            "https://www.reuters.com/world/us/rss",
            "https://feeds.npr.org/1001/rss.xml",
            "https://rss.cnn.com/rss/edition_world.rss",
            "https://feeds.bbci.co.uk/news/world/rss.xml"
        ]
        
        # Aumentar el número de noticias por feed
        ingestion = ProfessionalNewsIngestion(feeds=feeds, max_per_feed=25)
        
        print("✅ Instancia de ProfessionalNewsIngestion creada")
        print(f"   Feeds configurados: {len(feeds)}")
        print(f"   Max por feed: 25")
        print()
        
        # Test 1: collect_news() con más feeds
        print("🔄 TEST 1: collect_news() - MÁS FEEDS")
        print("-" * 50)
        
        result_collect = ingestion.collect_news()
        
        print(f"✅ collect_news() ejecutado")
        print(f"   URLs encontradas: {result_collect['count']}")
        print(f"   Fuentes procesadas: {len(result_collect['sources'])}")
        print()
        
        # Mostrar detalle por fuente
        print("📊 DETALLE POR FUENTE:")
        for source in result_collect['sources']:
            print(f"   {source['feed']}: {source['items']} noticias")
        print()
        
        # Mostrar más noticias con información detallada
        if result_collect['count'] > 0:
            print("📰 NOTICIAS ENCONTRADAS (PRIMERAS 15):")
            print("-" * 50)
            for i, url in enumerate(result_collect['urls'][:15], 1):
                print(f"   {i:2d}. {url}")
            print()
        
        # Test 2: search_emotional_news() con términos más amplios
        print("🔄 TEST 2: search_emotional_news() - TÉRMINOS AMPLIADOS")
        print("-" * 50)
        
        # Términos más amplios para capturar más noticias emocionales
        guidance_terms = [
            'decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio',
            'community', 'comunidad', 'familia', 'family', 'neighborhood', 'barrio',
            'empleo', 'salud', 'mental', 'escuela', 'educación', 'vivienda', 'alquiler',
            'protesta', 'manifestación', 'migración', 'ayuda', 'solidaridad', 'crimen',
            'violencia', 'inflación', 'costo de vida', 'eviction', 'duelo', 'tragedia',
            'celebración', 'voluntariado', 'housing', 'support', 'demonstration',
            'crisis', 'help', 'community', 'family', 'housing', 'support'
        ]
        
        result_emotional = ingestion.search_emotional_news(guidance_terms)
        
        print(f"✅ search_emotional_news() ejecutado")
        print(f"   Términos guía: {len(guidance_terms)} términos")
        print(f"   URLs emocionales: {result_emotional['count']}")
        print(f"   Fuentes procesadas: {len(result_emotional['sources'])}")
        print()
        
        if result_emotional['count'] > 0:
            print("💭 NOTICIAS EMOCIONALES ENCONTRADAS:")
            print("-" * 50)
            for i, url in enumerate(result_emotional['urls'], 1):
                print(f"   {i:2d}. {url}")
            print()
        
        # Test 3: Obtener información detallada de las noticias
        print("🔄 TEST 3: INFORMACIÓN DETALLADA DE NOTICIAS")
        print("-" * 50)
        
        # Crear una instancia para obtener detalles
        from app_vision.modules.news_ingestion import _extract_entries_from_feed
        
        print("📋 DETALLES DE NOTICIAS (PRIMERAS 10):")
        print("-" * 50)
        
        for feed_url in feeds[:3]:  # Solo los primeros 3 feeds para no sobrecargar
            try:
                entries = _extract_entries_from_feed(feed_url, 5)
                print(f"\n📰 FUENTE: {feed_url}")
                print("-" * 30)
                
                for i, entry in enumerate(entries, 1):
                    print(f"   {i}. TÍTULO: {entry['title']}")
                    print(f"      URL: {entry['url']}")
                    print(f"      FECHA: {entry['published']}")
                    print(f"      RESUMEN: {entry['summary'][:100]}...")
                    print()
                    
            except Exception as e:
                print(f"   Error procesando {feed_url}: {e}")
                continue
        
        # Resumen final
        print("🎯 RESUMEN FINAL:")
        print("-" * 50)
        print(f"✅ Noticias principales: {result_collect['count']}")
        print(f"✅ Noticias emocionales: {result_emotional['count']}")
        print(f"✅ Fuentes procesadas: {len(result_collect['sources'])}")
        print(f"✅ Feeds configurados: {len(feeds)}")
        print()
        
        if result_collect['count'] > 0:
            print("🎉 ÉXITO - NOTICIAS ACOPIADAS CON INFORMACIÓN COMPLETA")
        else:
            print("⚠️  ADVERTENCIA - NO SE ENCONTRARON NOTICIAS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba de noticias completas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_noticias_completas()
    if success:
        print("\n🎉 PRUEBA EXITOSA - NOTICIAS COMPLETAS OBTENIDAS")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")




