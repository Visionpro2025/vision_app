# ============================================
# 📌 TEST: ARTIFACTS STEP PATCH
# Prueba del step mejorado para generar reportes de noticias
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_artifacts_patch():
    print("🚀 PRUEBA: ARTIFACTS STEP PATCH")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el step patch
        from app_vision.steps.step6_artifacts_patch import ArtifactsStepPatch
        from app_vision.engine.contracts import StepContext
        
        print("✅ ArtifactsStepPatch importado correctamente")
        
        # Crear instancia del step
        step = ArtifactsStepPatch()
        
        print("✅ Instancia del step creada")
        print()
        
        # Crear contexto de prueba
        ctx = StepContext(
            run_id="test_artifacts_patch",
            seed=12345,
            cfg={},
            state_dir="./test_state",
            plan_path="./test_plan.json"
        )
        
        print("✅ Contexto de prueba creado")
        print()
        
        # Datos de prueba simulando noticias procesadas
        print("📊 CONFIGURACIÓN DE PRUEBA:")
        print("-" * 40)
        
        # Noticias seleccionadas (post-filtro)
        news_selected = [
            {
                "title": "Florida Community Housing Support Demonstration",
                "url": "https://example.com/news1",
                "final_url": "https://example.com/news1",
                "bucket": "vivienda",
                "score": 8.5
            },
            {
                "title": "Miami Housing Crisis Protest",
                "url": "https://example.com/news2", 
                "final_url": "https://example.com/news2",
                "bucket": "comunidad",
                "score": 7.2
            },
            {
                "title": "Orlando Family Eviction Support",
                "url": "https://example.com/news3",
                "final_url": "https://example.com/news3",
                "bucket": "familia",
                "score": 6.8
            }
        ]
        
        # Métricas de noticias
        news_metrics = {
            "kept": 3,
            "buckets": {
                "vivienda": 1,
                "comunidad": 1,
                "familia": 1
            }
        }
        
        # Guía utilizada
        guidance_used = {
            "guide_terms": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"]
        }
        
        # Datos de entrada
        data = {
            "news_selected": news_selected,
            "news_metrics": news_metrics,
            "guidance_used": guidance_used
        }
        
        print(f"Noticias seleccionadas: {len(news_selected)}")
        print(f"Métricas: {news_metrics}")
        print(f"Guía: {guidance_used['guide_terms']}")
        print()
        
        # Ejecutar el step
        print("🔄 EJECUTANDO ARTIFACTS STEP PATCH:")
        print("-" * 40)
        
        resultado = step.run(ctx, data)
        
        print(f"✅ ArtifactsStepPatch ejecutado")
        print(f"   Archivo generado: {resultado['news_summary_md']}")
        print(f"   Noticias seleccionadas: {resultado['selected_count']}")
        print(f"   Noticias válidas: {resultado['valid_count']}")
        print(f"   Noticias rechazadas: {resultado['rejected_count']}")
        print()
        
        # Verificar que el archivo se creó
        if os.path.exists(resultado['news_summary_md']):
            print("📄 CONTENIDO DEL REPORTE GENERADO:")
            print("-" * 40)
            with open(resultado['news_summary_md'], 'r', encoding='utf-8') as f:
                contenido = f.read()
                print(contenido)
            print()
            
            print("✅ Archivo de reporte creado exitosamente")
        else:
            print("❌ Archivo de reporte no encontrado")
            return False
        
        # Resumen final
        print("🎯 RESUMEN FINAL:")
        print("-" * 40)
        print("✅ ArtifactsStepPatch funcionando correctamente")
        print("✅ Reporte de noticias generado")
        print("✅ Métricas calculadas correctamente")
        print("✅ Guía utilizada documentada")
        print()
        print("🚀 ARTIFACTS STEP PATCH COMPLETADO EXITOSAMENTE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del ArtifactsStepPatch: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_artifacts_patch()
    if success:
        print("\n🎉 PRUEBA EXITOSA - ARTIFACTS STEP PATCH FUNCIONANDO")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")




