# ============================================
# 📌 TEST: PASO 7 - GENERACIÓN DE SERIES CUÁNTICAS
# Combina candidatos sefiróticos y números de Tabla 100 para generar series
# ============================================

import sys
import os
from datetime import datetime
import json
import random
import math

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso7_series_cuanticas():
    """
    Ejecuta el Paso 7: Generación de Series Cuánticas
    """
    print("🚀 PASO 7: GENERACIÓN DE SERIES CUÁNTICAS")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Cargar resultados del Paso 6 (Análisis Sefirótico)
        try:
            with open("reports/paso6_sefirotico_v2.json", "r", encoding="utf-8") as f:
                paso6_data = json.load(f)
            
            sefirotic_candidates = paso6_data.get('candidates', {})
            sefirah_scores = paso6_data.get('sefirah_scores', {})
            digit_scores = paso6_data.get('digit_scores', {})
            
            print("✅ Datos del Paso 6 (Sefirótico) cargados")
            print(f"   Candidatos sefiróticos: {sefirotic_candidates}")
            
        except FileNotFoundError:
            print("❌ No se encontró el archivo del Paso 6")
            print("   Usando datos de prueba...")
            sefirotic_candidates = {
                "alta": [3, 8, 2, 1, 7, 4],
                "media": [6, 9],
                "baja": [5]
            }
            sefirah_scores = {
                "Jésed": 1.000,
                "Yesod": 0.911,
                "Biná": 0.906,
                "Jojmá": 0.899,
                "Hod": 0.849
            }
            digit_scores = {
                3: 1.000, 8: 0.911, 2: 0.906, 1: 0.899, 7: 0.849
            }
        
        # Cargar resultados del Paso 5 (Tabla 100)
        try:
            with open("reports/paso5_atribucion_tabla100.json", "r", encoding="utf-8") as f:
                paso5_data = json.load(f)
            
            table100_numbers = paso5_data.get('attribution', {}).get('global_rank', [])
            
            print("✅ Datos del Paso 5 (Tabla 100) cargados")
            print(f"   Números de Tabla 100: {len(table100_numbers)}")
            
        except FileNotFoundError:
            print("❌ No se encontró el archivo del Paso 5")
            print("   Usando datos de prueba...")
            table100_numbers = [
                {"number": 69, "score": 1.030, "label": "responsabilidad-humanidad"},
                {"number": 96, "score": 1.030, "label": "humanidad-responsabilidad"},
                {"number": 49, "score": 0.883, "label": "estabilidad-humanidad"},
                {"number": 89, "score": 0.883, "label": "poder-humanidad"},
                {"number": 94, "score": 0.883, "label": "humanidad-estabilidad"},
                {"number": 91, "score": 0.849, "label": "humanidad-inicio"},
                {"number": 61, "score": 0.679, "label": "responsabilidad-inicio"}
            ]
        
        # Cargar resultados del Paso 3 (Subliminal)
        try:
            with open("reports/paso3_subliminal_v2.json", "r", encoding="utf-8") as f:
                paso3_data = json.load(f)
            
            subliminal_guidance = paso3_data.get('submensaje_guia', {})
            
            print("✅ Datos del Paso 3 (Subliminal) cargados")
            
        except FileNotFoundError:
            print("❌ No se encontró el archivo del Paso 3")
            print("   Usando datos de prueba...")
            subliminal_guidance = {
                "topics": ["crisis", "familia", "comunidad"],
                "keywords": ["ayuda", "solidaridad", "refugio"],
                "families": ["justicia", "derechos", "comunidad"]
            }
        
        print()
        
        # Ejecutar el Paso 7
        print("🔄 EJECUTANDO PASO 7 - GENERACIÓN DE SERIES CUÁNTICAS:")
        print("-" * 50)
        
        try:
            # Generar series cuánticas
            quantum_series = generar_series_cuanticas(
                sefirotic_candidates,
                table100_numbers,
                subliminal_guidance
            )
            
            print(f"✅ Paso 7 ejecutado")
            print(f"📊 Series generadas: {len(quantum_series.get('series', []))}")
            print()
            
            # Mostrar resultados detallados
            mostrar_resultados_paso7(quantum_series)
            
            # Guardar resultados
            guardar_resultados_paso7(quantum_series)
            
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando Paso 7: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Error general en Paso 7: {e}")
        import traceback
        traceback.print_exc()
        return False

