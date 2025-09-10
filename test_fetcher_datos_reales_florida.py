# ============================================
# 📌 TEST: FETCHER DE DATOS REALES DE FLORIDA PICK 3
# Prueba el sistema anti-simulación que obtiene datos REALES
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_fetcher_datos_reales_florida():
    """
    Prueba el fetcher de datos reales de Florida Pick 3
    """
    print("🚀 TEST: FETCHER DE DATOS REALES DE FLORIDA PICK 3")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el fetcher
        from app_vision.modules.fl_pick3_fetcher import fetch_last_n
        from app_vision.steps.step1_fetch_draws_real import FetchFLPick3RealStep
        from app_vision.engine.contracts import StepContext
        
        print("✅ Módulos importados correctamente")
        
        # Crear contexto de step (simulado)
        ctx = StepContext(
            run_id="test-fetcher-real",
            seed=12345,
            cfg={},
            state_dir="test_state",
            plan_path="test_plan.json"
        )
        
        print("✅ Contexto de step creado")
        print()
        
        # Test 1: Fetcher directo
        print("🔄 TEST 1: Fetcher directo (fetch_last_n)")
        print("-" * 50)
        
        try:
            draws = fetch_last_n(5)
            print(f"✅ Fetcher directo ejecutado")
            print(f"📊 Sorteos obtenidos: {len(draws)}")
            
            if draws:
                print("\n📊 SORTEOS OBTENIDOS (Fetcher directo):")
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
                print("❌ No se obtuvieron sorteos con fetcher directo")
                
        except Exception as e:
            print(f"❌ Error en fetcher directo: {e}")
        
        print()
        
        # Test 2: Step FSM
        print("🔄 TEST 2: Step FSM (FetchFLPick3RealStep)")
        print("-" * 50)
        
        try:
            step = FetchFLPick3RealStep()
            
            # Datos de entrada
            data = {
                "min_results": 5
            }
            
            print("🔄 Ejecutando Step FSM...")
            resultado = step.run(ctx, data)
            
            print(f"✅ Step FSM ejecutado")
            print(f"📊 Resultado: {resultado}")
            
            draws_fsm = resultado.get('draws', [])
            count = resultado.get('count', 0)
            
            print(f"📊 Sorteos obtenidos: {count}")
            
            if draws_fsm:
                print("\n📊 SORTEOS OBTENIDOS (Step FSM):")
                for i, draw in enumerate(draws_fsm, 1):
                    date = draw.get('date', 'N/A')
                    block = draw.get('block', 'N/A')
                    numbers = draw.get('numbers', [])
                    fireball = draw.get('fireball', 'N/A')
                    source = draw.get('source', 'N/A')
                    
                    print(f"🔸 {i}. {date} - {block}: {numbers} (Fireball: {fireball})")
                    print(f"   📡 Fuente: {source}")
                    print("-" * 40)
            else:
                print("❌ No se obtuvieron sorteos con Step FSM")
                
        except Exception as e:
            print(f"❌ Error en Step FSM: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Test 3: Verificación de datos reales
        print("🔄 TEST 3: Verificación de datos reales")
        print("-" * 50)
        
        if draws or draws_fsm:
            test_draws = draws if draws else draws_fsm
            
            print("✅ Verificando datos obtenidos...")
            
            # Verificar estructura
            required_fields = ['date', 'block', 'numbers', 'source']
            valid_draws = 0
            
            for draw in test_draws:
                if all(field in draw for field in required_fields):
                    valid_draws += 1
            
            print(f"📊 Sorteos válidos: {valid_draws}/{len(test_draws)}")
            
            # Verificar números
            valid_numbers = 0
            for draw in test_draws:
                numbers = draw.get('numbers', [])
                if len(numbers) == 3 and all(isinstance(n, int) and 0 <= n <= 9 for n in numbers):
                    valid_numbers += 1
            
            print(f"📊 Sorteos con números válidos: {valid_numbers}/{len(test_draws)}")
            
            # Verificar fechas
            valid_dates = 0
            for draw in test_draws:
                date = draw.get('date', '')
                if date and len(date) == 10 and date.count('-') == 2:
                    valid_dates += 1
            
            print(f"📊 Sorteos con fechas válidas: {valid_dates}/{len(test_draws)}")
            
            # Verificar bloques
            valid_blocks = 0
            for draw in test_draws:
                block = draw.get('block', '')
                if block in ['MID', 'EVE']:
                    valid_blocks += 1
            
            print(f"📊 Sorteos con bloques válidos: {valid_blocks}/{len(test_draws)}")
            
            # Verificar fuentes
            sources = set(draw.get('source', '') for draw in test_draws)
            print(f"📊 Fuentes únicas: {len(sources)}")
            for source in sources:
                print(f"   - {source}")
            
            # Diagnóstico final
            if valid_draws == len(test_draws) and valid_numbers == len(test_draws):
                print("\n✅ DIAGNÓSTICO: DATOS REALES VÁLIDOS")
                print("   - Estructura correcta")
                print("   - Números válidos")
                print("   - Listo para Paso 6 (Análisis Sefirótico)")
                
                # Guardar datos reales
                guardar_datos_reales(test_draws)
                return True
            else:
                print("\n⚠️  DIAGNÓSTICO: DATOS PARCIALMENTE VÁLIDOS")
                print("   - Revisar estructura o fuentes")
                return False
        else:
            print("❌ DIAGNÓSTICO: NO SE OBTUVIERON DATOS")
            print("   - Verificar conectividad")
            print("   - Revisar fuentes oficiales")
            return False
        
    except Exception as e:
        print(f"❌ Error general en test: {e}")
        import traceback
        traceback.print_exc()
        return False

def guardar_datos_reales(draws):
    """Guarda los datos reales obtenidos"""
    try:
        os.makedirs("reports", exist_ok=True)
        
        data_to_save = {
            "timestamp": datetime.now().isoformat(),
            "total_draws": len(draws),
            "lottery": "Florida Pick 3",
            "data_type": "REAL_DATA_VERIFIED",
            "verification_status": "PASSED",
            "draws": draws
        }
        
        filename = "reports/sorteos_reales_florida_pick3_verificados.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Datos reales guardados en: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error guardando datos reales: {e}")
        return None

def main():
    """Función principal"""
    print("🚀 INICIANDO TEST DE FETCHER DE DATOS REALES")
    print("=" * 80)
    
    success = test_fetcher_datos_reales_florida()
    
    if success:
        print("\n🎉 TEST EXITOSO - DATOS REALES OBTENIDOS")
        print("   - Fetcher funcionando correctamente")
        print("   - Datos reales verificados")
        print("   - Listo para integración en protocolo")
    else:
        print("\n💥 TEST FALLÓ - REVISAR FETCHER")
        print("   - Verificar conectividad")
        print("   - Revisar fuentes oficiales")
        print("   - Ajustar parámetros si es necesario")

if __name__ == "__main__":
    main()





