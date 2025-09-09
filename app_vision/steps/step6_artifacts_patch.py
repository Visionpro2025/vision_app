# ============================================
# 🚀 STEP PATCH: ARTIFACTS MEJORADO
# Exporta un resumen legible de noticias seleccionadas, válidas y rechazadas
# No falla el run si faltan partes; muestra lo que haya disponible
# ============================================

from __future__ import annotations
from typing import Dict, Any, List
import os, json, textwrap
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step

@register_step("ArtifactsStepPatch")
class ArtifactsStepPatch(Step):
    """
    Exporta un resumen legible de noticias:
      - Seleccionadas (post-filtro social/emoción)
      - Válidas (tras validación de fechas/domino)
      - Rechazadas (con razón)
    No falla el run si faltan partes; muestra lo que haya.
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Entradas opcionales (usa lo que exista)
        selected = data.get("news_selected") or []
        metrics  = data.get("news_metrics")  or {}
        guidance = data.get("guidance_used") or {}
        # Opcionalmente, ruta al reporte crudo del validador
        news_report_path = data.get("news_report_path")

        valid, rejected = [], []
        if news_report_path and os.path.exists(news_report_path):
            with open(news_report_path, "r", encoding="utf-8") as f:
                rep = json.load(f)
            valid = rep.get("valid", [])
            rejected = rep.get("rejected", [])

        # Markdown de salida
        md = ["# Informe de Noticias (Auditado)"]
        md.append("")
        md.append("## Seleccionadas (tras filtro social/emoción)")
        if selected:
            for i, a in enumerate(selected, 1):
                md.append(f"{i}. [{a.get('title','(sin título)')}]({a.get('final_url', a.get('url'))}) "
                          f"— bucket: *{a.get('bucket','?')}* — score: {round(a.get('score',0),2)}")
        else:
            md.append("No hay seleccionadas. Revisa filtros o guía.")

        md.append("")
        md.append("## Válidas (tras validación de fecha/dominio)")
        if valid:
            for i, v in enumerate(valid[:50], 1):
                md.append(f"{i}. [{v.get('title','(sin título)')}]({v.get('final_url', v.get('url'))}) "
                          f"— fecha: {v.get('date_iso')} — dominio: {v.get('domain')}")
        else:
            md.append("No hay válidas registradas por el validador.")

        md.append("")
        md.append("## Rechazadas (con motivo)")
        if rejected:
            # Muestra 50 máx para no explotar el reporte
            for i, r in enumerate(rejected[:50], 1):
                md.append(f"{i}. {r.get('title','(sin título)')} — dominio: {r.get('domain')} "
                          f"— motivo: *{r.get('drop_reason')}* — url: {r.get('final_url', r.get('url'))}")
        else:
            md.append("No hay rechazadas (o no se cargó el reporte).")

        md.append("")
        md.append("## Métricas")
        md.append(f"- selected.kept: {metrics.get('kept','?')}")
        md.append(f"- metrics.buckets: {metrics.get('buckets',{})}")
        md.append("")
        md.append("## Guía usada (mensaje del sorteo anterior)")
        md.append(f"- terms: {', '.join(guidance.get('guide_terms', [])) or '(vacío)'}")

        # Guardar
        os.makedirs("reports", exist_ok=True)
        out_md = os.path.join("reports", f"news_selected_{ctx.run_id}.md")
        with open(out_md, "w", encoding="utf-8") as f:
            f.write("\n".join(md))

        return {
            "news_summary_md": out_md,
            "selected_count": len(selected),
            "valid_count": len(valid),
            "rejected_count": len(rejected)
        }



