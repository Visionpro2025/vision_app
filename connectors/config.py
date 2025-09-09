# connectors/config.py
"""
Configuración para conectores de fuentes externas
"""

# URLs de fuentes
FLORIDA_PICK3_URL = "https://floridalottery.com/games/draw-games/pick-3"
FLORIDA_PICK4_URL = "https://flalottery.com/pick4"
FLORIDA_P3_PDF_URL = "https://www.flalottery.com/exptkt/p3.pdf"

LOTTERYUSA_MID_P3_URL = "https://www.lotteryusa.com/florida/midday-pick-3/"
LOTTERYUSA_EVE_P3_URL = "https://www.lotteryusa.com/florida/evening-pick-3/"
LOTTERYUSA_MID_P4_URL = "https://www.lotteryusa.com/florida/midday-pick-4/"
LOTTERYUSA_EVE_P4_URL = "https://www.lotteryusa.com/florida/evening-pick-4/"

BOLITA_DC_URL = "https://www.directoriocubano.info/bolita/"
BOLITA_LBC_URL = "https://www.labolitacubana.com/"

# Configuración de timeouts
DEFAULT_TIMEOUT = 12
QUICK_TIMEOUT = 5
LONG_TIMEOUT = 20

# Configuración de rate limiting
RATE_LIMIT_DELAY = 1  # segundos entre requests
MAX_RETRIES = 3

# User agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

# Configuración de validación
MIN_RESULTS_DEFAULT = 2
MAX_RESULTS_DEFAULT = 50
DAYS_BACK_DEFAULT = 7

# Marcas de confianza
SOURCE_CONFIDENCE = {
    "flalottery.com": "official",
    "floridalottery.com": "official", 
    "lotteryusa.com": "secondary",
    "directoriocubano.info": "reference",
    "labolitacubana.com": "reference"
}