def generar_series_cuanticas(sefirotic_candidates, table100_numbers, subliminal_guidance):
    """
    Genera series cuánticas combinando candidatos sefiróticos y números de Tabla 100
    """
    print("🔮 Generando series cuánticas...")
    
    # Extraer números de alta energía del análisis sefirótico
    alta_energia = sefirotic_candidates.get('alta', [])
    media_energia = sefirotic_candidates.get('media', [])
    baja_energia = sefirotic_candidates.get('baja', [])
    
    # Extraer números de Tabla 100 (convertir a dígitos 0-9)
    table100_digits = []
    for item in table100_numbers:
        number = item.get('number', 0)
        score = item.get('score', 0.0)
        if score >= 0.6:  # Solo números con alta correlación
            # Convertir número a dígitos individuales
            digits = [int(d) for d in str(number) if d.isdigit()]
            table100_digits.extend(digits)
    
    # Eliminar duplicados y mantener solo dígitos 0-9
    table100_digits = list(set([d for d in table100_digits if 0 <= d <= 9]))
    
    print(f"   Dígitos de alta energía: {alta_energia}")
    print(f"   Dígitos de Tabla 100: {table100_digits}")
    
    # Generar 10 series cuánticas distintas
    series = []
    for i in range(10):
        serie = generar_serie_cuantica_individual(
            alta_energia, media_energia, baja_energia, table100_digits, i
        )
        series.append(serie)
    
    # Crear configuraciones de series sugeridas
    suggested_configs = crear_configuraciones_sugeridas(series)
    
    # Aplicar filtros de coherencia cuántica
    filtered_series = aplicar_filtros_coherencia(series)
    
    # Validar con auditor
    auditor_validation = validar_series_cuanticas(filtered_series)
    
    return {
        "status": "completed",
        "quantum_series": filtered_series,
        "suggested_configs": suggested_configs,
        "auditor_validation": auditor_validation,
        "metadata": {
            "total_series": len(filtered_series),
            "sefirotic_candidates_used": sefirotic_candidates,
            "table100_digits_used": table100_digits,
            "subliminal_guidance_used": subliminal_guidance,
            "timestamp": datetime.now().isoformat()
        }
    }

def generar_serie_cuantica_individual(alta_energia, media_energia, baja_energia, table100_digits, seed):
    """
    Genera una serie cuántica individual
    """
    random.seed(seed + 12345)  # Semilla determinística
    
    # Combinar todas las fuentes de números
    all_digits = list(set(alta_energia + media_energia + table100_digits))
    
    if len(all_digits) < 3:
        # Si no hay suficientes dígitos, usar todos los dígitos 0-9
        all_digits = list(range(10))
    
    # Generar 3 números para la serie
    serie_numbers = []
    for _ in range(3):
        # Ponderar por energía (alta energía tiene más probabilidad)
        weights = []
        for digit in all_digits:
            if digit in alta_energia:
                weights.append(0.5)  # 50% de probabilidad
            elif digit in media_energia:
                weights.append(0.3)  # 30% de probabilidad
            elif digit in table100_digits:
                weights.append(0.4)  # 40% de probabilidad
            else:
                weights.append(0.1)  # 10% de probabilidad
        
        # Normalizar pesos
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(all_digits)] * len(all_digits)
        
        # Seleccionar dígito ponderado
        selected_digit = random.choices(all_digits, weights=weights)[0]
        serie_numbers.append(selected_digit)
    
    # Calcular propiedades cuánticas
    quantum_properties = calcular_propiedades_cuanticas(serie_numbers)
    
    return {
        "id": f"QS-{seed+1:03d}",
        "numbers": serie_numbers,
        "quantum_properties": quantum_properties,
        "energy_level": calcular_nivel_energia(serie_numbers, alta_energia, media_energia),
        "coherence_score": calcular_coherencia(serie_numbers),
        "generation_method": "quantum_hybrid"
    }

def calcular_propiedades_cuanticas(numbers):
    """Calcula propiedades cuánticas de la serie"""
    if len(numbers) != 3:
        return {}
    
    a, b, c = numbers
    
    # Suma cuántica
    quantum_sum = a + b + c
    
    # Producto cuántico
    quantum_product = a * b * c
    
    # Entropía cuántica (medida de aleatoriedad)
    entropy = -sum(p * math.log2(p) for p in [numbers.count(x)/3 for x in set(numbers)] if p > 0)
    
    # Coherencia cuántica (medida de patrón)
    coherence = 1.0 - abs(a - b) / 9.0 - abs(b - c) / 9.0 - abs(a - c) / 9.0
    
    return {
        "quantum_sum": quantum_sum,
        "quantum_product": quantum_product,
        "entropy": round(entropy, 3),
        "coherence": round(coherence, 3),
        "variance": round(sum((x - sum(numbers)/3)**2 for x in numbers) / 3, 3)
    }

