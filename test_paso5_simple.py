# ============================================
# 📌 TEST: PASO 5 - ATRIBUCIÓN A TABLA 100 (SIMPLE)
# Test simple para ver la estructura del resultado del Paso 5
# ============================================

import sys
import os
import json
from datetime import datetime

# Añadir el directorio de la app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_paso5_simple():
    print("🚀 PRUEBA SIMPLE: PASO 5 - ATRIBUCIÓN A TABLA 100")
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
        
        # Noticias del día actual (simuladas)
        noticias_dia = {
            "news_count": 98,
            "emotional_news_count": 14,
            "sources": ["BBC News", "NPR News", "BBC World News"],
            "topics": ["justicia", "crimen", "trabajo", "salud", "familia", "política"],
            "keywords": ["decisión", "contenedor", "umbral", "portal", "veredicto", "refugio"]
        }
        
        # Configuración del paso 5
        tabla_100_config = {
            "lottery_type": "florida_quiniela",
            "game": "Florida_Quiniela",
            "mode": "FLORIDA_QUINIELA",
            "draw_numbers": [4, 2, 7],
            "draw_date": "2025-09-07",
            "p3_mid": "427",
            "p4_mid": "8923", 
            "p3_eve": "156",
            "p4_eve": "3456",
            "noticias_dia": noticias_dia,
            "subliminal_topics": ['veredicto', 'decisión', 'propiedad', 'refugio', 'hogar', 'cirugía'],
            "subliminal_keywords": ['decisión', 'contenedor', 'umbral', 'portal', 'veredicto', 'refugio'],
            "subliminal_families": ['corte', 'casa']
        }
        
        print("📊 CONFIGURACIÓN:")
        print(f"   Juego: {tabla_100_config['game']}")
        print(f"   Sorteo: {tabla_100_config['draw_numbers']}")
        print(f"   Noticias del día: {noticias_dia['news_count']}")
        print(f"   Noticias emocionales: {noticias_dia['emotional_news_count']}")
        print()
        
        # Ejecutar Paso 5
        print("🔄 EJECUTANDO PASO 5:")
        print("-" * 40)
        
        resultado_paso5 = protocol._step_5_news_attribution_table100(
            news_data=noticias_dia,
            lottery_config=tabla_100_config
        )
        
        print(f"✅ Paso 5 ejecutado")
        print(f"   Estado: {resultado_paso5['status']}")
        print(f"   Nombre: {resultado_paso5['name']}")
        print()
        
        # Mostrar estructura completa del resultado
        print("📊 ESTRUCTURA COMPLETA DEL RESULTADO:")
        print("=" * 60)
        print(json.dumps(resultado_paso5, indent=2, ensure_ascii=False))
        print()
        
        # Mostrar detalles si existen
        if 'details' in resultado_paso5:
            print("📊 DETALLES DEL PASO 5:")
            print("-" * 40)
            detalles = resultado_paso5['details']
            for key, value in detalles.items():
                print(f"   {key}: {value}")
            print()
        
        # Resumen
        print("🎯 RESUMEN:")
        print("-" * 40)
        print(f"   Estado: {resultado_paso5['status']}")
        print(f"   Nombre: {resultado_paso5['name']}")
        if 'details' in resultado_paso5:
            print(f"   Detalles disponibles: {len(resultado_paso5['details'])} elementos")
        print()
        print("🚀 PASO 5 COMPLETADO")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en la prueba del Paso 5: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paso5_simple()
    if success:
        print("\n🎉 PRUEBA EXITOSA - ESTRUCTURA DEL PASO 5 CONOCIDA")
    else:
        print("\n💥 PRUEBA FALLIDA - REVISAR ERRORES")




