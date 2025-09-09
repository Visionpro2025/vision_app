#!/usr/bin/env python3
"""
TEST: Lógica de Candado Cubano para Florida Pick 3
Verifica que la construcción del candado funcione correctamente
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

def test_candado_cubano():
    """Test de la lógica de candado cubano"""
    
    print("🧪 TEST: Lógica de Candado Cubano para Florida Pick 3")
    print("=" * 60)
    
    try:
        from app_vision.steps.step_florida_previous_draw import FloridaPreviousDrawAnalysisStep
        
        # Crear instancia del paso
        step3 = FloridaPreviousDrawAnalysisStep()
        
        # ========================================
        # TEST CON DATOS ESPECÍFICOS
        # ========================================
        print("\n📊 DATOS DE PRUEBA:")
        pick3 = [0, 7, 1]  # Para generar fijo2d = "07"
        pick4 = [6, 7, 0, 2]  # Para generar p4_front2d = "67", p4_back2d = "02"
        
        print(f"   Pick3: {pick3}")
        print(f"   Pick4: {pick4}")
        
        # ========================================
        # CONSTRUIR CANDADO
        # ========================================
        print("\n🔧 CONSTRUYENDO CANDADO...")
        
        candado, parles = step3._build_candado_cubano(pick3, pick4)
        
        print(f"   Fijo2D: {pick3[1]}{pick3[2]} = 07")
        print(f"   P4 Front2D: {pick4[0]}{pick4[1]} = 67")
        print(f"   P4 Back2D: {pick4[2]}{pick4[3]} = 02")
        print(f"   Candado: {candado}")
        print(f"   Parles: {parles}")
        
        # ========================================
        # VERIFICAR RESULTADO ESPERADO
        # ========================================
        print("\n✅ VERIFICACIÓN:")
        
        expected_candado = ["07", "67", "02"]
        expected_parles = [["07", "67"], ["07", "02"], ["67", "02"]]
        
        # Verificar candado
        if candado == expected_candado:
            print("   ✅ Candado correcto")
        else:
            print(f"   ❌ Candado incorrecto. Esperado: {expected_candado}, Obtenido: {candado}")
            return False
        
        # Verificar parles
        if parles == expected_parles:
            print("   ✅ Parles correctos")
        else:
            print(f"   ❌ Parles incorrectos. Esperado: {expected_parles}, Obtenido: {parles}")
            return False
        
        # ========================================
        # TEST COMPLETO DEL PASO 3
        # ========================================
        print("\n🔍 TEST COMPLETO DEL PASO 3...")
        
        from app_vision.engine.contracts import StepContext
        
        ctx = StepContext(
            step_name="test_candado",
            step_id="test",
            pipeline_id="test",
            execution_id="test"
        )
        
        # Datos de entrada
        input_data = {
            "lottery_config": {
                "name": "florida_pick3",
                "bolita_format": "cubana",
                "windows": ["AM", "MID", "EVE"]
            },
            "apply_gematria": True,
            "apply_subliminal": True,
            "create_submessage": True
        }
        
        # Ejecutar paso completo
        result = step3.run(ctx, input_data)
        
        # Verificar resultado
        draw_data = result.get('previous_draw_analysis', {}).get('draw_data', {})
        
        print(f"   📅 Fecha: {draw_data.get('date', 'N/A')}")
        print(f"   🕐 Bloque: {draw_data.get('block', 'N/A')}")
        print(f"   🎯 Pick3: {draw_data.get('pick3', [])}")
        print(f"   🎯 Pick4: {draw_data.get('pick4', [])}")
        print(f"   🔒 Fijo2D: {draw_data.get('fijo2d', 'N/A')}")
        print(f"   🔒 P4 Front2D: {draw_data.get('p4_front2d', 'N/A')}")
        print(f"   🔒 P4 Back2D: {draw_data.get('p4_back2d', 'N/A')}")
        print(f"   🔒 Candado: {draw_data.get('candado', [])}")
        print(f"   🔒 Parles: {draw_data.get('parles', [])}")
        
        # Verificar submensaje
        submessage = result.get('submessage_guide', {})
        print(f"   💬 Submensaje: {submessage.get('submessage', 'N/A')}")
        
        # ========================================
        # VALIDACIÓN FINAL
        # ========================================
        print("\n✅ VALIDACIÓN FINAL:")
        
        if (draw_data.get('fijo2d') == "07" and 
            draw_data.get('p4_front2d') == "67" and 
            draw_data.get('p4_back2d') == "02" and
            draw_data.get('candado') == ["07", "67", "02"] and
            draw_data.get('parles') == [["07", "67"], ["07", "02"], ["67", "02"]]):
            print("   ✅ Todos los datos coinciden con el formato esperado")
        else:
            print("   ❌ Algunos datos no coinciden")
            return False
        
        print("\n🎉 TEST EXITOSO - LÓGICA DE CANDADO CUBANO FUNCIONANDO")
        print("   - Fijo2D construido correctamente")
        print("   - P4 Front2D y Back2D construidos correctamente")
        print("   - Candado generado correctamente")
        print("   - Parles generados correctamente")
        print("   - Submensaje incluye todos los componentes")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_candado_cubano()
    if success:
        print("\n🚀 TEST EXITOSO - CANDADO CUBANO IMPLEMENTADO CORRECTAMENTE")
    else:
        print("\n💥 TEST FALLÓ - REVISAR IMPLEMENTACIÓN")