def calcular_nivel_energia(numbers, alta_energia, media_energia):
    """Calcula el nivel de energía de la serie"""
    alta_count = sum(1 for n in numbers if n in alta_energia)
    media_count = sum(1 for n in numbers if n in media_energia)
    
    if alta_count >= 2:
        return "alta"
    elif alta_count >= 1 or media_count >= 2:
        return "media"
    else:
        return "baja"

def calcular_coherencia(numbers):
    """Calcula la coherencia de la serie"""
    if len(numbers) != 3:
        return 0.0
    
    # Coherencia basada en patrones
    a, b, c = numbers
    
    # Patrón de secuencia
    if abs(a - b) == 1 and abs(b - c) == 1:
        return 1.0
    
    # Patrón de repetición
    if a == b or b == c or a == c:
        return 0.8
    
    # Patrón de simetría
    if a + c == 2 * b:
        return 0.6
    
    # Coherencia base
    return 0.4

def crear_configuraciones_sugeridas(series):
    """Crea configuraciones sugeridas de series"""
    # Ordenar por coherencia
    sorted_series = sorted(series, key=lambda x: x['coherence_score'], reverse=True)
    
    configs = []
    
    # Configuración 1: Máxima coherencia
    configs.append({
        "name": "Máxima Coherencia",
        "description": "Series con mayor coherencia cuántica",
        "series": sorted_series[:3],
        "priority": "high"
    })
    
    # Configuración 2: Alta energía
    high_energy_series = [s for s in series if s['energy_level'] == 'alta']
    if high_energy_series:
        configs.append({
            "name": "Alta Energía",
            "description": "Series con mayor nivel de energía",
            "series": high_energy_series[:3],
            "priority": "high"
        })
    
    # Configuración 3: Equilibrio cuántico
    balanced_series = [s for s in series if 0.5 <= s['coherence_score'] <= 0.8]
    if balanced_series:
        configs.append({
            "name": "Equilibrio Cuántico",
            "description": "Series con equilibrio entre coherencia y energía",
            "series": balanced_series[:3],
            "priority": "medium"
        })
    
    # Configuración 4: Diversidad cuántica
    diverse_series = series[::2]  # Tomar cada segunda serie para diversidad
    configs.append({
        "name": "Diversidad Cuántica",
        "description": "Series con máxima diversidad",
        "series": diverse_series[:3],
        "priority": "medium"
    })
    
    return configs

def aplicar_filtros_coherencia(series):
    """Aplica filtros de coherencia cuántica"""
    filtered = []
    
    for serie in series:
        # Filtro 1: Coherencia mínima
        if serie['coherence_score'] >= 0.3:
            # Filtro 2: Propiedades cuánticas válidas
            props = serie['quantum_properties']
            if props.get('entropy', 0) >= 0.5:  # Entropía mínima
                # Filtro 3: Variación mínima
                if props.get('variance', 0) >= 0.1:
                    filtered.append(serie)
    
    return filtered

def validar_series_cuanticas(series):
    """Valida las series cuánticas generadas"""
    if not series:
        return {
            "valid": False,
            "error": "No se generaron series válidas",
            "count": 0
        }
    
    valid_count = 0
    issues = []
    
    for i, serie in enumerate(series):
        # Validar estructura
        if not all(key in serie for key in ['numbers', 'coherence_score', 'energy_level']):
            issues.append(f"Serie {i+1}: Estructura incompleta")
            continue
        
        # Validar números
        numbers = serie['numbers']
        if len(numbers) != 3 or not all(isinstance(n, int) and 0 <= n <= 9 for n in numbers):
            issues.append(f"Serie {i+1}: Números inválidos {numbers}")
            continue
        
        # Validar coherencia
        if serie['coherence_score'] < 0 or serie['coherence_score'] > 1:
            issues.append(f"Serie {i+1}: Coherencia inválida {serie['coherence_score']}")
            continue
        
        valid_count += 1
    
    return {
        "valid": valid_count > 0,
        "count": valid_count,
        "total": len(series),
        "issues": issues
    }

