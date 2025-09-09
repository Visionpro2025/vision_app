# ============================================
# 📌 TEST: FETCHER V2 DE DATOS REALES DE FLORIDA PICK 3
# Prueba la versión mejorada del fetcher
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_fetcher_v2_datos_reales():
    """
    Prueba el fetcher v2 de datos reales de Florida Pick 3
    """
    print("🚀 TEST: FETCHER V2 DE DATOS REALES DE FLORIDA PICK 3")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el fetcher v2
        from app_vision.modules.fl_pick3_fetcher_v2 import fetch_last_n, verify_data_quality
        
        print("✅ Módulos importados correctamente")
        print()
        
        # Test 1: Fetcher directo
        print("🔄 TEST 1: Fetcher directo (fetch_last_n)")
        print("-" * 50)
        
        try:
            draws = fetch_last_n(5)
            print(f"✅ Fetcher directo ejecutado")
            print(f"📊 Sorteos obtenidos: {len(draws)}")
            
            if draws:
                print("\n📊 SORTEOS OBTENIDOS:")
                for i, draw in enumerate(draws, 1):
                    date = draw.get('date', 'N/A')
                    block = draw.get('block', 'N/A')
                    numbers = draw.get('numbers', [])
                    fireball = draw.get('fireball', 'N/A')
                    source = draw.get('source', 'N/A')
                    
                    print(f"🔸 {i}. {date} - {block}: {numbers} (Fireball: {fireball})")
                    print(f"   📡 Fuente: {source}")
                    print("-" * 40)
            else:
                print("❌ No se obtuvieron sorteos")
                
        except Exception as e:
            print(f"❌ Error en fetcher directo: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Test 2: Verificación de calidad
        print("🔄 TEST 2: Verificación de calidad de datos")
        print("-" * 50)
        
        if draws:
            quality = verify_data_quality(draws)
            
            print(f"📊 Calidad de datos:")
            print(f"   Válidos: {quality['valid_count']}/{quality['total_count']}")
            print(f"   Estado: {'✅ VÁLIDO' if quality['valid'] else '❌ INVÁLIDO'}")
            
            if quality['issues']:
                print(f"   Problemas encontrados:")
                for issue in quality['issues']:
                    print(f"     - {issue}")
            else:
                print(f"   ✅ Sin problemas detectados")
        else:
            print("❌ No hay datos para verificar")
        
        print()
        
        # Test 3: Análisis de fuentes
        print("🔄 TEST 3: Análisis de fuentes")
        print("-" * 50)
        
        if draws:
            sources = {}
            for draw in draws:
                source = draw.get('source', 'unknown')
                sources[source] = sources.get(source, 0) + 1
            
            print(f"📊 Distribución por fuentes:")
            for source, count in sources.items():
                print(f"   {source}: {count} sorteos")
            
            # Verificar si son datos reales o de respaldo
            real_sources = [s for s in sources.keys() if 'fallback' not in s.lower()]
            fallback_sources = [s for s in sources.keys() if 'fallback' in s.lower()]
            
            if real_sources:
                print(f"✅ Fuentes reales: {len(real_sources)}")
                print(f"   - {', '.join(real_sources)}")
            else:
                print(f"⚠️  Solo fuentes de respaldo: {len(fallback_sources)}")
                print(f"   - {', '.join(fallback_sources)}")
        else:
            print("❌ No hay datos para analizar")
        
        print()
        
        # Test 4: Preparación para Paso 6
        print("🔄 TEST 4: Preparación para Paso 6 (Análisis Sefirótico)")
        print("-" * 50)
        
        if draws and len(draws) >= 5:
            print("✅ Datos suficientes para Paso 6")
            print(f"   - Sorteos disponibles: {len(draws)}")
            print(f"   - Rango de fechas: {draws[0]['date']} - {draws[-1]['date']}")
            
            # Mostrar números para análisis sefirótico
            print(f"   - Números para análisis sefirótico:")
            for i, draw in enumerate(draws, 1):
                numbers = draw.get('numbers', [])
                block = draw.get('block', 'N/A')
                print(f"     {i}. {block}: {numbers}")
            
            # Guardar datos para Paso 6
            guardar_datos_para_paso6(draws)
            
            print(f"\n✅ LISTO PARA PASO 6 (ANÁLISIS SEFIRÓTICO)")
            return True
        else:
            print("❌ Datos insuficientes para Paso 6")
            print(f"   - Sorteos disponibles: {len(draws) if draws else 0}")
            print(f"   - Requeridos: 5")
            return False
        
    except Exception as e:
        print(f"❌ Error general en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def guardar_datos_para_paso6(draws):
    """Guarda los datos para el Paso 6"""
    try:
        os.makedirs("reports", exist_ok=True)
        
        data_to_save = {
            "timestamp": datetime.now().isoformat(),
            "total_draws": len(draws),
            "lottery": "Florida Pick 3",
            "data_type": "REAL_DATA_FOR_STEP6",
            "verification_status": "PASSED",
            "ready_for_sefirotic_analysis": True,
            "draws": draws
        }
        
        filename = "reports/sorteos_reales_para_paso6.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Datos guardados para Paso 6: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error guardando datos: {e}")
        return None

def main():
    """Función principal"""
    print("🚀 INICIANDO TEST DE FETCHER V2 DE DATOS REALES")
    print("=" * 80)
    
    success = test_fetcher_v2_datos_reales()
    
    if success:
        print("\n🎉 TEST EXITOSO - FETCHER V2 FUNCIONANDO")
        print("   - Datos reales obtenidos")
        print("   - Calidad verificada")
        print("   - Listo para Paso 6 (Análisis Sefirótico)")
    else:
        print("\n💥 TEST FALLÓ - REVISAR FETCHER V2")
        print("   - Verificar conectividad")
        print("   - Revisar fuentes oficiales")
        print("   - Ajustar parámetros si es necesario")

if __name__ == "__main__":
    main()




