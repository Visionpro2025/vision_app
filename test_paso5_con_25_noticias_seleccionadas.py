# ============================================
# 📌 TEST: PASO 5 - ATRIBUCIÓN A TABLA 100 CON 25 NOTICIAS SELECCIONADAS
# Usa las 25 noticias seleccionadas para realizar atribución a Tabla 100
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso5_con_25_noticias_seleccionadas():
    print("🚀 PASO 5: ATRIBUCIÓN A TABLA 100 CON 25 NOTICIAS SELECCIONADAS")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el step de News Attribution Table 100
        from app_vision.steps.step5_news_attribution_table100 import NewsAttributionTable100Step
        from app_vision.engine.contracts import StepContext
        
        print("✅ NewsAttributionTable100Step importado correctamente")
        
        # Crear contexto de step (simulado)
        ctx = StepContext(
            run_id="test-paso5-tabla100",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Cargar las 25 noticias seleccionadas del reporte anterior
        try:
            with open("reports/news_selector25_resultado.json", "r", encoding="utf-8") as f:
                reporte_seleccion = json.load(f)
            
            print("✅ Reporte de News Selector 25 cargado")
            print(f"📊 Noticias seleccionadas disponibles: {reporte_seleccion.get('selected_news', 0)}")
            
        except FileNotFoundError:
            print("❌ No se encontró el reporte de News Selector 25")
            print("   Usando noticias de prueba...")
            reporte_seleccion = {"selected_news": 0, "selected_articles": []}
        
        # Obtener las 25 noticias seleccionadas
        selected_news = reporte_seleccion.get("selected_articles", [])
        
        if not selected_news:
            print("❌ No hay noticias seleccionadas disponibles")
            return False
        
        print(f"📰 Noticias seleccionadas cargadas: {len(selected_news)}")
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
        
        print("🎯 CONFIGURACIÓN DE PASO 5:")
        print("-" * 50)
        print(f"Noticias de entrada: {len(selected_news)}")
        print(f"Umbral mínimo: 0.6")
        print(f"Mínimo atribuido: 3")
        print(f"Términos de guía: {len(guidance['topics'])}")
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
        
        print("🔄 EJECUTANDO PASO 5 - ATRIBUCIÓN A TABLA 100:")
        print("-" * 50)
        
        # Ejecutar el step
        resultado = step.run(ctx, data)
        
        print(f"✅ Paso 5 ejecutado")
        print()
        
        # Mostrar resultados detallados
        print("📊 RESULTADOS DE PASO 5 - ATRIBUCIÓN A TABLA 100:")
        print("=" * 80)
        
        attribution = resultado.get('attribution', {})
        status = resultado.get('status', 'UNKNOWN')
        
        print(f"📊 ESTADO: {status}")
        print()
        
        # Mostrar información de la tabla
        table_version = attribution.get('table_version', 'N/A')
        per_article = attribution.get('per_article', [])
        global_rank = attribution.get('global_rank', [])
        auditor = attribution.get('auditor', {})
        
        print(f"📋 INFORMACIÓN DE LA TABLA:")
        print("-" * 50)
        print(f"Versión de tabla: {table_version}")
        print(f"Artículos procesados: {len(per_article)}")
        print(f"Números en ranking global: {len(global_rank)}")
        print()
        
        # Mostrar ranking global de números
        if global_rank:
            print("🏆 RANKING GLOBAL DE NÚMEROS (Top 20):")
            print("-" * 50)
            
            for i, item in enumerate(global_rank[:20], 1):
                number = item.get('number', 0)
                score = item.get('score', 0.0)
                label = item.get('label', 'N/A')
                meaning = item.get('meaning', 'N/A')
                
                print(f"🔸 {i:2d}. Número {number:2d}: {label}")
                print(f"   📊 Score: {score:.3f}")
                print(f"   💡 Significado: {meaning}")
                print("-" * 60)
        else:
            print("❌ No hay ranking global disponible")
        
        # Mostrar análisis por artículo
        if per_article:
            print(f"\n📰 ANÁLISIS POR ARTÍCULO (Top 10):")
            print("-" * 50)
            
            for i, article in enumerate(per_article[:10], 1):
                url = article.get('url', 'N/A')
                title = article.get('title', 'Sin título')
                top_numbers = article.get('top', [])
                
                print(f"🔸 {i:2d}. {title[:60]}...")
                print(f"   🔗 URL: {url[:80]}...")
                
                if top_numbers:
                    print(f"   🎯 Top números:")
                    for j, num_info in enumerate(top_numbers[:3], 1):
                        num = num_info.get('number', 0)
                        score = num_info.get('score', 0.0)
                        label = num_info.get('label', 'N/A')
                        hits = num_info.get('hits', [])
                        print(f"      {j}. {num:2d} ({label}): {score:.3f} - {', '.join(hits[:3])}")
                else:
                    print("   ❌ Sin números atribuidos")
                print("-" * 60)
        else:
            print("❌ No hay análisis por artículo disponible")
        
        # Mostrar auditoría
        print(f"\n📈 AUDITORÍA DEL PASO 5:")
        print("-" * 50)
        print(f"📊 OK: {auditor.get('ok', False)}")
        print(f"📊 Umbral: {auditor.get('threshold', 'N/A')}")
        print(f"📊 Mínimo atribuido: {auditor.get('min_attr', 'N/A')}")
        print(f"📊 Mantenidos arriba del umbral: {auditor.get('kept_above_threshold', 0)}")
        print(f"📊 Total de artículos: {auditor.get('total_articles', 0)}")
        print(f"📊 Razones: {len(auditor.get('reasons', []))}")
        
        # Mostrar razones de rechazo
        reasons = auditor.get('reasons', [])
        if reasons:
            print(f"\n❌ RAZONES DE RECHAZO:")
            print("-" * 50)
            for i, reason in enumerate(reasons[:10], 1):
                url = reason.get('url', 'N/A')
                reason_text = reason.get('reason', 'N/A')
                print(f"   {i}. {url[:60]}... - {reason_text}")
        
        # Análisis de números únicos
        if global_rank:
            print(f"\n🔢 ANÁLISIS DE NÚMEROS ÚNICOS:")
            print("-" * 50)
            
            # Contar repeticiones
            number_counts = {}
            for item in global_rank:
                num = item.get('number', 0)
                score = item.get('score', 0.0)
                if score >= 0.6:  # Solo números arriba del umbral
                    number_counts[num] = number_counts.get(num, 0) + 1
            
            # Mostrar números que se repiten
            if number_counts:
                print("📊 Números que se repiten (arriba del umbral):")
                for num, count in sorted(number_counts.items(), key=lambda x: x[1], reverse=True):
                    if count > 1:
                        print(f"   Número {num:2d}: {count} veces")
                
                # Mostrar números únicos
                unique_numbers = [num for num, count in number_counts.items() if count == 1]
                if unique_numbers:
                    print(f"\n📊 Números únicos (arriba del umbral): {len(unique_numbers)}")
                    print(f"   Números: {', '.join(map(str, sorted(unique_numbers)))}")
            else:
                print("❌ No hay números arriba del umbral")
        
        # Diagnóstico final
        print(f"\n🎯 DIAGNÓSTICO FINAL:")
        print("=" * 80)
        
        if auditor.get('ok', False):
            print("✅ ÉXITO: Paso 5 completado exitosamente")
            print("   - Atribución a Tabla 100 realizada")
            print("   - Números identificados y rankeados")
            print("   - Listo para Paso 6 (Análisis Sefirótico)")
        elif len(global_rank) > 0:
            print("⚠️  PARCIAL: Paso 5 completado con limitaciones")
            print("   - Atribución realizada pero con pocos números")
            print("   - Considerar ajustar umbral o criterios")
        else:
            print("❌ FALLO: Paso 5 no pudo completarse")
            print("   - No se pudieron atribuir números")
            print("   - Revisar noticias y guía")
        
        # Guardar reporte de atribución
        reporte_atribucion = {
            "timestamp": datetime.now().isoformat(),
            "input_news": len(selected_news),
            "status": status,
            "attribution": attribution,
            "auditor": auditor
        }
        
        # Crear directorio reports si no existe
        os.makedirs("reports", exist_ok=True)
        
        # Guardar reporte
        with open("reports/paso5_atribucion_tabla100.json", "w", encoding="utf-8") as f:
            json.dump(reporte_atribucion, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte de atribución guardado en: reports/paso5_atribucion_tabla100.json")
        
        return auditor.get('ok', False)
        
    except Exception as e:
        print(f"❌ Error en Paso 5: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso5_con_25_noticias_seleccionadas()
    if success:
        print("\n🎉 PASO 5 EXITOSO - ATRIBUCIÓN A TABLA 100 COMPLETADA")
    else:
        print("\n💥 PASO 5 FALLÓ - REVISAR NOTICIAS Y GUÍA")




