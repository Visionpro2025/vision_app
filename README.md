# 🎯 VISION PREMIUM - Sistema de Orquestación Global

## 📋 DOCTRINA DE OPERACIÓN

> **Cursor es orquestador. La App.Vision es la que piensa. Sin datos reales → se aborta. No se simula, no se pregunta, no se rellena.**

---

## 🏗️ ARQUITECTURA DE ORQUESTACIÓN

### **POLÍTICA GLOBAL (Única Fuente de Verdad)**
- **Orquestador:** `cursor_only` - Cursor ejecuta, no opina
- **Simulaciones:** `false` - Prohibido simular datos
- **Fuentes:** `required` - Cada output debe tener fuente verificada
- **Vacío:** `abort` - Datos vacíos generan error ruidoso

### **SENTINELA UNIVERSAL**
- **Step 0:** `EnforceOrchestratorStep` - Se ejecuta en TODOS los planes
- **Enforcement:** Valida política global antes de cualquier operación
- **Bloqueo:** Aborta si detecta violaciones de política

### **GUARDRAILS REUTILIZABLES**
- **Validación de fuentes:** Solo dominios en allowlist
- **Prohibición de simulaciones:** Detecta y bloquea datos fake
- **Validación de outputs:** Garantiza datos completos y reales
- **Timeouts:** Límites estrictos de ejecución

---

## 🚀 USO DEL SISTEMA

### **1. CREAR UN NUEVO PLAN**

```json
{
  "name": "mi-plan",
  "steps": [
    {
      "name": "step0_enforce",
      "class": "EnforceOrchestratorStep",
      "inputs": {
        "policy": {
          "allow_simulation": false,
          "require_sources": true,
          "abort_on_empty": true
        }
      }
    },
    {
      "name": "mi_logica",
      "class": "MiCustomStep",
      "inputs": {
        "source": "https://reliable-source.com"
      }
    },
    {
      "name": "stepZ_audit",
      "class": "AuditEmitStep",
      "inputs": {
        "summary": {"completed": true}
      }
    }
  ]
}
```

### **2. IMPLEMENTAR UN STEP**

```python
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

@register_step("MiCustomStep")
class MiCustomStep(Step):
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Validar inputs con guardrails
        apply_basic_guardrails(
            step_name="MiCustomStep",
            input_data=data,
            output_data={},  # Se llenará después
            required_input_keys=["source"],
            sources_allowlist=["reliable-source.com"]
        )
        
        # 2. Procesar datos reales (NO simular)
        source = data["source"]
        real_data = fetch_real_data(source)
        
        # 3. Validar outputs
        output = {"result": real_data, "source": source}
        apply_basic_guardrails(
            step_name="MiCustomStep",
            input_data=data,
            output_data=output,
            required_output_keys=["result", "source"]
        )
        
        return output
```

### **3. EJECUTAR EL SISTEMA**

```bash
# Ejecutar aplicación
streamlit run app.py

# Ejecutar canary de salud
python scripts/ci_canary.py

# Verificar auditoría
ls reports/audit_*.json
```

---

## 🛡️ GUARDRAILS AUTOMÁTICOS

### **VALIDACIONES APLICADAS:**
- ✅ **Fuentes verificadas:** Solo dominios en allowlist
- ✅ **Simulaciones bloqueadas:** Detecta y prohíbe datos fake
- ✅ **Outputs completos:** Aborta si datos vacíos
- ✅ **Timeouts respetados:** Límites estrictos de ejecución
- ✅ **Política enforced:** Cursor solo orquesta

### **DOMINIOS PERMITIDOS:**
- **Lotería:** flalottery.com, floridalottery.com
- **Noticias:** apnews.com, reuters.com, bbc.com, nytimes.com
- **Oficiales:** .gov, .edu, .mil, .org

---

## 📊 AUDITORÍA AUTOMÁTICA

### **REPORTES GENERADOS:**
- **JSON:** `reports/audit_YYYYMMDD_HHMMSS.json`
- **Markdown:** `reports/audit_YYYYMMDD_HHMMSS.md`

### **INFORMACIÓN AUDITADA:**
- Política global aplicada
- Fuentes utilizadas y validadas
- Guardrails aplicados
- Tiempo de ejecución
- Errores y éxitos

---

## 🔧 CONFIGURACIÓN

### **POLÍTICA GLOBAL:** `plans/policy_app.yaml`
```yaml
app:
  orchestrator: cursor_only
  allow_simulation: false
  require_sources: true
  abort_on_empty: true
```

### **FUENTES PERMITIDAS:** Configuradas en `policy_app.yaml`
### **TIMEOUTS:** 20s por defecto, máximo 300s
### **AUDITORÍA:** Habilitada por defecto

---

## ⚠️ REGLAS ESTRICTAS

### **❌ PROHIBIDO:**
- Simular datos (dummy, test, mock, fake)
- Usar fuentes no permitidas
- Generar outputs vacíos
- Exceder timeouts
- Violar política global

### **✅ REQUERIDO:**
- Fuentes reales y verificadas
- Datos completos y válidos
- Aplicar guardrails en cada step
- Generar auditoría al final
- Cumplir política global

---

## 🐤 CANARY DE SALUD

El sistema incluye un canary automático que verifica:

1. **Política aplicada:** `cursor_role: orchestrator_only`
2. **Sin simulaciones:** No detecta patrones fake
3. **Guardrails activos:** Validaciones aplicadas
4. **Auditoría generada:** Reportes creados

```bash
python scripts/ci_canary.py
```

---

## 📞 SOPORTE

- **Documentación:** Ver archivos en `plans/` y `app_vision/`
- **Ejemplos:** Usar `plans/template_with_enforcement.json`
- **Debugging:** Revisar reportes en `reports/`
- **Canary:** Ejecutar `scripts/ci_canary.py`

---

## 🎯 RESUMEN EJECUTIVO

**VISION PREMIUM** implementa orquestación global con:

- 🎯 **Cursor solo orquesta** - No opina, solo ejecuta
- 🛡️ **App decide** - Lógica centralizada en la aplicación
- 🚫 **Sin simulaciones** - Solo datos reales y verificados
- 📊 **Auditoría completa** - Trazabilidad total
- ⚡ **Abortar en vacío** - Errores ruidosos, no silenciosos

**SISTEMA LISTO PARA PRODUCCIÓN CON GARANTÍAS DE CALIDAD.**



