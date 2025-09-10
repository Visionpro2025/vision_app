#!/usr/bin/env python3
"""
Control interactivo para Florida Pick 3
Ejecuta comandos del usuario en tiempo real
"""

from orquestador_florida_pick3 import OrquestadorFloridaPick3
import sys

def main():
    """Función principal de control interactivo"""
    
    print("🎯 CONTROL INTERACTIVO - FLORIDA PICK 3")
    print("=" * 60)
    print("📅 Sistema de orquestación activo")
    print("🎯 Lotería: Florida Pick 3 (0-9, 3 posiciones)")
    print("=" * 60)
    
    # Crear orquestador
    orquestador = OrquestadorFloridaPick3()
    
    # Inicializar
    if not orquestador.inicializar():
        print("❌ Error inicializando orquestador")
        return
    
    print("\n✅ SISTEMA LISTO")
    print("🎯 Orquestador activo - Esperando instrucciones")
    print("\n💡 COMANDOS DISPONIBLES:")
    print("   • 'estado' - Ver estado actual")
    print("   • 'pasos' - Ver pasos disponibles")
    print("   • 'paso X' - Ejecutar paso específico (1-9)")
    print("   • 'ayuda' - Ver ayuda completa")
    print("   • 'salir' - Terminar orquestación")
    print("\n" + "="*60)
    
    # Bucle principal de comandos
    while True:
        try:
            # Obtener comando del usuario
            comando = input("\n🎯 Ingrese comando: ").strip()
            
            if comando.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 Finalizando orquestación...")
                break
            
            elif comando.lower() in ['ayuda', 'help']:
                orquestador.mostrar_ayuda()
            
            elif comando.lower() in ['estado', 'status']:
                orquestador.mostrar_estado()
            
            elif comando.lower() in ['pasos', 'steps']:
                orquestador.mostrar_pasos_disponibles()
            
            elif comando.lower().startswith('paso') or comando.lower().startswith('ejecutar paso'):
                orquestador.ejecutar_comando(comando)
            
            elif comando == '':
                continue
            
            else:
                print(f"❌ Comando no reconocido: '{comando}'")
                print("💡 Use 'ayuda' para ver comandos disponibles")
        
        except KeyboardInterrupt:
            print("\n\n👋 Orquestación interrumpida por el usuario")
            break
        
        except Exception as e:
            print(f"❌ Error procesando comando: {str(e)}")
    
    print("\n🎯 ORQUESTACIÓN FINALIZADA")
    print("=" * 60)

if __name__ == "__main__":
    main()






