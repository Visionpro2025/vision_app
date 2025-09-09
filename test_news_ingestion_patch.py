# ============================================
# 📌 TEST: PATCH DE INGESTA DE NOTICIAS
# Prueba del sistema corregido de ingesta de noticias
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_news_ingestion_patch():
    print("🚀 PRUEBA: PATCH DE INGESTA DE NOTICIAS")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el módulo de ingesta
        from app_vision.modules.news_ingestion import ProfessionalNewsIngestion
        
        print("✅ ProfessionalNewsIngestion importado correctamente")
        
        # Crear instancia con feeds de prueba
        feeds = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            "https://www.reuters.com/world/us/rss"
        ]
        
        ingestion = ProfessionalNewsIngestion(feeds=feeds, max_per_feed=10)
        
        print("✅ Instancia de ProfessionalNewsIngestion creada")
        print(f"   Feeds configurados: {len(feeds)}")
        print(f"   Max por feed: 10")
        print()
        
        # Test 1: collect_news()
        print("🔄 TEST 1: collect_news()")
        print("-" * 40)
        
        result_collect = ingestion.collect_news()
        
        print(f"✅ collect_news() ejecutado")
        print(f"   URLs encontradas: {result_collect['count']}")
        print(f"   Fuentes procesadas: {len(result_collect['sources'])}")
        print(f"   Logs: {len(result_collect['log'])}")
        print()
        
        if result_collect['count'] > 0:
            print("📰 PRIMERAS 5 URLs ENCONTRADAS:")
            for i, url in enumerate(result_collect['urls'][:5], 1):
                print(f"   {i}. {url}")
            print()
        
        # Test 2: search_emotional_news()
        print("🔄 TEST 2: search_emotional_news()")
        print("-" * 40)
        
        guidance_terms = ['decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio']
        
        result_emotional = ingestion.search_emotional_news(guidance_terms)
        
        print(f"✅ search_emotional_news() ejecutado")
        print(f"   Términos guía: {guidance_terms}")
        print(f"   URLs emocionales: {result_emotional['count']}")
        print(f"   Fuentes procesadas: {len(result_emotional['sources'])}")
        print(f"   Logs: {len(result_emotional['log'])}")
        print()
        
        if result_emotional['count'] > 0:
            print("💭 PRIMERAS 5 URLs EMOCIONALES:")
            for i, url in enumerate(result_emotional['urls'][:5], 1):
                print(f"   {i}. {url}")
            print()
        
        # Test 3: YourNewsFetchStep
        print("🔄 TEST 3: YourNewsFetchStep")
        print("-" * 40)
        
        from app_vision.steps.step2_news_fetch_fixed import YourNewsFetchStep
        from app_vision.engine.contracts import StepContext
        
        # Crear contexto de prueba
        ctx = StepContext(
            run_id="test_news_ingestion_patch",
            seed=12345,
            cfg={},
            state_dir="./test_state",
            plan_path="./test_plan.json"
        )
        
        # Crear step
        step = YourNewsFetchStep()
        
        # Datos de entrada
        data = {
            "feeds": feeds,
            "max_per_feed": 10,
            "mode": "emotional",
            "guidance_terms": guidance_terms
        }
        
        result_step = step.run(ctx, data)
        
        print(f"✅ YourNewsFetchStep ejecutado")
        print(f"   URLs devueltas: {result_step['count']}")
        print(f"   Fuentes: {len(result_step['sources'])}")
        print(f"   Logs: {len(result_step['log'])}")
        print()
        
        if result_step['count'] > 0:
            print("📊 PRIMERAS 5 URLs DEL STEP:")
            for i, url in enumerate(result_step['urls'][:5], 1):
                print(f"   {i}. {url}")
            print()
        
        # Mostrar logs si hay
        if result_step['log']:
            print("📝 LOGS DEL SISTEMA:")
            for log in result_step['log']:
                print(f"   - {log}")
            print()
        
        # Resumen final
        print("🎯 RESUMEN FINAL:")
        print("-" * 40)
        print(f"✅ collect_news(): {result_collect['count']} URLs")
        print(f"✅ search_emotional_news(): {result_emotional['count']} URLs")
        print(f"✅ YourNewsFetchStep: {result_step['count']} URLs")
        print()
        
        if result_collect['count'] > 0 or result_emotional['count'] > 0 or result_step['count'] > 0:
            print("🎉 PATCH EXITOSO - NOTICIAS ACOPIADAS CORRECTAMENTE")
        else:
            print("⚠️  PATCH FUNCIONANDO PERO SIN NOTICIAS - REVISAR FEEDS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del patch de ingesta: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_news_ingestion_patch()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PATCH DE INGESTA FUNCIONANDO")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")



