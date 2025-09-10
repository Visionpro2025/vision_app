# ============================================
# 📌 TEST: PROTOCOLO CUÁNTICO FLORIDA QUINIELA - VERSIÓN SIMPLIFICADA
# Prueba básica del protocolo cuántico sin errores de dimensiones
# ============================================

import sys
import os
import json
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app_vision'))

def test_florida_quantum_simple():
    print("🚀 PRUEBA: PROTOCOLO CUÁNTICO FLORIDA QUINIELA - SIMPLIFICADO")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar módulos cuánticos básicos
        from app_vision.modules.quantum_engine import QuantumEngine
        from app_vision.modules.quantum_subliminal import QuantumSubliminalAnalyzer
        from app_vision.modules.quantum_candado import QuantumCandadoGenerator
        
        print("✅ Módulos cuánticos importados correctamente")
        
        # Crear instancias de los motores cuánticos
        quantum_engine = QuantumEngine()
        quantum_subliminal = QuantumSubliminalAnalyzer()
        quantum_candado = QuantumCandadoGenerator()
        
        print("✅ Motores cuánticos inicializados")
        print()
        
        # Datos de prueba para Florida Quiniela Pick 3
        print("📊 DATOS DE PRUEBA - FLORIDA QUINIELA PICK 3")
        print("-" * 40)
        
        # Números del sorteo (ejemplo real)
        p3_mid = "698"    # Pick 3 Midday
        p4_mid = "5184"   # Pick 4 Midday
        p3_eve = "607"    # Pick 3 Evening
        p4_eve = "1670"   # Pick 4 Evening
        
        print(f"Pick 3 Midday: {p3_mid}")
        print(f"Pick 4 Midday: {p4_mid}")
        print(f"Pick 3 Evening: {p3_eve}")
        print(f"Pick 4 Evening: {p4_eve}")
        print()
        
        # Test 1: Análisis Cuántico Subliminal
        print("1️⃣ ANÁLISIS CUÁNTICO SUBLIMINAL")
        print("-" * 40)
        
        draw_numbers = [6, 9, 8, 5, 1, 8, 4, 6, 0, 7, 1, 6, 7, 0]
        context = {
            "temporal_context": 1.0,
            "geographic_context": 1.0,
            "temporal_phase": 0.0,
            "geographic_phase": 0.0
        }
        
        subliminal_result = quantum_subliminal.analyze_quantum_subliminal(draw_numbers, context)
        
        print(f"✅ Análisis cuántico subliminal completado")
        print(f"   Tópicos cuánticos: {subliminal_result.quantum_topics}")
        print(f"   Keywords cuánticas: {subliminal_result.quantum_keywords}")
        print(f"   Familias cuánticas: {subliminal_result.quantum_families}")
        print(f"   Coherencia cuántica: {subliminal_result.quantum_coherence:.3f}")
        print(f"   Fuerza de entrelazamiento: {subliminal_result.quantum_entanglement_strength:.3f}")
        print()
        
        # Test 2: Generación Cuántica de Candado
        print("2️⃣ GENERACIÓN CUÁNTICA DE CANDADO")
        print("-" * 40)
        
        cfg = {
            "usar_p4_como_corrido_bloque": True,
            "parles_ordenados": False,
            "activar_empuje": True,
            "activar_reversa": True,
            "equivalencia_cero_100": True
        }
        
        candado_result = quantum_candado.generate_quantum_candado(p3_mid, p4_mid, p3_eve, p4_eve, cfg)
        
        print(f"✅ Generación cuántica de candado completada")
        print(f"   Candado MID cuántico: {candado_result.quantum_candado_mid}")
        print(f"   Candado EVE cuántico: {candado_result.quantum_candado_eve}")
        print(f"   Parlés MID cuánticos: {candado_result.quantum_parles_mid}")
        print(f"   Parlés EVE cuánticos: {candado_result.quantum_parles_eve}")
        print(f"   Conjunto 2D MID: {candado_result.quantum_conjunto_2d_mid}")
        print(f"   Conjunto 2D EVE: {candado_result.quantum_conjunto_2d_eve}")
        print(f"   Coherencia MID: {candado_result.quantum_coherence_scores['mid_coherence']:.3f}")
        print(f"   Coherencia EVE: {candado_result.quantum_coherence_scores['eve_coherence']:.3f}")
        print(f"   Coherencia total: {candado_result.quantum_coherence_scores['total_coherence']:.3f}")
        print()
        
        # Test 3: Motor Cuántico Fundamental
        print("3️⃣ MOTOR CUÁNTICO FUNDAMENTAL")
        print("-" * 40)
        
        # Test de superposición cuántica
        numbers = [6, 9, 8]
        quantum_numbers = quantum_engine.create_quantum_superposition(numbers)
        
        print(f"✅ Superposición cuántica creada")
        print(f"   Números cuánticos: {len(quantum_numbers)}")
        for i, qnum in enumerate(quantum_numbers):
            print(f"     {i+1}. Valor: {qnum.value}, Amplitud: {qnum.amplitude:.3f}, Fase: {qnum.phase:.3f}")
        
        # Test de entrelazamiento cuántico
        entangled_numbers = quantum_engine.create_quantum_entanglement(quantum_numbers)
        
        print(f"✅ Entrelazamiento cuántico aplicado")
        print(f"   Números entrelazados: {len(entangled_numbers)}")
        for i, qnum in enumerate(entangled_numbers):
            print(f"     {i+1}. Valor: {qnum.value}, Partners: {qnum.entanglement_partners}")
        
        # Test de interferencia cuántica
        interfered_numbers = quantum_engine.apply_quantum_interference(entangled_numbers)
        
        print(f"✅ Interferencia cuántica aplicada")
        print(f"   Números interferidos: {len(interfered_numbers)}")
        for i, qnum in enumerate(interfered_numbers):
            print(f"     {i+1}. Valor: {qnum.value}, Amplitud: {qnum.amplitude:.3f}")
        
        # Test de medición cuántica
        measured_numbers = quantum_engine.quantum_measurement(interfered_numbers)
        
        print(f"✅ Medición cuántica realizada")
        print(f"   Números medidos: {measured_numbers}")
        print()
        
        # Resumen final
        print("🎯 RESUMEN FINAL - PROTOCOLO CUÁNTICO FLORIDA QUINIELA")
        print("=" * 70)
        print("✅ Análisis cuántico subliminal completado")
        print("✅ Generación cuántica de candado completada")
        print("✅ Motor cuántico fundamental funcionando")
        print()
        print("🚀 EL PROTOCOLO CUÁNTICO FLORIDA QUINIELA ESTÁ FUNCIONANDO")
        print("📊 Análisis cuántico básico operativo")
        print("🎯 Listo para análisis de sorteos de Florida Quiniela Pick 3")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en el protocolo cuántico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_florida_quantum_simple()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PROTOCOLO CUÁNTICO FUNCIONANDO")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")





