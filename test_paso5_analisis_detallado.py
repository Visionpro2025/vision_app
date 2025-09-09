# ============================================
# 📌 TEST: ANÁLISIS DETALLADO - NOTICIAS Y NÚMEROS TABLA 100
# Muestra las noticias y sus números equivalentes con conteo de repeticiones
# ============================================

import sys
import os
from datetime import datetime
from collections import Counter

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_analisis_detallado_noticias_numeros():
    print("🚀 ANÁLISIS DETALLADO: NOTICIAS Y NÚMEROS TABLA 100")
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
            run_id="test-analisis-detallado",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Simular las noticias reales del día (basadas en el test anterior)
        selected_news = []
        
        # Generar noticias principales (98) con temas variados
        temas_principales = [
            "Supreme Court Decision on Property Rights",
            "Community Health Center Opens New Portal", 
            "Union Agreement Reached After Long Negotiations",
            "Family Crisis Support Program Launched",
            "Spiritual Center Offers Community Services",
            "Economic Stability Measures Announced",
            "Housing Crisis Response Initiative",
            "Educational Reform Program",
            "Healthcare Access Improvement",
            "Community Safety Initiative"
        ]
        
        for i in range(1, 99):
            tema = temas_principales[i % len(temas_principales)]
            selected_news.append({
                "title": f"{tema} - Update {i}",
                "final_url": f"https://example.com/noticia-principal-{i}",
                "text": f"Contenido de la noticia principal número {i} sobre {tema.lower()}. Esta noticia contiene información importante sobre eventos que están ocurriendo en la sociedad y afectan a la comunidad.",
                "bucket": f"tema_{i % 10}",
                "score": 0.5 + (i % 50) * 0.01
            })
        
        # Generar noticias emocionales (14) con temas específicos
        temas_emocionales = [
            "Crisis Familiar en la Comunidad",
            "Apoyo a Familias en Dificultades", 
            "Programa de Ayuda Comunitaria",
            "Centro de Salud Mental Abre",
            "Iniciativa de Voluntariado",
            "Apoyo a Refugiados",
            "Crisis de Vivienda",
            "Programa de Empleo",
            "Centro Espiritual de Ayuda",
            "Iniciativa de Solidaridad",
            "Apoyo a Migrantes",
            "Crisis Económica Familiar",
            "Programa de Educación",
            "Centro de Crisis Comunitaria"
        ]
        
        for i, tema in enumerate(temas_emocionales):
            selected_news.append({
                "title": tema,
                "final_url": f"https://example.com/noticia-emocional-{i+1}",
                "text": f"Noticia emocional sobre {tema.lower()}. Esta noticia trata sobre temas sociales y emocionales que afectan a la comunidad. Contiene información sobre ayuda, solidaridad, crisis y apoyo mutuo para las familias.",
                "bucket": "emocional",
                "score": 0.7 + (i % 30) * 0.01
            })
        
        # Guía del análisis subliminal (Paso 3)
        guidance = {
            "topics": ["veredicto", "decisión", "propiedad", "refugio", "hogar", "cirugía"],
            "keywords": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"],
            "families": ["corte", "casa"]
        }
        
        print("📊 CONFIGURACIÓN DEL ANÁLISIS DETALLADO:")
        print("-" * 50)
        print(f"Noticias principales: 98")
        print(f"Noticias emocionales: 14")
        print(f"Total de noticias: {len(selected_news)}")
        print()
        
        # Crear instancia del step
        step = NewsAttributionTable100Step()
        
        # Datos de entrada
        data = {
            "selected_news": selected_news,
            "guidance": guidance,
            "min_attr": 5,
            "threshold": 0.4
        }
        
        print("🔄 EJECUTANDO ANÁLISIS DETALLADO:")
        print("-" * 50)
        
        # Ejecutar el step
        resultado = step.run(ctx, data)
        
        print(f"✅ Análisis detallado ejecutado con {len(selected_news)} noticias")
        print(f"   Estado: {resultado['status']}")
        print()
        
        # Mostrar análisis detallado
        if 'attribution' in resultado:
            attribution = resultado['attribution']
            
            print("📊 ANÁLISIS DETALLADO: NOTICIAS Y NÚMEROS TABLA 100")
            print("=" * 80)
            
            # Obtener la tabla 100 para mostrar significados
            from app_vision.modules.table100_universal import build_table100
            table_100 = build_table100()
            
            # Análisis por artículo con números
            print("📰 NOTICIAS Y SUS NÚMEROS EQUIVALENTES:")
            print("=" * 80)
            
            per_article = attribution.get('per_article', [])
            todos_los_numeros = []
            
            for i, article in enumerate(per_article, 1):
                print(f"\n🔸 NOTICIA {i}: {article['title']}")
                print(f"   URL: {article['url']}")
                
                if article.get('top'):
                    print("   📊 NÚMEROS EQUIVALENTES EN TABLA 100:")
                    for j, top_item in enumerate(article['top'], 1):
                        numero = top_item['number']
                        score = top_item['score']
                        label = top_item['label']
                        hits = top_item['hits']
                        
                        # Obtener significado completo de la tabla
                        significado = table_100.get(numero, {}).get('meaning', 'N/A')
                        
                        print(f"      {j}. Número {numero:2d}: {label}")
                        print(f"         Score: {score:.3f}")
                        print(f"         Significado: {significado}")
                        print(f"         Keywords encontradas: {', '.join(hits[:5])}")
                        
                        # Agregar a la lista para conteo
                        todos_los_numeros.append(numero)
                else:
                    print("   ⚠️  No se encontraron correlaciones")
                print("-" * 60)
            
            # Análisis de repeticiones
            print("\n🔢 ANÁLISIS DE REPETICIONES DE NÚMEROS:")
            print("=" * 80)
            
            if todos_los_numeros:
                contador = Counter(todos_los_numeros)
                numeros_ordenados = contador.most_common()
                
                print(f"Total de números encontrados: {len(todos_los_numeros)}")
                print(f"Números únicos: {len(contador)}")
                print()
                
                print("📊 RANKING POR FRECUENCIA:")
                print("-" * 40)
                for i, (numero, repeticiones) in enumerate(numeros_ordenados, 1):
                    significado = table_100.get(numero, {}).get('meaning', 'N/A')
                    label = table_100.get(numero, {}).get('label', 'N/A')
                    
                    print(f"{i:2d}. Número {numero:2d}: {label}")
                    print(f"    Repeticiones: {repeticiones}")
                    print(f"    Significado: {significado}")
                    print()
            else:
                print("❌ No se encontraron números para analizar")
            
            # Ranking global
            print("\n🏆 RANKING GLOBAL DE NÚMEROS:")
            print("=" * 80)
            global_rank = attribution.get('global_rank', [])
            if global_rank:
                print("Top 15 números más relevantes del día:")
                print("-" * 40)
                for i, item in enumerate(global_rank[:15], 1):
                    numero = item['number']
                    score = item['score']
                    label = item['label']
                    significado = item['meaning']
                    
                    # Contar repeticiones
                    repeticiones = contador.get(numero, 0) if 'contador' in locals() else 0
                    
                    print(f"{i:2d}. Número {numero:2d}: {label}")
                    print(f"    Score global: {score:.3f}")
                    print(f"    Repeticiones: {repeticiones}")
                    print(f"    Significado: {significado}")
                    print()
            else:
                print("❌ No hay ranking global disponible")
            
            # Resumen estadístico
            print("\n📈 RESUMEN ESTADÍSTICO:")
            print("=" * 80)
            if 'contador' in locals():
                print(f"Total de números encontrados: {len(todos_los_numeros)}")
                print(f"Números únicos: {len(contador)}")
                print(f"Número más repetido: {contador.most_common(1)[0][0]} ({contador.most_common(1)[0][1]} veces)")
                print(f"Promedio de repeticiones por número: {len(todos_los_numeros) / len(contador):.2f}")
                
                # Números con más de 1 repetición
                numeros_multiples = [(n, r) for n, r in contador.items() if r > 1]
                if numeros_multiples:
                    print(f"Números con múltiples repeticiones: {len(numeros_multiples)}")
                    print("Números más repetidos:")
                    for numero, repeticiones in sorted(numeros_multiples, key=lambda x: x[1], reverse=True)[:10]:
                        label = table_100.get(numero, {}).get('label', 'N/A')
                        print(f"  - Número {numero:2d}: {label} ({repeticiones} veces)")
                else:
                    print("Todos los números aparecen solo una vez")
            
        else:
            print("❌ No se encontró información de atribución en el resultado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el análisis detallado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_analisis_detallado_noticias_numeros()
    if success:
        print("\n🎉 ANÁLISIS DETALLADO COMPLETADO EXITOSAMENTE")
    else:
        print("\n💥 ANÁLISIS DETALLADO FALLIDO - REVISAR ERRORES")




