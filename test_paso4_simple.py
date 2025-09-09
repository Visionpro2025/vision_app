# ============================================
# 📌 TEST: PASO 4 - RECOPILACIÓN DE NOTICIAS (SIMPLE)
# Test simple para ver la estructura del resultado del Paso 4
# ============================================

import sys
import os
import json
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso4_simple():
    print("🚀 PRUEBA SIMPLE: PASO 4 - RECOPILACIÓN DE NOTICIAS")
    print("=" * 80)
    print(f"Fecha actual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Importar el protocolo universal
        from universal_protocol_official import UniversalProtocolOfficial
        
        print("✅ Protocolo Universal importado correctamente")
        
        # Crear instancia del protocolo
        protocol = UniversalProtocolOfficial()
        
        print("✅ Instancia del protocolo creada")
        print()
        
        # Submensaje guía del Paso 3 V2
        submensaje_guia = {
            "topics": ['veredicto', 'decisión', 'propiedad', 'refugio', 'hogar', 'cirugía'],
            "keywords": ['decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio'],
            "families": ['corte', 'casa']
        }
        
        # Configuración del paso 4
        noticias_config = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "news_query": "Florida community housing support demonstration september 2025",
            "submessage_guide": submensaje_guia,
            "draw_date": "2025-09-07",
            "draw_numbers": [4, 2, 7]
        }
        
        print("📊 CONFIGURACIÓN:")
        print(f"   Submensaje guía: {submensaje_guia}")
        print(f"   Consulta noticias: {noticias_config['news_query']}")
        print()
        
        # Ejecutar Paso 4
        print("🔄 EJECUTANDO PASO 4:")
        print("-" * 40)
        
        resultado_paso4 = protocol._step_4_news_collection(
            submessage_guide=str(submensaje_guia),
            lottery_config=noticias_config
        )
        
        print(f"✅ Paso 4 ejecutado")
        print(f"   Estado: {resultado_paso4['status']}")
        print(f"   Nombre: {resultado_paso4['name']}")
        print()
        
        # Mostrar estructura completa del resultado
        print("📊 ESTRUCTURA COMPLETA DEL RESULTADO:")
        print("=" * 60)
        print(json.dumps(resultado_paso4, indent=2, ensure_ascii=False))
        print()
        
        # Mostrar detalles si existen
        if 'details' in resultado_paso4:
            print("📊 DETALLES DEL PASO 4:")
            print("-" * 40)
            detalles = resultado_paso4['details']
            for key, value in detalles.items():
                print(f"   {key}: {value}")
            print()
        
        # Resumen
        print("🎯 RESUMEN:")
        print("-" * 40)
        print(f"   Estado: {resultado_paso4['status']}")
        print(f"   Nombre: {resultado_paso4['name']}")
        if 'details' in resultado_paso4:
            print(f"   Detalles disponibles: {len(resultado_paso4['details'])} elementos")
        print()
        print("🚀 PASO 4 COMPLETADO")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 4: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso4_simple()
    if success:
        print("\n🎉 PRUEBA EXITOSA - ESTRUCTURA DEL PASO 4 CONOCIDA")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")




