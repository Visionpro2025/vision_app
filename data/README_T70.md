# Sistema T70/T100 - VISIÓN Premium

## 📋 Descripción

El Sistema T70/T100 es una implementación completa para la gestión, validación y fusión de las tablas T70 y T100. La tabla T70 contiene 70 entradas numerológicas originales, mientras que T100 extiende el sistema a 100 entradas con capas narrativas enriquecidas según las teorías de Joseph Campbell, Marie-Louise von Franz y Sigmund Freud.

## 🏗️ Estructura del Proyecto

```
data/
├── T70.csv                           # CSV original con datos base (1-70)
├── T100.csv                          # CSV extendido (1-100)
├── T100_enriched.json                # JSON con capas narrativas (1-100)
├── T100_enriched_merged.json         # Archivo fusionado final (1-100)
├── T70_validation_*.txt              # Reportes de validación
├── T70_merge_report_*.txt            # Reportes de fusión
└── README_T70.md                     # Esta documentación

scripts/
├── validate_t70.py                   # Script de validación (1-100)
├── merge_t70.py                      # Script de fusión
└── upgrade_t70_to_t100.py            # Script de actualización T70→T100

pages/
└── 13_Admin_T70.py                   # Interfaz Streamlit (T70/T100)
```

## 🔧 Scripts Disponibles

### 1. Validación (`validate_t70.py`)

**Propósito**: Valida la estructura y contenido del archivo CSV T70.

**Uso**:
```bash
python scripts/validate_t70.py data/T70.csv
```

**Funcionalidades**:
- ✅ Detección automática de encabezados (tolerante a acentos/alias)
- ✅ Validación de unicidad de números N (1-70)
- ✅ Verificación de campos obligatorios no vacíos
- ✅ Validación de rangos y tipos de datos
- ✅ Generación de reportes detallados

**Campos Obligatorios**:
- `N`: Número base (1-70, único)
- `titulo`: Título de la entrada
- `lectura`: Descripción/lectura
- `categoria`: Categoría temática

**Alias de Encabezados Soportados**:
- `N`: n, num, numero, número, id, idx
- `EQ`: eq, equivalente, equiv, valor, valor_eq
- `titulo`: titulo, título, title, nombre
- `lectura`: lectura, reading, descripcion, descripción, desc
- `categoria`: categoria, categoría, category, grupo, caracteristicas

### 2. Actualización T70→T100 (`upgrade_t70_to_t100.py`)

**Propósito**: Extiende automáticamente la tabla T70 (1-70) a T100 (1-100) sin alterar los datos existentes.

**Uso**:
```bash
python scripts/upgrade_t70_to_t100.py
```

**Funcionalidades**:
- 🔄 Extensión automática de 70 a 100 entradas
- 🎯 Generación de 30 nuevas entradas (71-100) con capas narrativas completas
- 💾 Preservación total de datos existentes (1-70)
- 📊 Estructura coherente con Campbell, vonFranz y Freud
- 🎨 EQ = 101-N para nuevas entradas (sin conflictos)

**Salidas**:
- `data/T100.csv` - CSV extendido con 100 entradas
- `data/T100_enriched.json` - JSON con todas las capas narrativas

### 3. Fusión (`merge_t70.py`)

**Propósito**: Combina el CSV validado con el JSON enriquecido.

**Uso**:
```bash
python scripts/merge_t70.py --csv data/T70.csv --json data/T70_enriched.json --out data/T70_enriched_merged.json
```

**Opciones**:
- `--csv`: Archivo CSV de entrada
- `--json`: Archivo JSON enriquecido
- `--out`: Archivo de salida
- `--dry-run`: Solo reporte, no escribe archivo

**Funcionalidades**:
- 🔄 Fusión inteligente por número N o EQ
- 📊 Estadísticas de emparejamiento
- 💾 Backup automático del archivo de salida
- 📄 Reportes detallados de fusión

## 🎯 Estructura de Datos Final

Cada entrada en el archivo fusionado contiene:

```json
{
  "N": 1,                       // Número base (1-70)
  "EQ": 70,                     // Equivalente numérico
  "titulo": "Texto",            // Título de la entrada
  "lectura": "Texto",           // Descripción/lectura
  "categoria": "Texto",         // Categoría temática
  "campbell_stage": "Texto",    // Etapa del viaje del héroe
  "vonfranz_symbol": ["txt"],   // Símbolos sociales
  "freud": {                    // Análisis psicoanalítico
    "manifest": "Texto",        // Lo visible/explícito
    "latent": "Texto"           // Lo reprimido/inconsciente
  }
}
```

