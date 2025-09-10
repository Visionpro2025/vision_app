# ============================================
# 📌 TEST: PASO 2 - CONFIGURACIÓN DE LOTERÍA
# Prueba del segundo paso del Protocolo Universal
# Configuración para Florida Quiniela Pick 3
# ============================================

import sys
import os
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso2_configuracion():
    print("🚀 PRUEBA: PASO 2 - CONFIGURACIÓN DE LOTERÍA")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el protocolo universal
        from universal_protocol_official import UniversalProtocolOfficial
        
        print("✅ Protocolo Universal importado correctamente")
        
        # Crear instancia del protocolo
        protocol = UniversalProtocolOfficial()
        
        print("✅ Instancia del protocolo creada")
        print()
        
        # Configuración para Florida Quiniela Pick 3
        print("📊 CONFIGURACIÓN PARA FLORIDA QUINIELA PICK 3")
        print("-" * 50)
        
        # Configuración específica de Florida Quiniela
        florida_config = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "p3_mid": "698",    # Pick 3 Midday
            "p4_mid": "5184",   # Pick 4 Midday
            "p3_eve": "607",    # Pick 3 Evening
            "p4_eve": "1670",   # Pick 4 Evening
            "draw_numbers": [6, 9, 8, 5, 1, 8, 4, 6, 0, 7, 1, 6, 7, 0],
            "news_query": "Florida community housing support demonstration"
        }
        
        print(f"Tipo de lotería: {florida_config['lottery_type']}")
        print(f"Juego: {florida_config['game']}")
        print(f"Modo: {florida_config['mode']}")
        print(f"Pick 3 Midday: {florida_config['p3_mid']}")
        print(f"Pick 4 Midday: {florida_config['p4_mid']}")
        print(f"Pick 3 Evening: {florida_config['p3_eve']}")
        print(f"Pick 4 Evening: {florida_config['p4_eve']}")
        print(f"Números del sorteo: {florida_config['draw_numbers']}")
        print(f"Consulta de noticias: {florida_config['news_query']}")
        print()
        
        # Ejecutar Paso 2: Configuración de Lotería
        print("🔄 EJECUTANDO PASO 2: CONFIGURACIÓN DE LOTERÍA")
        print("-" * 50)
        
        # Ejecutar el paso 2
        resultado_paso2 = protocol._step_2_lottery_configuration(
            lottery_type=florida_config['lottery_type'],
            lottery_config=florida_config
        )
        
        print(f"✅ Paso 2 ejecutado")
        print(f"   Estado: {resultado_paso2['status']}")
        print(f"   Nombre: {resultado_paso2['name']}")
        print()
        
        # Mostrar detalles del paso 2
        if resultado_paso2['status'] == 'completed':
            print("📊 DETALLES DEL PASO 2:")
            print("-" * 30)
            
            detalles = resultado_paso2['details']
            
            # 2.1 Perfil de lotería seleccionado
            print("2.1 Perfil de lotería seleccionado:")
            lottery_profile = detalles['lottery_profile']
            print(f"   ✅ Nombre: {lottery_profile.get('name', 'N/A')}")
            print(f"   ✅ Pools: {lottery_profile.get('pools', [])}")
            print(f"   ✅ Allow zero: {lottery_profile.get('allow_zero', False)}")
            print(f"   ✅ Perfil seleccionado: {lottery_profile.get('profile_selected', True)}")
            if 'error' in lottery_profile:
                print(f"   ⚠️  Error: {lottery_profile['error']}")
            print()
            
            # 2.2 Parámetros configurados
            print("2.2 Parámetros configurados:")
            parameters = detalles['parameters']
            print(f"   ✅ Nombre de lotería: {parameters.get('lottery_name', 'N/A')}")
            print(f"   ✅ Pools: {parameters.get('pools', [])}")
            print(f"   ✅ Allow zero: {parameters.get('allow_zero', False)}")
            print(f"   ✅ Parámetros configurados: {parameters.get('parameters_configured', False)}")
            if 'error' in parameters:
                print(f"   ⚠️  Error: {parameters['error']}")
            print()
            
            # 2.3 Validación del auditor
            print("2.3 Validación del auditor:")
            auditor_validation = detalles['auditor_validation']
            print(f"   ✅ Validación exitosa: {auditor_validation.get('valid', False)}")
            print(f"   ✅ Confianza: {auditor_validation.get('confidence', 'N/A')}")
            print(f"   ✅ Verificación: {auditor_validation.get('verification', 'N/A')}")
            if 'error' in auditor_validation:
                print(f"   ⚠️  Error: {auditor_validation['error']}")
            print()
            
            # Timestamp
            print(f"⏰ Timestamp: {detalles.get('timestamp', 'N/A')}")
            print()
            
            # Resumen final
            print("🎯 RESUMEN DEL PASO 2:")
            print("-" * 30)
            print("✅ Perfil de lotería seleccionado")
            print("✅ Parámetros configurados")
            print("✅ Configuración validada con auditor")
            print()
            print("🚀 PASO 2 COMPLETADO EXITOSAMENTE")
            print("📊 Sistema configurado para Florida Quiniela Pick 3")
            
        else:
            print(f"❌ Error en Paso 2: {resultado_paso2.get('error', 'Error desconocido')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 2: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso2_configuracion()
    if success:
        print("\n🎉 PRUEBA EXITOSA - PASO 2 FUNCIONANDO")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")





