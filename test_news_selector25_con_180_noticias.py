# ============================================
# 📌 TEST: NEWS SELECTOR 25 CON 180 NOTICIAS REALES
# Usa las noticias reales encontradas para seleccionar las 25 mejores
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_news_selector25_con_180_noticias():
    print("🚀 NEWS SELECTOR 25 CON 180 NOTICIAS REALES")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el step de News Selector 25
        from app_vision.steps.step4_news_selector25 import NewsSelector25Step
        from app_vision.engine.contracts import StepContext
        
        print("✅ NewsSelector25Step importado correctamente")
        
        # Crear contexto de step (simulado)
        ctx = StepContext(
            run_id="test-news-selector-25",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Cargar las 180 noticias reales del reporte anterior
        try:
            with open("reports/busqueda_masiva_noticias.json", "r", encoding="utf-8") as f:
                reporte_completo = json.load(f)
            
            print("✅ Reporte de búsqueda masiva cargado")
            print(f"📊 Total de noticias disponibles: {reporte_completo.get('total_articles', 0)}")
            
        except FileNotFoundError:
            print("❌ No se encontró el reporte de búsqueda masiva")
            print("   Ejecutando búsqueda básica...")
            reporte_completo = {"total_articles": 0, "feeds_report": []}
        
        # Crear lista de noticias válidas a partir del reporte
        valid_news = []
        feeds_report = reporte_completo.get("feeds_report", [])
        
        for feed_data in feeds_report:
            if feed_data.get('items', 0) > 0:
                titles = feed_data.get('titles', [])
                for article in titles:
                    if article.get('url'):
                        valid_news.append({
                            "url": article.get('url'),
                            "title": article.get('title', 'Sin título'),
                            "published": article.get('published', 'Sin fecha'),
                            "feed": feed_data.get('feed', 'N/A')
                        })
        
        print(f"📰 Noticias válidas extraídas: {len(valid_news)}")
        print()
        
        # Guía del Paso 3 (simulada basada en el análisis subliminal)
        guidance = {
            "topics": [
                "crisis", "familia", "comunidad", "ayuda", "solidaridad", "refugio",
                "vivienda", "empleo", "salud", "educación", "seguridad", "inmigración",
                "corte", "veredicto", "decisión", "propiedad", "hogar", "shelter",
                "homeless", "housing", "eviction", "court", "ruling", "sentencing"
            ],
            "keywords": [
                "crisis", "familia", "comunidad", "ayuda", "solidaridad", "refugio",
                "vivienda", "empleo", "salud", "educación", "seguridad", "inmigración",
                "corte", "veredicto", "decisión", "propiedad", "hogar", "shelter",
                "homeless", "housing", "eviction", "court", "ruling", "sentencing"
            ],
            "families": [
                "justicia", "derechos", "comunidad", "familia", "vivienda", "empleo",
                "salud", "educación", "seguridad", "inmigración", "corte", "veredicto"
            ]
        }
        
        print("🎯 CONFIGURACIÓN DE NEWS SELECTOR 25:")
        print("-" * 50)
        print(f"Noticias de entrada: {len(valid_news)}")
        print(f"Objetivo: Seleccionar 25 noticias")
        print(f"Umbral inicial: 0.6")
        print(f"Términos de guía: {len(guidance['topics'])}")
        print()
        
        # Crear instancia del step
        step = NewsSelector25Step()
        
        # Datos de entrada
        data = {
            "valid_news": valid_news,
            "guidance": guidance,
            "start_threshold": 0.6,
            "min_keep": 25,
            "require_body": False
        }
        
        print("🔄 EJECUTANDO NEWS SELECTOR 25:")
        print("-" * 50)
        
        # Ejecutar el step
        resultado = step.run(ctx, data)
        
        print(f"✅ News Selector 25 ejecutado")
        print()
        
        # Mostrar resultados detallados
        print("📊 RESULTADOS DE NEWS SELECTOR 25:")
        print("=" * 80)
        
        selected_25 = resultado.get('selected_25', [])
        selector_audit = resultado.get('selector_audit', {})
        
        print(f"📰 NOTICIAS SELECCIONADAS: {len(selected_25)}")
        print()
        
        # Mostrar las noticias seleccionadas
        if selected_25:
            print("🎯 NOTICIAS SELECCIONADAS (Top 25):")
            print("-" * 50)
            
            for i, article in enumerate(selected_25, 1):
                url = article.get('url', 'N/A')
                title = article.get('title', 'Sin título')
                score = article.get('score', 0.0)
                hits = article.get('hits', [])
                bucket = article.get('bucket', 'N/A')
                reason = article.get('reason', '')
                
                print(f"🔸 {i:2d}. {title[:60]}...")
                print(f"   📊 Score: {score:.3f}")
                print(f"   🎯 Hits: {', '.join(hits[:3])}{'...' if len(hits) > 3 else ''}")
                print(f"   📂 Bucket: {bucket}")
                if reason:
                    print(f"   💡 Razón: {reason}")
                print(f"   🔗 URL: {url[:80]}...")
                print("-" * 60)
        else:
            print("❌ No se seleccionaron noticias")
        
        # Mostrar auditoría del selector
        print("\n📈 AUDITORÍA DEL SELECTOR:")
        print("-" * 50)
        print(f"📊 Noticias de entrada: {selector_audit.get('input_total', 0)}")
        print(f"📊 Noticias evaluadas: {selector_audit.get('scored_total', 0)}")
        print(f"📊 Noticias seleccionadas: {selector_audit.get('selected', 0)}")
        print(f"📊 Umbral elegido: {selector_audit.get('threshold_chosen', 'N/A')}")
        print(f"📊 Fallback aplicado: {selector_audit.get('fallback_applied', False)}")
        print(f"📊 Razones: {', '.join(selector_audit.get('reasons', []))}")
        print(f"📊 Términos de guía usados: {len(selector_audit.get('guide_terms_used', []))}")
        
        # Análisis de buckets
        if selected_25:
            buckets = {}
            for article in selected_25:
                bucket = article.get('bucket', 'otros')
                buckets[bucket] = buckets.get(bucket, 0) + 1
            
            print(f"\n📂 DISTRIBUCIÓN POR BUCKETS:")
            print("-" * 50)
            for bucket, count in sorted(buckets.items(), key=lambda x: x[1], reverse=True):
                print(f"   {bucket}: {count} noticias")
        
        # Diagnóstico final
        print(f"\n🎯 DIAGNÓSTICO FINAL:")
        print("=" * 80)
        
        if len(selected_25) >= 25:
            print("✅ ÉXITO: Se seleccionaron 25+ noticias")
            print("   - Objetivo cumplido")
            print("   - Listo para Paso 5 (Atribución a Tabla 100)")
        elif len(selected_25) >= 15:
            print("⚠️  PARCIAL: Se seleccionaron 15-24 noticias")
            print("   - Objetivo parcialmente cumplido")
            print("   - Considerar ajustar criterios")
        else:
            print("❌ LIMITADO: Se seleccionaron <15 noticias")
            print("   - Objetivo no cumplido")
            print("   - Revisar guía y criterios")
        
        # Guardar reporte de selección
        reporte_seleccion = {
            "timestamp": datetime.now().isoformat(),
            "input_news": len(valid_news),
            "selected_news": len(selected_25),
            "selector_audit": selector_audit,
            "selected_articles": selected_25
        }
        
        # Crear directorio reports si no existe
        os.makedirs("reports", exist_ok=True)
        
        # Guardar reporte
        with open("reports/news_selector25_resultado.json", "w", encoding="utf-8") as f:
            json.dump(reporte_seleccion, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte de selección guardado en: reports/news_selector25_resultado.json")
        
        return len(selected_25) >= 25
        
    except Exception as e:
        print(f"❌ Error en News Selector 25: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_news_selector25_con_180_noticias()
    if success:
        print("\n🎉 NEWS SELECTOR 25 EXITOSO - 25+ NOTICIAS SELECCIONADAS")
    else:
        print("\n💥 NEWS SELECTOR 25 LIMITADO - REVISAR CRITERIOS")




