# Conectores de Fuentes Externas

Este directorio contiene conectores para obtener datos reales de fuentes externas de lotería.

## Fuentes Disponibles

### 1. Florida Lottery Oficial
- **Archivo:** `florida_official.py`
- **URLs:** 
  - Pick 3: https://floridalottery.com/games/draw-games/pick-3
  - Pick 4: https://flalottery.com/pick4
- **Confianza:** Oficial
- **Datos:** Pick 3, Pick 4, Fireball, fechas, bloques (MID/EVE)

### 2. LotteryUSA Backup
- **Archivo:** `lotteryusa_backup.py`
- **URLs:**
  - Midday Pick 3: https://www.lotteryusa.com/florida/midday-pick-3/
  - Evening Pick 3: https://www.lotteryusa.com/florida/evening-pick-3/
  - Midday Pick 4: https://www.lotteryusa.com/florida/midday-pick-4/
  - Evening Pick 4: https://www.lotteryusa.com/florida/evening-pick-4/
- **Confianza:** Secundaria
- **Datos:** Pick 3, Pick 4, fechas, bloques (MID/EVE)

### 3. Bolita Cubana
- **Archivo:** `bolita_cuba.py`
- **URLs:**
  - Directorio Cubano: https://www.directoriocubano.info/bolita/
  - LaBolitaCubana: https://www.labolitacubana.com/
- **Confianza:** Referencia
- **Datos:** Fijo, corridos, parlés, candado

## Uso

### Importar conectores
```python
from connectors.florida_official import fetch_pick3_latest_html, fetch_pick4_latest_html, merge_p3_p4
from connectors.lotteryusa_backup import fetch_pick3_pick4_backup
from connectors.bolita_cuba import fetch_directorio_cubano, fetch_labolitacubana
```

### Obtener datos de Florida
```python
# Obtener Pick 3
p3_data = fetch_pick3_latest_html()

# Obtener Pick 4
p4_data = fetch_pick4_latest_html()

# Combinar datos
combined = merge_p3_p4(p3_data, p4_data)
```

### Usar backup
```python
# Si la fuente oficial falla
backup_data = fetch_pick3_pick4_backup()
```

### Obtener referencias de bolita
```python
# Directorio Cubano
dc_data = fetch_directorio_cubano()

# LaBolitaCubana
lbc_data = fetch_labolitacubana()
```

## Integración en Steps

Los conectores están integrados en:
- `FetchExternalSourcesStep` - Step principal para obtener datos
- `FetchFLPick3RealStep` - Step específico de Florida Pick 3

## Configuración

- **Timeouts:** Configurables por fuente
- **Rate Limiting:** 1 segundo entre requests
- **Retries:** Máximo 3 intentos
- **User Agents:** Rotación automática

## Validación

- **Fuentes permitidas:** Solo fuentes oficiales y verificadas
- **Datos mínimos:** Configurable (default: 2 sorteos)
- **Normalización:** Fechas en formato ISO, bloques normalizados

## Política de Datos Reales

**NO HAY FALLBACK SIMULADO** - El sistema solo funciona con datos reales de fuentes externas verificadas. Si las fuentes fallan, el sistema reporta error y no genera datos simulados.

## Consideraciones Legales

- Respetar Términos de Servicio de cada sitio
- Rate limiting para evitar sobrecarga
- User agents claros y identificables
- Solo para uso personal/educativo