## 🗺️ Distribución de Etapas Campbell

| Etapa | Números | Descripción |
|-------|---------|-------------|
| **Mundo ordinario** | 1-5 | Estado inicial, identidad, comienzo |
| **Llamado a la aventura** | 6-10 | Invitación al cambio |
| **Rechazo del llamado** | 11-15 | Resistencia al cambio |
| **Encuentro con el mentor** | 16-20 | Guía y preparación |
| **Cruce del umbral** | 21-25 | Ruptura inicial |
| **Pruebas, aliados y enemigos** | 26-35 | Desafíos múltiples |
| **Acercamiento a la caverna profunda** | 36-45 | Crisis y acumulación |
| **Ordalía / Abismo** | 46-50 | Enfrentamiento central |
| **Recompensa** | 51-55 | Reconocimiento y premio |
| **Camino de regreso** | 56-60 | Retorno con aprendizajes |
| **Resurrección** | 61-65 | Transformación profunda |
| **Regreso con el elixir** | 66-70 | Sabiduría compartida |

## 🚀 Interfaz Streamlit

La página `13_Admin_T70.py` proporciona una interfaz gráfica para:

- 🔍 **Validar T70.csv**: Ejecuta validación y muestra reportes
- 🔄 **Fusionar T70**: Combina archivos y genera resultado final
- 📊 **Monitorear Estado**: Muestra estado de archivos y estadísticas
- 📄 **Ver Reportes**: Acceso directo a reportes generados

## ✅ Criterios de Aceptación

- **Validación**: Si hay errores bloqueantes, la fusión no se ejecuta
- **Tolerancia**: Funciona con encabezados con/sin acentos
- **Backup**: Crea backup automático del archivo de salida
- **Reportes**: Genera reportes detallados de cada operación
- **Idempotencia**: Se puede ejecutar múltiples veces sin problemas
- **Compatibilidad**: T70→T100 preserva 100% de datos existentes
- **Extensibilidad**: Nuevas entradas (71-100) con capas narrativas completas

## 🔍 Ejemplos de Uso

### Validación Básica
```bash
# Validar CSV T70
python scripts/validate_t70.py data/T70.csv

# Validar CSV T100
python scripts/validate_t70.py data/T100.csv

# Si la validación pasa, proceder con fusión
python scripts/merge_t70.py --csv data/T70.csv --json data/T70_enriched.json --out data/T70_enriched_merged.json
```

### Actualización T70→T100
```bash
# Extender automáticamente de T70 a T100
python scripts/upgrade_t70_to_t100.py

# Validar T100 generado
python scripts/validate_t70.py data/T100.csv

# Fusionar T100
python scripts/merge_t70.py --csv data/T100.csv --json data/T100_enriched.json --out data/T100_enriched_merged.json
```

### Modo Dry-Run
```bash
# Solo ver qué pasaría sin escribir archivo
python scripts/merge_t70.py --csv data/T70.csv --json data/T70_enriched.json --out data/T70_enriched_merged.json --dry-run
```

### Desde Streamlit
1. Navegar a la página "Admin T70"
2. Hacer clic en "🔍 Validar T70.csv"
3. Si es exitoso, hacer clic en "🔄 Fusionar T70"
4. Revisar reportes y archivo generado

## 📊 Monitoreo y Reportes

### Reportes de Validación
- Detección de encabezados
- Mapeo de campos
- Errores y advertencias
- Estadísticas de datos

### Reportes de Fusión
- Estadísticas de emparejamiento
- Entradas emparejadas
- Entradas solo CSV/JSON
- Estructura final

## 🛠️ Mantenimiento

### Archivos de Backup
- Se crean automáticamente antes de sobrescribir
- Formato: `.bak_YYYYMMDD_HHMMSS`
- Ubicación: mismo directorio que el archivo original

### Logs y Reportes
- Se generan con timestamp único
- Se almacenan en directorio `data/`
- Se pueden revisar desde la interfaz Streamlit

## 🎉 Estado Actual

✅ **Sistema T70/T100 Completamente Funcional**
- Validación robusta implementada (1-100)
- Fusión inteligente funcionando
- Actualización automática T70→T100
- Interfaz Streamlit operativa
- Documentación completa
- Reportes automáticos
- Backup automático
- 30 nuevas entradas (71-100) con capas narrativas completas

El Sistema T70/T100 está listo para producción y puede manejar actualizaciones, validaciones y fusiones de manera robusta y confiable. La extensión a T100 preserva 100% de la funcionalidad existente.
