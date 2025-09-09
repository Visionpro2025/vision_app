# ============================================
# 📌 TEST: BÚSQUEDA MASIVA DE NOTICIAS
# Expande fuentes para encontrar mucho más contenido emocional/social
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_busqueda_masiva_noticias():
    print("🚀 BÚSQUEDA MASIVA DE NOTICIAS - EXPANDIENDO FUENTES")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el step de diagnóstico
        from app_vision.steps.stepX_news_feeds_check import NewsFeedsCheckStep
        from app_vision.engine.contracts import StepContext
        
        print("✅ NewsFeedsCheckStep importado correctamente")
        
        # Crear contexto de step (simulado)
        ctx = StepContext(
            run_id="test-busqueda-masiva",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # EXPANDIR SIGNIFICATIVAMENTE LAS FUENTES DE NOTICIAS
        feeds_expandidos = [
            # Fuentes principales internacionales
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss",
            "https://www.reuters.com/world/us/rss",
            "https://feeds.npr.org/1001/rss.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            
            # Fuentes específicas de noticias sociales/emocionales
            "https://feeds.bbci.co.uk/news/health/rss.xml",
            "https://feeds.bbci.co.uk/news/education/rss.xml",
            "https://feeds.bbci.co.uk/news/uk/rss.xml",
            "https://rss.cnn.com/rss/edition_us.rss",
            "https://rss.cnn.com/rss/edition_americas.rss",
            
            # Fuentes de noticias locales y comunitarias
            "https://feeds.npr.org/1002/rss.xml",  # NPR News
            "https://feeds.npr.org/1003/rss.xml",  # NPR Politics
            "https://feeds.npr.org/1004/rss.xml",  # NPR Health
            "https://feeds.npr.org/1005/rss.xml",  # NPR Education
            "https://feeds.npr.org/1006/rss.xml",  # NPR Business
            
            # Fuentes adicionales de noticias sociales
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "https://rss.cnn.com/rss/edition_world.rss",
            "https://rss.cnn.com/rss/edition_technology.rss",
            
            # Fuentes de noticias comunitarias y locales
            "https://feeds.npr.org/1007/rss.xml",  # NPR Science
            "https://feeds.npr.org/1008/rss.xml",  # NPR Arts
            "https://feeds.npr.org/1009/rss.xml",  # NPR Books
            "https://feeds.npr.org/1010/rss.xml",  # NPR Music
            "https://feeds.npr.org/1011/rss.xml",  # NPR Food
            
            # Fuentes adicionales de noticias emocionales
            "https://feeds.bbci.co.uk/news/entertainment/rss.xml",
            "https://feeds.bbci.co.uk/news/arts/rss.xml",
            "https://rss.cnn.com/rss/edition_entertainment.rss",
            "https://rss.cnn.com/rss/edition_living.rss",
            "https://rss.cnn.com/rss/edition_travel.rss",
            
            # Fuentes de noticias de justicia y derechos
            "https://feeds.bbci.co.uk/news/uk_politics/rss.xml",
            "https://rss.cnn.com/rss/edition_politics.rss",
            "https://rss.cnn.com/rss/edition_justice.rss",
            "https://feeds.npr.org/1012/rss.xml",  # NPR Justice
            "https://feeds.npr.org/1013/rss.xml",  # NPR Law
        ]
        
        print("📊 CONFIGURACIÓN DE BÚSQUEDA MASIVA:")
        print("-" * 50)
        print(f"Total de feeds RSS: {len(feeds_expandidos)}")
        print(f"Máximo por feed: 10 (aumentado)")
        print(f"Objetivo: Encontrar noticias emocionales/sociales")
        print()
        
        # Crear instancia del step
        step = NewsFeedsCheckStep()
        
        # Datos de entrada expandidos
        data = {
            "feeds": feeds_expandidos,
            "max_per_feed": 10  # Aumentado de 5 a 10
        }
        
        print("🔄 EJECUTANDO BÚSQUEDA MASIVA:")
        print("-" * 50)
        
        # Ejecutar el step
        resultado = step.run(ctx, data)
        
        print(f"✅ Búsqueda masiva ejecutada")
        print()
        
        # Mostrar resultados detallados
        print("📊 RESULTADOS DE BÚSQUEDA MASIVA:")
        print("=" * 80)
        
        feeds_report = resultado.get('feeds_report', [])
        total_articles = resultado.get('total_articles', 0)
        
        print(f"📰 TOTAL DE ARTÍCULOS ENCONTRADOS: {total_articles}")
        print()
        
        # Análisis por feed
        feeds_funcionando = 0
        feeds_vacios = 0
        feeds_rotos = 0
        total_noticias = 0
        
        for i, feed_data in enumerate(feeds_report, 1):
            feed_url = feed_data.get('feed', 'N/A')
            items = feed_data.get('items', 0)
            error = feed_data.get('error')
            
            print(f"🔸 FEED {i:2d}: {feed_url}")
            print(f"   📊 Artículos: {items}")
            
            if error:
                print(f"   ❌ Error: {error}")
                print("   🔴 ESTADO: FEED ROTO")
                feeds_rotos += 1
            elif items == 0:
                print("   ⚠️  Sin artículos")
                print("   🟡 ESTADO: FEED VACÍO")
                feeds_vacios += 1
            else:
                print("   ✅ Artículos disponibles:")
                titles = feed_data.get('titles', [])
                for j, article in enumerate(titles[:3], 1):  # Mostrar solo primeros 3
                    title = article.get('title', 'Sin título')
                    published = article.get('published', 'Sin fecha')
                    print(f"      {j}. {title[:60]}...")
                    print(f"         📅 {published}")
                if len(titles) > 3:
                    print(f"      ... y {len(titles) - 3} más")
                print("   🟢 ESTADO: FEED FUNCIONANDO")
                feeds_funcionando += 1
                total_noticias += items
            print("-" * 60)
        
        # Resumen estadístico
        print("\n📈 RESUMEN ESTADÍSTICO:")
        print("=" * 80)
        print(f"📊 Feeds totales: {len(feeds_report)}")
        print(f"🟢 Feeds funcionando: {feeds_funcionando}")
        print(f"🔴 Feeds rotos: {feeds_rotos}")
        print(f"🟡 Feeds vacíos: {feeds_vacios}")
        print(f"📰 Total de noticias: {total_noticias}")
        print(f"📊 Promedio por feed funcionando: {total_noticias / max(feeds_funcionando, 1):.1f}")
        print()
        
        # Análisis de contenido emocional/social
        print("🎯 ANÁLISIS DE CONTENIDO EMOCIONAL/SOCIAL:")
        print("-" * 50)
        
        # Palabras clave emocionales/sociales a buscar
        palabras_clave = [
            "crisis", "familia", "comunidad", "ayuda", "solidaridad", "refugio",
            "vivienda", "empleo", "salud", "educación", "seguridad", "inmigración",
            "corte", "veredicto", "decisión", "propiedad", "hogar", "shelter",
            "homeless", "housing", "eviction", "court", "ruling", "sentencing"
        ]
        
        noticias_emocionales = 0
        for feed_data in feeds_report:
            if feed_data.get('items', 0) > 0:
                titles = feed_data.get('titles', [])
                for article in titles:
                    title = article.get('title', '').lower()
                    if any(keyword in title for keyword in palabras_clave):
                        noticias_emocionales += 1
        
        print(f"📊 Noticias con contenido emocional/social: {noticias_emocionales}")
        print(f"📊 Porcentaje de contenido relevante: {(noticias_emocionales / max(total_noticias, 1)) * 100:.1f}%")
        print()
        
        # Diagnóstico final
        if total_noticias >= 50:
            print("✅ DIAGNÓSTICO: BÚSQUEDA EXITOSA")
            print("   - Se encontraron suficientes noticias")
            print("   - Contenido diverso disponible")
            print("   - Listo para News Selector 25")
        elif total_noticias >= 25:
            print("⚠️  DIAGNÓSTICO: BÚSQUEDA PARCIAL")
            print("   - Se encontraron noticias pero pueden ser insuficientes")
            print("   - Considerar ajustar criterios de selección")
        else:
            print("❌ DIAGNÓSTICO: BÚSQUEDA LIMITADA")
            print("   - Pocas noticias encontradas")
            print("   - Revisar fuentes y conectividad")
        
        # Guardar reporte completo
        reporte_completo = {
            "timestamp": datetime.now().isoformat(),
            "total_feeds": len(feeds_report),
            "feeds_funcionando": feeds_funcionando,
            "feeds_rotos": feeds_rotos,
            "feeds_vacios": feeds_vacios,
            "total_articles": total_noticias,
            "noticias_emocionales": noticias_emocionales,
            "feeds_report": feeds_report
        }
        
        # Crear directorio reports si no existe
        os.makedirs("reports", exist_ok=True)
        
        # Guardar reporte
        with open("reports/busqueda_masiva_noticias.json", "w", encoding="utf-8") as f:
            json.dump(reporte_completo, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte completo guardado en: reports/busqueda_masiva_noticias.json")
        
        return total_noticias >= 25
        
    except Exception as e:
        print(f"❌ Error en la búsqueda masiva: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_busqueda_masiva_noticias()
    if success:
        print("\n🎉 BÚSQUEDA MASIVA EXITOSA - NOTICIAS ENCONTRADAS")
    else:
        print("\n💥 BÚSQUEDA MASIVA LIMITADA - REVISAR FUENTES")




