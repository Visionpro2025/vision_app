#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN CLI - Interfaz de línea de comandos para App.Vision
Recibe texto corto y llama al orquestador conversacional
"""

import sys
import argparse
from conversational_orchestrator import call_conversational_orchestrator, get_orchestrator_status
from session_state import get_session_state, reset_session, save_session, load_session
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Función principal del CLI"""
    parser = argparse.ArgumentParser(
        description="App.Vision Orquestador Conversacional - CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_cli.py "Inicia protocolo"
  python run_cli.py "Continuar"
  python run_cli.py "Estado"
  python run_cli.py "Buscar sorteos 2025-08-20..2025-09-05"
  python run_cli.py "Cambia a nano"
  python run_cli.py "Detener"
  python run_cli.py "Reinicia"
  python run_cli.py "Hola, ¿cómo estás?"
        """
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        help="Mensaje o comando para el orquestador"
    )
    
    parser.add_argument(
        "--model",
        choices=["gpt-4o-mini", "gpt-5-nano"],
        help="Modelo específico a usar (sobrescribe el modelo actual)"
    )
    
    parser.add_argument(
        "--status",
        action="store_true",
        help="Mostrar estado del orquestador"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reiniciar el estado del orquestador"
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Guardar el estado actual"
    )
    
    parser.add_argument(
        "--load",
        action="store_true",
        help="Cargar el estado guardado"
    )
    
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Modo interactivo (bucle de comandos)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Modo verbose (más información de debug)"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Cargar estado si se solicita
    if args.load:
        if load_session():
            print("✅ Estado cargado desde archivo")
        else:
            print("ℹ️ No se encontró estado guardado")
    
    # Mostrar estado si se solicita
    if args.status:
        status = get_orchestrator_status()
        print("📊 Estado del Orquestador:")
        print(f"  Modo: {status['mode']}")
        print(f"  Modelo: {status['current_model']}")
        print(f"  Tarea: {status['current_task'] or 'Ninguna'}")
        print(f"  Etapa: {status['protocol_stage'] or 'Ninguna'}")
        print(f"  Mensajes: {status['history_count']}")
        print(f"  Herramientas: {status['tools_available']}")
        return
    
    # Reiniciar si se solicita
    if args.reset:
        reset_session()
        print("🔄 Estado reiniciado")
        return
    
    # Guardar si se solicita
    if args.save:
        save_session()
        print("💾 Estado guardado")
        return
    
    # Modo interactivo
    if args.interactive:
        run_interactive_mode(args.model)
        return
    
    # Procesar mensaje único
    if args.message:
        process_message(args.message, args.model)
    else:
        print("❌ Error: Debes proporcionar un mensaje o usar --interactive")
        parser.print_help()
        sys.exit(1)

def process_message(message: str, model: str = None):
    """Procesa un mensaje único"""
    try:
        print(f"🎯 Procesando: {message}")
        print("-" * 50)
        
        # Llamar al orquestador
        response = call_conversational_orchestrator(message, model)
        
        print(f"🤖 Respuesta: {response}")
        print("-" * 50)
        
        # Guardar estado automáticamente
        save_session()
        
    except Exception as e:
        logger.error(f"❌ Error procesando mensaje: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

def run_interactive_mode(model: str = None):
    """Ejecuta el modo interactivo"""
    print("🎯 VISION PREMIUM - Modo Interactivo")
    print("=" * 50)
    print("💡 Escribe comandos cortos o mensajes largos")
    print("💡 Comandos especiales: 'salir', 'estado', 'ayuda'")
    print("=" * 50)
    
    session_state = get_session_state()
    
    while True:
        try:
            # Obtener input del usuario
            user_input = input("\n👤 Usuario: ").strip()
            
            # Comandos especiales del CLI
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                save_session()
                break
            elif user_input.lower() == 'estado':
                status = get_orchestrator_status()
                print(f"📊 Estado: {status}")
                continue
            elif user_input.lower() == 'ayuda':
                print_help()
                continue
            elif user_input.lower() == 'reset':
                reset_session()
                print("🔄 Estado reiniciado")
                continue
            elif user_input.lower() == 'save':
                save_session()
                print("💾 Estado guardado")
                continue
            elif user_input.lower() == 'load':
                if load_session():
                    print("✅ Estado cargado")
                else:
                    print("ℹ️ No se encontró estado guardado")
                continue
            
            # Procesar mensaje normal
            if user_input:
                response = call_conversational_orchestrator(user_input, model)
                print(f"🤖 Sistema: {response}")
                
                # Guardar estado cada 5 mensajes
                if len(session_state.get_history()) % 5 == 0:
                    save_session()
        
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            save_session()
            break
        except Exception as e:
            logger.error(f"❌ Error en modo interactivo: {e}")
            print(f"❌ Error: {e}")

def print_help():
    """Muestra la ayuda del CLI"""
    print("""
📋 Comandos del CLI:

🎯 Comandos de Protocolo:
  Inicia protocolo    - Arranca análisis de MegaMillions
  Continuar          - Siguiente etapa del protocolo
  Estado             - Muestra estado actual
  Detener            - Cierra protocolo actual

🔧 Comandos de Herramientas:
  Gematria           - Fuerza análisis de gematría
  Subliminal         - Fuerza análisis subliminal

🔍 Comandos de Búsqueda:
  Buscar sorteos 2025-08-20..2025-09-05  - Busca por rango
  Buscar sorteos 2025-09-01              - Busca por fecha

⚙️ Comandos de Configuración:
  Cambia a mini      - Modelo gpt-4o-mini
  Cambia a nano      - Modelo gpt-5-nano

💾 Comandos de Gestión:
  Guardar serie guía - Persiste resultado
  Reinicia           - Borra estado

❓ Comandos Especiales:
  salir              - Salir del modo interactivo
  estado             - Mostrar estado
  ayuda              - Mostrar esta ayuda
  reset              - Reiniciar estado
  save               - Guardar estado
  load               - Cargar estado

💬 Mensajes Largos:
  Cualquier mensaje de más de 50 caracteres se procesa como conversación normal.
    """)

if __name__ == "__main__":
    main()






