# 🔄 Plan de Rollback Express - Dagster Cloud

## Si algo falla en producción (Dagster Cloud)

### 1. Desactivar Schedules
En la UI de Dagster Cloud:
1. Ve a **Schedules**
2. Desactiva (OFF) los siguientes schedules:
   - `protocolo_am`
   - `protocolo_mid` 
   - `protocolo_eve`

### 2. Rollback Rápido del Código
En GitHub:

1. **Identificar commit anterior:**
   ```bash
   git log --oneline -5
   # Busca el commit anterior a chore/cloud-hardening
   ```

2. **Crear rama de rollback:**
   ```bash
   git checkout -b rollback/hardening <commit-anterior>
   git push origin rollback/hardening
   ```

3. **Crear PR de rollback:**
   - Ve a: https://github.com/Visionpro2025/vision_app/compare/main...rollback/hardening
   - Title: `rollback: revert cloud hardening changes`
   - Body: `Reverting cloud hardening changes due to production issues`
   - Merge PR → main

4. **Cloud importará automáticamente** la versión anterior

### 3. Reactivar Schedules (cuando el fix esté listo)
Una vez que merges la corrección:
1. Ve a **Schedules** en Dagster Cloud UI
2. Reactiva (ON) los schedules:
   - `protocolo_am`
   - `protocolo_mid`
   - `protocolo_eve`

## Comandos de Emergencia

```bash
# Verificar estado actual
git status
git log --oneline -3

# Rollback rápido (si estás en main)
git reset --hard HEAD~1
git push --force-with-lease origin main

# O crear rama de rollback
git checkout -b rollback/emergency
git push origin rollback/emergency
```

## Notas Importantes

- **NUNCA** hagas `git push --force` sin `--force-with-lease`
- **Siempre** desactiva schedules antes del rollback
- **Documenta** el motivo del rollback para futuras referencias
- **Prueba** el rollback en un entorno de desarrollo primero si es posible
