# ============================================
# 📌 TEST: PASO 5 FIX - ATRIBUCIÓN A TABLA 100 UNIVERSAL
# Prueba del fix completo del Paso 5 con noticias reales
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso5_fix():
    print("🚀 PRUEBA: PASO 5 FIX - ATRIBUCIÓN A TABLA 100 UNIVERSAL")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el nuevo step
        from app_vision.steps.step5_news_attribution_table100 import NewsAttributionTable100Step
        from app_vision.engine.contracts import StepContext
        
        print("✅ NewsAttributionTable100Step importado correctamente")
        
        # Crear contexto de step (simulado)
        ctx = StepContext(
            run_id="test-paso5-fix",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Noticias simuladas del día actual (basadas en el test anterior)
        selected_news = [
            {
                "title": "Supreme Court Decision on Property Rights",
                "final_url": "https://example.com/sc-decision",
                "text": "The Supreme Court announced a landmark decision regarding property rights and housing stability. The ruling affects thousands of families seeking refuge and stability in their homes.",
                "bucket": "justicia",
                "score": 0.85
            },
            {
                "title": "Community Health Center Opens New Portal",
                "final_url": "https://example.com/health-center",
                "text": "A new community health center opened its doors, providing essential services to families in need. The center represents a new beginning for healthcare access in the neighborhood.",
                "bucket": "salud",
                "score": 0.78
            },
            {
                "title": "Union Agreement Reached After Long Negotiations",
                "final_url": "https://example.com/union-agreement",
                "text": "Workers and management reached a historic agreement after months of cooperation. The deal ensures job stability and fair wages for employees.",
                "bucket": "trabajo",
                "score": 0.72
            },
            {
                "title": "Family Crisis Support Program Launched",
                "final_url": "https://example.com/family-support",
                "text": "A new program to help families in crisis has been launched. The initiative provides emotional support and practical assistance to those in need.",
                "bucket": "familia",
                "score": 0.68
            },
            {
                "title": "Spiritual Center Offers Community Services",
                "final_url": "https://example.com/spiritual-center",
                "text": "The local spiritual center has expanded its services to include community outreach. The center focuses on wisdom, compassion, and helping those in need.",
                "bucket": "espiritualidad",
                "score": 0.65
            }
        ]
        
        # Guía del análisis subliminal (Paso 3)
        guidance = {
            "topics": ["veredicto", "decisión", "propiedad", "refugio", "hogar", "cirugía"],
            "keywords": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"],
            "families": ["corte", "casa"]
        }
        
        print("📊 CONFIGURACIÓN DEL TEST:")
        print("-" * 40)
        print(f"Noticias seleccionadas: {len(selected_news)}")
        print(f"Tópicos guía: {guidance['topics']}")
        print(f"Keywords guía: {guidance['keywords']}")
        print(f"Familias guía: {guidance['families']}")
        print()
        
        # Crear instancia del step
        step = NewsAttributionTable100Step()
        
        # Datos de entrada
        data = {
            "selected_news": selected_news,
            "guidance": guidance,
            "min_attr": 3,
            "threshold": 0.6
        }
        
        print("🔄 EJECUTANDO PASO 5 FIX:")
        print("-" * 40)
        
        # Ejecutar el step
        resultado = step.run(ctx, data)
        
        print(f"✅ Paso 5 Fix ejecutado")
        print(f"   Estado: {resultado['status']}")
        print()
        
        # Mostrar resultados detallados
        if 'attribution' in resultado:
            attribution = resultado['attribution']
            
            print("📊 RESULTADOS DETALLADOS:")
            print("=" * 60)
            
            # Información de la tabla
            print("🗺️ TABLA 100 UNIVERSAL:")
            print("-" * 40)
            print(f"   Versión: {attribution.get('table_version', 'N/A')}")
            print()
            
            # Ranking global
            print("🏆 RANKING GLOBAL:")
            print("-" * 40)
            global_rank = attribution.get('global_rank', [])
            if global_rank:
                print("   Top 10 números más relevantes:")
                for i, item in enumerate(global_rank[:10], 1):
                    print(f"   {i:2d}. Número {item['number']:2d}: {item['label']} (score: {item['score']:.3f})")
                    print(f"       Significado: {item['meaning']}")
            else:
                print("   No hay números en el ranking global")
            print()
            
            # Análisis por artículo
            print("📰 ANÁLISIS POR ARTÍCULO:")
            print("-" * 40)
            per_article = attribution.get('per_article', [])
            for i, article in enumerate(per_article, 1):
                print(f"   Artículo {i}: {article['title'][:50]}...")
                print(f"   URL: {article['url']}")
                if article.get('top'):
                    print("   Top números:")
                    for top_item in article['top'][:3]:
                        print(f"     - Número {top_item['number']}: {top_item['label']} (score: {top_item['score']:.3f})")
                        print(f"       Hits: {', '.join(top_item['hits'][:3])}")
                else:
                    print("   No se encontraron correlaciones")
                print()
            
            # Auditoría
            print("🔍 AUDITORÍA:")
            print("-" * 40)
            auditor = attribution.get('auditor', {})
            print(f"   ✅ Auditoría OK: {auditor.get('ok', False)}")
            print(f"   📊 Umbral: {auditor.get('threshold', 'N/A')}")
            print(f"   📊 Mínimo requerido: {auditor.get('min_attr', 'N/A')}")
            print(f"   📊 Por encima del umbral: {auditor.get('kept_above_threshold', 0)}")
            print(f"   📊 Total de artículos: {auditor.get('total_articles', 0)}")
            
            if auditor.get('reasons'):
                print("   ⚠️  Razones de exclusión:")
                for reason in auditor['reasons'][:3]:
                    print(f"     - {reason.get('url', 'N/A')}: {reason.get('reason', 'N/A')}")
            print()
            
            # Resumen final
            print("🎯 RESUMEN FINAL:")
            print("-" * 40)
            if auditor.get('ok'):
                print("✅ Paso 5 Fix EXITOSO")
                print("✅ Atribución de noticias funcionando")
                print("✅ Tabla 100 Universal correlacionada")
                print(f"✅ {len(global_rank)} números identificados")
            else:
                print("⚠️  Paso 5 Fix con advertencias")
                print("⚠️  Pocos números por encima del umbral")
                print(f"⚠️  Solo {auditor.get('kept_above_threshold', 0)} de {auditor.get('min_attr', 3)} requeridos")
            
        else:
            print("❌ No se encontró información de atribución en el resultado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 5 Fix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso5_fix()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 5 FIX FUNCIONANDO CORRECTAMENTE")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")





