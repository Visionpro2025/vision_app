# ============================================
# 📌 STEP 2B: VALIDACIÓN Y AUDITORÍA DE NOTICIAS
# Step de FSM que valida fechas, dominios y deduplicación
# ============================================

from __future__ import annotations
from typing import Dict, Any, List
import os
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.news_guarded import validate_news, save_report

@register_step("NewsGuardedStep")
class NewsGuardedStep(Step):
    """
    Step que valida noticias con Protocolo de Confianza:
    - Dominios permitidos (whitelist)
    - Fechas reales y recientes
    - Deduplicación por similitud
    - Evidencia exportable
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Espera entradas de un paso previo (p.ej. step2_news_fetch)
        raw_urls: List[str] = data.get("raw_news_urls") or []
        policy_path: str = data.get("policy_path") or "plans/news_policy.yaml"

        if not raw_urls:
            raise StepError("InputError", "No se recibieron URLs de noticias (raw_news_urls).")

        # Directorio de evidencia
        evidence_dir = os.path.join(ctx.state_dir, ctx.run_id, "evidence", "html")
        
        # Validar noticias
        report = validate_news(raw_urls, policy_path, evidence_dir)

        # Guardar reporte
        report_path = os.path.join("reports", f"news_evidence_{ctx.run_id}.json")
        save_report(report, report_path)

        # Verificar evidencia suficiente
        if report.get("status") != "OK":
            raise StepError(
                report.get("error_kind", "EvidenceError"), 
                report.get("error_detail", "Fallo de evidencia")
            )

        # Solo devolvemos lo necesario para el resto del pipeline
        valid_urls = [v["final_url"] for v in report["valid"]]
        
        return {
            "valid_news_urls": valid_urls,
            "news_report_path": report_path,
            "metrics": report["metrics"],
            "evidence_count": len(valid_urls),
            "rejected_count": report["metrics"]["rejected_count"]
        }




