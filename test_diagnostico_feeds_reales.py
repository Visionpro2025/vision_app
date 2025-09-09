# ============================================
# 📌 TEST: DIAGNÓSTICO DE FEEDS RSS REALES
# Verifica cada feed real y muestra noticias disponibles
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_diagnostico_feeds_reales():
    print("🚀 DIAGNÓSTICO DE FEEDS RSS REALES")
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
            run_id="test-diagnostico-feeds",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Feeds RSS reales para diagnóstico
        feeds_reales = [
            "https://feeds.bbci.co.uk/news/rss.xml",
            "https://rss.cnn.com/rss/edition.rss", 
            "https://www.reuters.com/world/us/rss",
            "https://feeds.npr.org/1001/rss.xml",
            "https://feeds.bbci.co.uk/news/world/rss.xml"
        ]
        
        print("📊 CONFIGURACIÓN DEL DIAGNÓSTICO:")
        print("-" * 50)
        print(f"Feeds RSS a verificar: {len(feeds_reales)}")
        for i, feed in enumerate(feeds_reales, 1):
            print(f"   {i}. {feed}")
        print(f"Máximo por feed: 5")
        print()
        
        # Crear instancia del step
        step = NewsFeedsCheckStep()
        
        # Datos de entrada
        data = {
            "feeds": feeds_reales,
            "max_per_feed": 5
        }
        
        print("🔄 EJECUTANDO DIAGNÓSTICO DE FEEDS:")
        print("-" * 50)
        
        # Ejecutar el step
        resultado = step.run(ctx, data)
        
        print(f"✅ Diagnóstico ejecutado")
        print()
        
        # Mostrar resultados detallados
        print("📊 RESULTADOS DEL DIAGNÓSTICO:")
        print("=" * 80)
        
        feeds_report = resultado.get('feeds_report', [])
        total_articles = resultado.get('total_articles', 0)
        
        print(f"📰 TOTAL DE ARTÍCULOS ENCONTRADOS: {total_articles}")
        print()
        
        # Análisis por feed
        for i, feed_data in enumerate(feeds_report, 1):
            feed_url = feed_data.get('feed', 'N/A')
            items = feed_data.get('items', 0)
            error = feed_data.get('error')
            
            print(f"🔸 FEED {i}: {feed_url}")
            print(f"   📊 Artículos encontrados: {items}")
            
            if error:
                print(f"   ❌ Error: {error}")
                print("   🔴 ESTADO: FEED ROTO")
            elif items == 0:
                print("   ⚠️  No se encontraron artículos")
                print("   🟡 ESTADO: FEED VACÍO")
            else:
                print("   ✅ Artículos disponibles:")
                titles = feed_data.get('titles', [])
                for j, article in enumerate(titles, 1):
                    title = article.get('title', 'Sin título')
                    published = article.get('published', 'Sin fecha')
                    url = article.get('url', 'Sin URL')
                    
                    print(f"      {j}. {title}")
                    print(f"         📅 Fecha: {published}")
                    print(f"         🔗 URL: {url}")
                print("   🟢 ESTADO: FEED FUNCIONANDO")
            print("-" * 60)
        
        # Resumen de diagnóstico
        print("\n🎯 RESUMEN DEL DIAGNÓSTICO:")
        print("=" * 80)
        
        feeds_funcionando = len([f for f in feeds_report if f.get('items', 0) > 0])
        feeds_rotos = len([f for f in feeds_report if f.get('error')])
        feeds_vacios = len([f for f in feeds_report if not f.get('error') and f.get('items', 0) == 0])
        
        print(f"📊 Feeds totales: {len(feeds_report)}")
        print(f"🟢 Feeds funcionando: {feeds_funcionando}")
        print(f"🔴 Feeds rotos: {feeds_rotos}")
        print(f"🟡 Feeds vacíos: {feeds_vacios}")
        print(f"📰 Total artículos: {total_articles}")
        print()
        
        # Diagnóstico del problema
        if total_articles == 0:
            print("❌ DIAGNÓSTICO: PROBLEMA EN FEEDS")
            print("   - Todos los feeds están rotos o vacíos")
            print("   - Verificar conectividad de red")
            print("   - Verificar URLs de feeds")
        elif total_articles < 10:
            print("⚠️  DIAGNÓSTICO: POCOS ARTÍCULOS")
            print("   - Feeds funcionan pero con pocos artículos")
            print("   - Puede ser problema de horario o disponibilidad")
        else:
            print("✅ DIAGNÓSTICO: FEEDS FUNCIONANDO")
            print("   - Feeds están funcionando correctamente")
            print("   - El problema está en el filtro de contenido del Paso 5")
            print("   - Revisar umbrales y criterios de atribución")
        
        # Guardar reporte en JSON
        reporte_json = {
            "timestamp": datetime.now().isoformat(),
            "total_articles": total_articles,
            "feeds_report": feeds_report,
            "diagnostico": {
                "feeds_funcionando": feeds_funcionando,
                "feeds_rotos": feeds_rotos,
                "feeds_vacios": feeds_vacios,
                "problema_identificado": "feeds" if total_articles == 0 else "filtro" if total_articles >= 10 else "pocos_articulos"
            }
        }
        
        # Crear directorio reports si no existe
        os.makedirs("reports", exist_ok=True)
        
        # Guardar reporte
        with open("reports/feeds_check_diagnostico.json", "w", encoding="utf-8") as f:
            json.dump(reporte_json, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: reports/feeds_check_diagnostico.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el diagnóstico de feeds: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_diagnostico_feeds_reales()
    if success:
        print("\n🎉 DIAGNÓSTICO COMPLETADO EXITOSAMENTE")
    else:
        print("\n💥 DIAGNÓSTICO FALLIDO - REVISAR ERRORES")




