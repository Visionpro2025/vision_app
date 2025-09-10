# ============================================
# 📌 TEST: NEWS SELECTOR 25 - GARANTIZA ≥25 NOTICIAS REALES
# Prueba el sistema que garantiza al menos 25 noticias alineadas con la guía
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_news_selector25():
    print("🚀 TEST: NEWS SELECTOR 25 - GARANTIZA ≥25 NOTICIAS REALES")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el step
        from app_vision.steps.step4_news_selector25 import NewsSelector25Step
        from app_vision.engine.contracts import StepContext
        
        print("✅ NewsSelector25Step importado correctamente")
        
        # Crear contexto de step (simulado)
        ctx = StepContext(
            run_id="test-news-selector25",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Noticias reales encontradas en el diagnóstico anterior
        noticias_reales = [
            # BBC News (5 artículos)
            {
                "title": "Huge drugs bust reveals battles on cocaine 'superhighway'",
                "url": "https://www.bbc.com/news/articles/c5yvplyrrwno",
                "published": "Mon, 08 Sep 2025 05:02:40 GMT",
                "summary": "Police operation uncovers major drug trafficking network"
            },
            {
                "title": "Ex-sergeant major admits sexually assaulting soldier who took her own life",
                "url": "https://www.bbc.com/news/articles/ckgqzxq0z55o",
                "published": "Mon, 08 Sep 2025 04:30:09 GMT",
                "summary": "Military court case involving sexual assault allegations"
            },
            {
                "title": "Unions warn government not to water down workers' rights bill",
                "url": "https://www.bbc.com/news/articles/cq65l5epl3eo",
                "published": "Sun, 07 Sep 2025 18:20:19 GMT",
                "summary": "Labor unions express concerns about proposed legislation"
            },
            {
                "title": "Alcaraz edges Sinner trilogy to win US Open",
                "url": "https://www.bbc.com/sport/tennis/articles/c8xrpd5jeveo",
                "published": "Sun, 07 Sep 2025 22:09:49 GMT",
                "summary": "Tennis championship final results"
            },
            {
                "title": "'He put his hand down my tights': Sexual harassment widespread among barristers, review finds",
                "url": "https://www.bbc.com/news/articles/c8xrejzk0edo",
                "published": "Mon, 08 Sep 2025 04:46:41 GMT",
                "summary": "Legal profession harassment investigation findings"
            },
            # NPR News (5 artículos)
            {
                "title": "Australian woman is sentenced to life for poisoning relatives with mushrooms",
                "url": "https://www.npr.org/2025/09/08/nx-s1-5533902/australia-erin-patterson-life-sentence-mushroom-murder",
                "published": "Mon, 08 Sep 2025 01:14:43 -0400",
                "summary": "Court sentencing in poisoning case"
            },
            {
                "title": "Carlos Alcaraz wins his 2nd U.S. Open at match delayed by Trump's attendance",
                "url": "https://www.npr.org/2025/09/07/nx-s1-5533207/carlos-alcaraz-trump-us-open-tennis-rolex",
                "published": "Sun, 07 Sep 2025 20:37:01 -0400",
                "summary": "Tennis tournament results with political context"
            },
            {
                "title": "More than 90,000 Jeep Grand Cherokees recalled over potential loss of drive power",
                "url": "https://www.npr.org/2025/09/07/nx-s1-5533180/jeep-grand-cherokee-recall-plug-in-hybrid",
                "published": "Sun, 07 Sep 2025 19:24:34 -0400",
                "summary": "Automotive safety recall announcement"
            },
            {
                "title": "Trump walks back Chicago 'war' threat, but vows to 'clean up' cities",
                "url": "https://www.npr.org/2025/09/07/nx-s1-5533191/trump-chicago-threat-baltimore-new-orleans",
                "published": "Sun, 07 Sep 2025 18:41:43 -0400",
                "summary": "Political statements about urban policy"
            },
            {
                "title": "Postal traffic to US drops more than 80% after trade exemption rule ends, UN agency says",
                "url": "https://www.npr.org/2025/09/07/nx-s1-5533121/postal-traffic-to-us-drops-more-than-80-after-trade-exemption-rule-ends-un-agency-says",
                "published": "Sun, 07 Sep 2025 13:54:41 -0400",
                "summary": "International trade policy impact analysis"
            },
            # BBC World News (5 artículos)
            {
                "title": "Palestinian prisoners not being given adequate food, Israel top court says",
                "url": "https://www.bbc.com/news/articles/c1mxlk518vko",
                "published": "Mon, 08 Sep 2025 02:53:54 GMT",
                "summary": "International human rights court ruling"
            },
            {
                "title": "European leaders to visit US to discuss war in Ukraine, Trump says",
                "url": "https://www.bbc.com/news/articles/cwyrx205dj2o",
                "published": "Mon, 08 Sep 2025 03:10:08 GMT",
                "summary": "International diplomacy and conflict discussions"
            },
            {
                "title": "South Korean worker tells BBC of panic and confusion during Hyundai ICE raid",
                "url": "https://www.bbc.com/news/articles/c5yqg0rln74o",
                "published": "Sun, 07 Sep 2025 23:14:55 GMT",
                "summary": "Immigration enforcement workplace incident"
            },
            {
                "title": "France is set to vote out another PM. Can anything break its political deadlock?",
                "url": "https://www.bbc.com/news/articles/cm2z8xyz68mo",
                "published": "Sun, 07 Sep 2025 23:52:21 GMT",
                "summary": "Political instability and governance challenges"
            },
            {
                "title": "'Suitcase murder' trial begins in New Zealand",
                "url": "https://www.bbc.com/news/articles/cn83jjx9pjvo",
                "published": "Mon, 08 Sep 2025 05:12:14 GMT",
                "summary": "Criminal trial proceedings"
            }
        ]
        
        # Guía del Paso 3 (análisis subliminal real)
        guia_paso3 = {
            "topics": ["veredicto", "decisión", "propiedad", "refugio", "hogar", "cirugía"],
            "keywords": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"],
            "families": ["corte", "casa"]
        }
        
        print("📊 CONFIGURACIÓN DEL TEST:")
        print("-" * 50)
        print(f"Noticias reales disponibles: {len(noticias_reales)}")
        print(f"Guía del Paso 3: {guia_paso3['topics']}")
        print(f"Keywords: {guia_paso3['keywords']}")
        print(f"Familias: {guia_paso3['families']}")
        print(f"Mínimo requerido: 25 noticias")
        print()
        
        # Crear instancia del step
        step = NewsSelector25Step()
        
        # Datos de entrada
        data = {
            "valid_news": noticias_reales,
            "guidance": guia_paso3,
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
        
        # Mostrar resultados
        selected_25 = resultado.get('selected_25', [])
        selector_audit = resultado.get('selector_audit', {})
        
        print("📊 RESULTADOS DEL NEWS SELECTOR 25:")
        print("=" * 80)
        
        # Auditoría
        print("🔍 AUDITORÍA DEL SELECTOR:")
        print("-" * 40)
        print(f"   📊 Total de entrada: {selector_audit.get('input_total', 0)}")
        print(f"   📊 Total evaluadas: {selector_audit.get('scored_total', 0)}")
        print(f"   📊 Seleccionadas: {selector_audit.get('selected', 0)}")
        print(f"   📊 Umbral elegido: {selector_audit.get('threshold_chosen', 'N/A')}")
        print(f"   📊 Fallback aplicado: {selector_audit.get('fallback_applied', False)}")
        print(f"   📊 Razones: {', '.join(selector_audit.get('reasons', []))}")
        print(f"   📊 Términos guía usados: {len(selector_audit.get('guide_terms_used', []))}")
        print()
        
        # Noticias seleccionadas
        print("📰 NOTICIAS SELECCIONADAS (≥25):")
        print("-" * 40)
        if selected_25:
            print(f"✅ Total seleccionadas: {len(selected_25)}")
            print()
            for i, noticia in enumerate(selected_25, 1):
                print(f"🔸 NOTICIA {i}: {noticia['title']}")
                print(f"   🔗 URL: {noticia['url']}")
                print(f"   📊 Score: {noticia['score']}")
                print(f"   🎯 Hits: {', '.join(noticia.get('hits', [])[:5])}")
                if 'reason' in noticia:
                    print(f"   📋 Razón: {noticia['reason']}")
                print()
        else:
            print("❌ No se seleccionaron noticias")
        
        # Análisis de cobertura
        print("🎯 ANÁLISIS DE COBERTURA:")
        print("-" * 40)
        if len(selected_25) >= 25:
            print("✅ OBJETIVO CUMPLIDO: ≥25 noticias seleccionadas")
            print("✅ Sistema funcionando correctamente")
        elif len(selected_25) > 0:
            print(f"⚠️  PARCIAL: {len(selected_25)} noticias seleccionadas (objetivo: 25)")
            print("⚠️  Sistema funcionando pero con limitaciones")
        else:
            print("❌ FALLO: 0 noticias seleccionadas")
            print("❌ Sistema no pudo encontrar noticias alineadas")
        
        # Guardar reporte
        reporte = {
            "timestamp": datetime.now().isoformat(),
            "selected_25": selected_25,
            "selector_audit": selector_audit,
            "objetivo_cumplido": len(selected_25) >= 25
        }
        
        # Crear directorio reports si no existe
        os.makedirs("reports", exist_ok=True)
        
        # Guardar reporte
        with open("reports/news_selector25_resultado.json", "w", encoding="utf-8") as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: reports/news_selector25_resultado.json")
        
        return len(selected_25) >= 25
        
    except Exception as e:
        print(f"❌ Error en el test de News Selector 25: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_news_selector25()
    if success:
        print("\n🎉 TEST EXITOSO - NEWS SELECTOR 25 FUNCIONANDO")
    else:
        print("\n💥 TEST FALLIDO - REVISAR CONFIGURACIÓN")





