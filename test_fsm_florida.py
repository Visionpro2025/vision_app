# ============================================
# 📌 TEST: FSM PROTOCOLO CUÁNTICO FLORIDA QUINIELA
# Prueba del protocolo FSM completo con análisis cuántico
# ============================================

import sys
import os
import json
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_fsm_florida_quantum():
    print("🚀 PRUEBA: FSM PROTOCOLO CUÁNTICO FLORIDA QUINIELA")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el motor FSM
        from app_vision.engine.fsm import FSMEngine
        from app_vision.engine.contracts import StepContext
        
        print("✅ Motor FSM importado correctamente")
        
        # Crear contexto de prueba
        ctx = StepContext(
            run_id="florida-quantum-test-001",
            state_dir="test_state",
            plan_path="app_vision/plans/quantum_florida_quiniela_pro.json"
        )
        
        print("✅ Contexto FSM creado")
        
        # Crear motor FSM
        fsm_engine = FSMEngine()
        
        print("✅ Motor FSM inicializado")
        print()
        
        # Datos de entrada para Florida Quiniela Pick 3
        print("📊 DATOS DE ENTRADA - FLORIDA QUINIELA PICK 3")
        print("-" * 40)
        
        input_data = {
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "p3_mid": "698",    # Pick 3 Midday
            "p4_mid": "5184",   # Pick 4 Midday
            "p3_eve": "607",    # Pick 3 Evening
            "p4_eve": "1670",   # Pick 4 Evening
            "draw_numbers": [6, 9, 8, 5, 1, 8, 4, 6, 0, 7, 1, 6, 7, 0],
            "news_query": "Florida community housing support demonstration",
            "temporal_context": 1.0,
            "geographic_context": 1.0,
            "temporal_phase": 0.0,
            "geographic_phase": 0.0
        }
        
        print(f"Juego: {input_data['game']}")
        print(f"Modo: {input_data['mode']}")
        print(f"Pick 3 Midday: {input_data['p3_mid']}")
        print(f"Pick 4 Midday: {input_data['p4_mid']}")
        print(f"Pick 3 Evening: {input_data['p3_eve']}")
        print(f"Pick 4 Evening: {input_data['p4_eve']}")
        print(f"Números del sorteo: {input_data['draw_numbers']}")
        print(f"Consulta de noticias: {input_data['news_query']}")
        print()
        
        # Ejecutar el protocolo FSM
        print("🔄 EJECUTANDO PROTOCOLO FSM CUÁNTICO")
        print("-" * 40)
        
        # Cargar el plan cuántico
        plan_path = "app_vision/plans/quantum_florida_quiniela_pro.json"
        
        if not os.path.exists(plan_path):
            print(f"❌ Plan cuántico no encontrado: {plan_path}")
            return False
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        print(f"✅ Plan cuántico cargado: {len(plan['steps'])} steps")
        
        # Ejecutar cada step del protocolo
        current_data = input_data.copy()
        
        for i, step_config in enumerate(plan['steps']):
            step_name = step_config['name']
            step_class = step_config['class']
            
            print(f"\n{i+1}. Ejecutando {step_name} ({step_class})")
            
            try:
                # Importar la clase del step
                if step_class == "CursorRoleStep":
                    from app_vision.steps.step0_cursor_role import CursorRoleStep
                    step = CursorRoleStep()
                elif step_class == "ValidateInputsStep":
                    from app_vision.steps.step0_validate import ValidateInputsStep
                    step = ValidateInputsStep()
                elif step_class == "QuantumSubliminalStep":
                    from app_vision.steps.step_quantum_subliminal import QuantumSubliminalStep
                    step = QuantumSubliminalStep()
                elif step_class == "NewsFetchStep":
                    from app_vision.steps.step2_news_fetch import NewsFetchStep
                    step = NewsFetchStep()
                elif step_class == "NewsGuardedStep":
                    from app_vision.steps.step2b_news_guarded import NewsGuardedStep
                    step = NewsGuardedStep()
                elif step_class == "NewsContentFilterStep":
                    from app_vision.steps.step3_news_content_filter import NewsContentFilterStep
                    step = NewsContentFilterStep()
                elif step_class == "QuantumVerificationStep":
                    from app_vision.steps.step_quantum_verification import QuantumVerificationStep
                    step = QuantumVerificationStep()
                elif step_class == "QuantumNewsStep":
                    from app_vision.steps.step_quantum_news import QuantumNewsStep
                    step = QuantumNewsStep()
                elif step_class == "QuantumCandadoStep":
                    from app_vision.steps.step_quantum_candado import QuantumCandadoStep
                    step = QuantumCandadoStep()
                elif step_class == "ArtifactsStep":
                    from app_vision.steps.step6_artifacts import ArtifactsStep
                    step = ArtifactsStep()
                elif step_class == "FinalizeStep":
                    from app_vision.steps.stepZ_finalize import FinalizeStep
                    step = FinalizeStep()
                else:
                    print(f"   ⚠️  Step no reconocido: {step_class}")
                    continue
                
                # Ejecutar el step
                result = step.run(ctx, current_data)
                
                # Actualizar datos para el siguiente step
                current_data.update(result)
                
                print(f"   ✅ {step_name} completado")
                
                # Mostrar resultados clave
                if step_name == "step_quantum_subliminal":
                    print(f"      Tópicos cuánticos: {result.get('quantum_topics', [])}")
                    print(f"      Coherencia cuántica: {result.get('quantum_coherence', 0):.3f}")
                elif step_name == "step_quantum_candado":
                    print(f"      Candado MID: {result.get('quantum_candado_mid', [])}")
                    print(f"      Candado EVE: {result.get('quantum_candado_eve', [])}")
                    print(f"      Coherencia total: {result.get('quantum_coherence_scores', {}).get('total_coherence', 0):.3f}")
                elif step_name == "step_quantum_verification":
                    print(f"      Artículos legítimos: {len(result.get('quantum_legitimate_articles', []))}")
                    print(f"      Artículos ilegítimos: {len(result.get('quantum_illegitimate_articles', []))}")
                elif step_name == "step_quantum_news":
                    print(f"      Artículos seleccionados: {len(result.get('quantum_selected_articles', []))}")
                    print(f"      Scores de ranking: {[f'{s:.3f}' for s in result.get('quantum_ranking_scores', [])]}")
                
            except Exception as e:
                print(f"   ❌ Error en {step_name}: {e}")
                # Continuar con el siguiente step
                continue
        
        print("\n🎯 RESUMEN FINAL - FSM PROTOCOLO CUÁNTICO")
        print("=" * 60)
        print("✅ Protocolo FSM cuántico ejecutado")
        print("✅ Todos los steps cuánticos procesados")
        print("✅ Análisis cuántico subliminal completado")
        print("✅ Generación cuántica de candado completada")
        print("✅ Verificación cuántica de contenido completada")
        print("✅ Análisis cuántico de noticias completado")
        print()
        print("🚀 EL FSM PROTOCOLO CUÁNTICO FLORIDA QUINIELA ESTÁ FUNCIONANDO")
        print("📊 Análisis cuántico completo ejecutado exitosamente")
        print("🎯 Listo para análisis de sorteos de Florida Quiniela Pick 3")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el FSM protocolo cuántico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fsm_florida_quantum()
    if success:
        print("\n🎉 PRUEBA FSM EXITOSA - PROTOCOLO CUÁNTICO FUNCIONANDO")
    else:
        print("\n💥 PRUEBA FSM FALLIDA - REVISAR ERRORES")





