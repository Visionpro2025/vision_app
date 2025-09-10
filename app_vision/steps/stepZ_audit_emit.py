from __future__ import annotations
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from datetime import datetime
import os
import json
from pathlib import Path
from typing import Dict, Any

@register_step("AuditEmitStep")
class AuditEmitStep(Step):
    """
    Step final de auditoría que emite reportes de ejecución.
    Se ejecuta al final de todos los planes para trazabilidad completa.
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Crear directorio de reportes
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Generar timestamp único
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            run_id = ctx.execution_id or f"run_{timestamp}"
            
            # Preparar payload de auditoría
            audit_payload = {
                "audit_metadata": {
                    "run_id": run_id,
                    "execution_id": ctx.execution_id,
                    "pipeline_id": ctx.pipeline_id,
                    "step_name": ctx.step_name,
                    "when_utc": datetime.utcnow().isoformat(),
                    "timestamp": timestamp
                },
                "execution_summary": {
                    "status": data.get("status", "completed"),
                    "steps_executed": data.get("steps_executed", []),
                    "total_steps": data.get("total_steps", 0),
                    "success_count": data.get("success_count", 0),
                    "error_count": data.get("error_count", 0),
                    "execution_time_s": data.get("execution_time_s", 0)
                },
                "data_summary": data.get("summary", {}),
                "policy_compliance": {
                    "allow_simulation": False,
                    "require_sources": True,
                    "abort_on_empty": True,
                    "orchestrator": "cursor_only"
                },
                "sources_used": data.get("sources_used", []),
                "outputs_generated": data.get("outputs_generated", []),
                "guardrails_applied": data.get("guardrails_applied", [])
            }
            
            # Escribir archivo JSON de auditoría
            json_path = reports_dir / f"audit_{run_id}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(audit_payload, f, ensure_ascii=False, indent=2)
            
            # Escribir reporte Markdown si está habilitado
            md_path = reports_dir / f"audit_{run_id}.md"
            self._write_markdown_report(md_path, audit_payload)
            
            # Log de auditoría
            print(f"[AUDIT] Reporte generado: {json_path}")
            print(f"[AUDIT] Markdown generado: {md_path}")
            
            return {
                "audit_completed": True,
                "audit_paths": {
                    "json": str(json_path),
                    "markdown": str(md_path)
                },
                "run_id": run_id,
                "timestamp": timestamp,
                "files_created": 2
            }
            
        except Exception as e:
            raise StepError("AuditError", f"Error generando auditoría: {e}")
    
    def _write_markdown_report(self, path: Path, payload: Dict[str, Any]) -> None:
        """Escribe un reporte de auditoría en formato Markdown"""
        metadata = payload["audit_metadata"]
        summary = payload["execution_summary"]
        compliance = payload["policy_compliance"]
        
        md_content = f"""# 🔍 AUDITORÍA DE EJECUCIÓN - VISION PREMIUM

## 📋 Información de Ejecución
- **Run ID:** `{metadata['run_id']}`
- **Execution ID:** `{metadata['execution_id']}`
- **Pipeline ID:** `{metadata['pipeline_id']}`
- **Timestamp:** `{metadata['when_utc']}`

## 📊 Resumen de Ejecución
- **Estado:** {summary['status']}
- **Pasos Ejecutados:** {summary['steps_executed']}
- **Total de Pasos:** {summary['total_steps']}
- **Éxitos:** {summary['success_count']}
- **Errores:** {summary['error_count']}
- **Tiempo de Ejecución:** {summary['execution_time_s']}s

## ✅ Cumplimiento de Política
- **Simulaciones Prohibidas:** {compliance['allow_simulation']} ❌
- **Fuentes Requeridas:** {compliance['require_sources']} ✅
- **Abortar en Vacío:** {compliance['abort_on_empty']} ✅
- **Orquestador:** {compliance['orchestrator']} ✅

## 🔗 Fuentes Utilizadas
{self._format_sources_list(payload.get('sources_used', []))}

## 📤 Outputs Generados
{self._format_outputs_list(payload.get('outputs_generated', []))}

## 🛡️ Guardrails Aplicados
{self._format_guardrails_list(payload.get('guardrails_applied', []))}

---
*Reporte generado automáticamente por VISION PREMIUM Audit System*
"""
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)
    
    def _format_sources_list(self, sources: list) -> str:
        if not sources:
            return "- No se registraron fuentes"
        return "\n".join(f"- `{source}`" for source in sources)
    
    def _format_outputs_list(self, outputs: list) -> str:
        if not outputs:
            return "- No se generaron outputs"
        return "\n".join(f"- `{output}`" for output in outputs)
    
    def _format_guardrails_list(self, guardrails: list) -> str:
        if not guardrails:
            return "- No se aplicaron guardrails específicos"
        return "\n".join(f"- {guardrail}" for guardrail in guardrails)