def mostrar_resultados_paso7(resultado):
    """Muestra los resultados del Paso 7"""
    print("📊 RESULTADOS DEL PASO 7 - GENERACIÓN DE SERIES CUÁNTICAS:")
    print("=" * 80)
    
    status = resultado.get('status', 'UNKNOWN')
    quantum_series = resultado.get('quantum_series', [])
    suggested_configs = resultado.get('suggested_configs', [])
    auditor_validation = resultado.get('auditor_validation', {})
    metadata = resultado.get('metadata', {})
    
    print(f"📊 ESTADO: {status}")
    print(f"📊 Series generadas: {len(quantum_series)}")
    print()
    
    # Mostrar series cuánticas
    if quantum_series:
        print("🔮 SERIES CUÁNTICAS GENERADAS:")
        print("-" * 50)
        for i, serie in enumerate(quantum_series, 1):
            serie_id = serie.get('id', f'QS-{i:03d}')
            numbers = serie.get('numbers', [])
            coherence = serie.get('coherence_score', 0.0)
            energy = serie.get('energy_level', 'N/A')
            props = serie.get('quantum_properties', {})
            
            print(f"   {i}. {serie_id}: {numbers}")
            print(f"      Coherencia: {coherence:.3f}")
            print(f"      Energía: {energy}")
            print(f"      Propiedades: {props}")
            print("-" * 40)
        print()
    
    # Mostrar configuraciones sugeridas
    if suggested_configs:
        print("⚙️ CONFIGURACIONES SUGERIDAS:")
        print("-" * 50)
        for i, config in enumerate(suggested_configs, 1):
            name = config.get('name', f'Config {i}')
            description = config.get('description', 'N/A')
            priority = config.get('priority', 'N/A')
            series = config.get('series', [])
            
            print(f"   {i}. {name} ({priority})")
            print(f"      Descripción: {description}")
            print(f"      Series: {[s.get('numbers', []) for s in series]}")
            print("-" * 40)
        print()
    
    # Mostrar validación del auditor
    if auditor_validation:
        print("✅ VALIDACIÓN DEL AUDITOR:")
        print("-" * 50)
        valid = auditor_validation.get('valid', False)
        count = auditor_validation.get('count', 0)
        total = auditor_validation.get('total', 0)
        issues = auditor_validation.get('issues', [])
        
        print(f"   Estado: {'✅ VÁLIDO' if valid else '❌ INVÁLIDO'}")
        print(f"   Series válidas: {count}/{total}")
        
        if issues:
            print(f"   Problemas encontrados:")
            for issue in issues:
                print(f"     - {issue}")
        print()
    
    # Mostrar metadatos
    if metadata:
        print("📋 METADATOS:")
        print("-" * 50)
        for key, value in metadata.items():
            if key != 'timestamp':
                print(f"   {key}: {value}")
        print()

def guardar_resultados_paso7(resultado):
    """Guarda los resultados del Paso 7"""
    try:
        os.makedirs("reports", exist_ok=True)
        
        data_to_save = {
            "timestamp": datetime.now().isoformat(),
            "step": 7,
            "name": "Generación de Series Cuánticas",
            "status": resultado.get('status', 'UNKNOWN'),
            "quantum_series": resultado.get('quantum_series', []),
            "suggested_configs": resultado.get('suggested_configs', []),
            "auditor_validation": resultado.get('auditor_validation', {}),
            "metadata": resultado.get('metadata', {}),
            "ready_for_step8": True
        }
        
        filename = "reports/paso7_series_cuanticas.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados del Paso 7 guardados en: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error guardando resultados: {e}")
        return None

def main():
    """Función principal"""
    print("🚀 INICIANDO PASO 7 - GENERACIÓN DE SERIES CUÁNTICAS")
    print("=" * 80)
    
    success = test_paso7_series_cuanticas()
    
    if success:
        print("\n🎉 PASO 7 COMPLETADO EXITOSAMENTE")
        print("   - Series cuánticas generadas")
        print("   - Configuraciones sugeridas creadas")
        print("   - Filtros de coherencia aplicados")
        print("   - Listo para Paso 8 (Documento Oficial)")
    else:
        print("\n💥 PASO 7 FALLÓ - REVISAR GENERACIÓN")
        print("   - Verificar datos de entrada")
        print("   - Revisar algoritmos cuánticos")
        print("   - Ajustar parámetros si es necesario")

if __name__ == "__main__":
    main()



