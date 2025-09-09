import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_MODEL = os.getenv("APP_MODEL", "gpt-4o-mini")
APP_MODEL_TEST = os.getenv("APP_MODEL_TEST", "gpt-5-nano")
APP_MAX_OUTPUT_TOKENS = int(os.getenv("APP_MAX_OUTPUT_TOKENS", "800"))
APP_TEMPERATURE = float(os.getenv("APP_TEMPERATURE", "0.2"))
APP_BUDGET_USD_PER_CALL = float(os.getenv("APP_BUDGET_USD_PER_CALL", "0.002"))
APP_MAX_RETRIES = int(os.getenv("APP_MAX_RETRIES", "3"))

# Función para verificar configuración
def verify_config():
    """Verifica que la configuración esté correcta"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-tu-clave-api-aqui":
        return False, "OPENAI_API_KEY no configurada"
    
    return True, "Configuración correcta"

# Función para obtener información del orquestador
def get_orchestrator_config():
    """Obtiene la configuración del orquestador"""
    return {
        "provider": "OpenAI API (Orquestador Controlado)",
        "model_principal": APP_MODEL,
        "model_test": APP_MODEL_TEST,
        "api_key_configured": bool(OPENAI_API_KEY and OPENAI_API_KEY != "sk-tu-clave-api-aqui"),
        "max_tokens": APP_MAX_OUTPUT_TOKENS,
        "temperature": APP_TEMPERATURE,
        "budget_per_call": APP_BUDGET_USD_PER_CALL,
        "max_retries": APP_MAX_RETRIES
    }

if __name__ == "__main__":
    print("🔧 VISION PREMIUM - Configuración del Orquestador")
    print("=" * 60)
    
    # Verificar configuración
    is_valid, message = verify_config()
    print(f"Estado: {'✅' if is_valid else '❌'} {message}")
    
    # Mostrar configuración del orquestador
    config = get_orchestrator_config()
    print(f"Proveedor: {config['provider']}")
    print(f"Modelo principal: {config.get('model_principal', 'N/A')}")
    print(f"Modelo test: {config.get('model_test', 'N/A')}")
    print(f"API Key: {'✅ Configurada' if config['api_key_configured'] else '❌ No configurada'}")
    print(f"Max tokens: {config.get('max_tokens', 'N/A')}")
    print(f"Temperatura: {config.get('temperature', 'N/A')}")
    print(f"Presupuesto por llamada: ${config.get('budget_per_call', 'N/A')}")
    print(f"Max reintentos: {config.get('max_retries', 'N/A')}")