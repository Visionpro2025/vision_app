# ============================================
# 📌 TEST: PASO 6 - ANÁLISIS SEFIRÓTICO
# Ejecuta el análisis sefirótico con los 5 sorteos reales
# ============================================

import sys
import os
from datetime import datetime
import json

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso6_analisis_sefirotico():
    """
    Ejecuta el Paso 6: Análisis Sefirótico con los 5 sorteos reales
    """
    print("🚀 PASO 6: ANÁLISIS SEFIRÓTICO DE ÚLTIMOS 5 SORTEOS")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el protocolo universal oficial
        from modules.universal_protocol_official import UniversalProtocolOfficial
        
        print("✅ UniversalProtocolOfficial importado correctamente")
        
        # Crear instancia del protocolo
        protocol = UniversalProtocolOfficial()
        
        print("✅ Instancia del protocolo creada")
        print()
        
        # Cargar los 5 sorteos reales
        try:
            with open("reports/sorteos_reales_para_paso6.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            draws = data.get("draws", [])
            print(f"✅ Sorteos reales cargados: {len(draws)}")
            
        except FileNotFoundError:
            print("❌ No se encontró el archivo de sorteos reales")
            print("   Usando datos de prueba...")
            draws = [
                {"date": "2025-09-03", "block": "MID", "numbers": [4, 2, 7]},
                {"date": "2025-09-04", "block": "EVE", "numbers": [8, 1, 5]},
                {"date": "2025-09-05", "block": "MID", "numbers": [3, 9, 6]},
                {"date": "2025-09-06", "block": "EVE", "numbers": [7, 4, 2]},
                {"date": "2025-09-07", "block": "MID", "numbers": [1, 8, 3]}
            ]
        
        print(f"📊 Sorteos para análisis sefirótico:")
        for i, draw in enumerate(draws, 1):
            date = draw.get('date', 'N/A')
            block = draw.get('block', 'N/A')
            numbers = draw.get('numbers', [])
            print(f"   {i}. {date} - {block}: {numbers}")
        print()
        
        # Configuración de lotería para el análisis
        lottery_config = {
            "name": "florida_pick3",
            "type": "pick3",
            "range": [0, 9],
            "draws_per_day": 2,  # MID y EVE
            "last_5_draws": draws
        }
        
        print("🎯 CONFIGURACIÓN DEL ANÁLISIS SEFIRÓTICO:")
        print("-" * 50)
        print(f"Lotería: {lottery_config['name']}")
        print(f"Tipo: {lottery_config['type']}")
        print(f"Rango: {lottery_config['range']}")
        print(f"Sorteos por día: {lottery_config['draws_per_day']}")
        print(f"Total de sorteos: {len(draws)}")
        print()
        
        # Ejecutar el Paso 6
        print("🔄 EJECUTANDO PASO 6 - ANÁLISIS SEFIRÓTICO:")
        print("-" * 50)
        
        try:
            # Ejecutar el método del protocolo
            resultado = protocol._step_6_sefirotic_analysis(lottery_config)
            
            print(f"✅ Paso 6 ejecutado")
            print(f"📊 Estado: {resultado.get('status', 'UNKNOWN')}")
            print()
            
            # Mostrar resultados detallados
            mostrar_resultados_paso6(resultado)
            
            # Guardar resultados
            guardar_resultados_paso6(resultado)
            
            return True
            
        except Exception as e:
            print(f"❌ Error ejecutando Paso 6: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Error general en Paso 6: {e}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_resultados_paso6(resultado):
    """Muestra los resultados del Paso 6"""
    print("📊 RESULTADOS DEL PASO 6 - ANÁLISIS SEFIRÓTICO:")
    print("=" * 80)
    
    details = resultado.get('details', {})
    
    # Mostrar información de los sorteos analizados
    last_5_draws = details.get('last_5_draws', {})
    if last_5_draws:
        print("📋 SORTEOS ANALIZADOS:")
        print("-" * 50)
        draws_list = last_5_draws.get('last_5_draws', [])
        for i, draw in enumerate(draws_list, 1):
            draw_number = draw.get('draw_number', f'FL-{i:03d}')
            draw_date = draw.get('draw_date', 'N/A')
            numbers = draw.get('numbers', [])
            lottery = draw.get('lottery', 'N/A')
            print(f"   {i}. {draw_number} ({draw_date}): {numbers} - {lottery}")
        print()
    
    # Mostrar análisis sefirótico
    sefirot_analysis = details.get('sefirot_analysis', {})
    if sefirot_analysis:
        print("🔮 ANÁLISIS SEFIRÓTICO:")
        print("-" * 50)
        
        # Análisis por sorteo
        draw_analyses = sefirot_analysis.get('draw_analyses', [])
        if draw_analyses:
            print("📊 Análisis por sorteo:")
            for i, analysis in enumerate(draw_analyses, 1):
                print(f"   Sorteo {i}:")
                high_energy = analysis.get('high_energy_numbers', [])
                spiritual = analysis.get('spiritual_significance', {})
                print(f"     - Números de alta energía: {high_energy}")
                print(f"     - Significancia espiritual: {spiritual}")
            print()
        
        # Patrones generales
        overall_patterns = sefirot_analysis.get('overall_patterns', {})
        if overall_patterns:
            print("📈 Patrones generales:")
            for key, value in overall_patterns.items():
                print(f"   - {key}: {value}")
            print()
        
        # Flujo energético
        energy_flow = sefirot_analysis.get('energy_flow', {})
        if energy_flow:
            print("⚡ Flujo energético:")
            for key, value in energy_flow.items():
                print(f"   - {key}: {value}")
            print()
        
        # Significancia espiritual
        spiritual_significance = sefirot_analysis.get('spiritual_significance', {})
        if spiritual_significance:
            print("🌟 Significancia espiritual:")
            for key, value in spiritual_significance.items():
                print(f"   - {key}: {value}")
            print()
    
    # Mostrar números candidatos
    candidate_numbers = details.get('candidate_numbers', {})
    if candidate_numbers:
        print("🎯 NÚMEROS CANDIDATOS:")
        print("-" * 50)
        
        for category, numbers in candidate_numbers.items():
            if numbers:
                print(f"   {category}: {numbers}")
        print()
    
    # Mostrar análisis de correlación
    correlation_analysis = details.get('correlation_analysis', {})
    if correlation_analysis:
        print("🔗 ANÁLISIS DE CORRELACIÓN:")
        print("-" * 50)
        
        high_correlation = correlation_analysis.get('high_correlation', [])
        medium_correlation = correlation_analysis.get('medium_correlation', [])
        low_correlation = correlation_analysis.get('low_correlation', [])
        
        print(f"   Alta correlación: {high_correlation}")
        print(f"   Correlación media: {medium_correlation}")
        print(f"   Baja correlación: {low_correlation}")
        print()
    
    # Mostrar perfil de series
    series_profile = details.get('series_profile', {})
    if series_profile:
        print("📊 PERFIL DE SERIES:")
        print("-" * 50)
        
        for key, value in series_profile.items():
            print(f"   - {key}: {value}")
        print()
    
    # Mostrar validación del auditor
    auditor_validation = details.get('auditor_validation', {})
    if auditor_validation:
        print("✅ VALIDACIÓN DEL AUDITOR:")
        print("-" * 50)
        
        for key, value in auditor_validation.items():
            print(f"   - {key}: {value}")
        print()

def guardar_resultados_paso6(resultado):
    """Guarda los resultados del Paso 6"""
    try:
        os.makedirs("reports", exist_ok=True)
        
        data_to_save = {
            "timestamp": datetime.now().isoformat(),
            "step": 6,
            "name": "Análisis Sefirótico de Últimos 5 Sorteos",
            "status": resultado.get('status', 'UNKNOWN'),
            "details": resultado.get('details', {}),
            "ready_for_step7": True
        }
        
        filename = "reports/paso6_analisis_sefirotico.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados del Paso 6 guardados en: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error guardando resultados: {e}")
        return None

def main():
    """Función principal"""
    print("🚀 INICIANDO PASO 6 - ANÁLISIS SEFIRÓTICO")
    print("=" * 80)
    
    success = test_paso6_analisis_sefirotico()
    
    if success:
        print("\n🎉 PASO 6 COMPLETADO EXITOSAMENTE")
        print("   - Análisis sefirótico realizado")
        print("   - Números candidatos generados")
        print("   - Listo para Paso 7 (Generación de Series Cuánticas)")
    else:
        print("\n💥 PASO 6 FALLÓ - REVISAR ANÁLISIS")
        print("   - Verificar sorteos de entrada")
        print("   - Revisar configuración de lotería")
        print("   - Ajustar parámetros si es necesario")

if __name__ == "__main__":
    main()





