# ============================================
# 📌 STEP 2C: VERIFICACIÓN AVANZADA DE CONTENIDO
# Detecta información ilegítima, falsa y generada por IA
# ============================================

from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.content_verification import ContentVerificationEngine
from app_vision.modules.role_guard import enforce_orchestrator_role

@register_step("ContentVerificationStep")
class ContentVerificationStep(Step):
    """
    Step que verifica contenido avanzado para detectar:
    - Información generada por IA
    - Contenido falsificado o inventado
    - Inconsistencias temporales
    - Metadatos corruptos
    - Fuentes no confiables
    """
    
    def __init__(self):
        self.verification_engine = ContentVerificationEngine()
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Verificar rol de orquestador
        enforce_orchestrator_role(ctx, data, "ContentVerificationStep")
        
        # Obtener artículos seleccionados del paso anterior
        selected_articles = data.get("selected_articles") or []
        if not selected_articles:
            raise StepError("InputError", "No hay artículos seleccionados para verificar.")
        
        # Verificar contenido
        verification_results = self.verification_engine.verify_content(selected_articles)
        
        # Separar artículos legítimos de los ilegítimos
        legitimate_articles = []
        illegitimate_articles = []
        
        for i, (article, result) in enumerate(zip(selected_articles, verification_results)):
            if result.is_legitimate:
                legitimate_articles.append(article)
            else:
                illegitimate_articles.append({
                    "article": article,
                    "verification_result": result.__dict__,
                    "rejection_reasons": result.verification_reasons
                })
        
        # Calcular métricas
        total_articles = len(selected_articles)
        legitimate_count = len(legitimate_articles)
        illegitimate_count = len(illegitimate_articles)
        
        # Análisis de razones de rechazo
        rejection_analysis = {
            "ai_generated": sum(1 for r in verification_results if r.ai_detection),
            "suspicious_content": sum(1 for r in verification_results if not r.temporal_coherence),
            "metadata_corrupted": sum(1 for r in verification_results if not r.metadata_integrity),
            "low_source_reliability": sum(1 for r in verification_results if r.source_reliability < 0.5)
        }
        
        # Verificar si hay suficientes artículos legítimos
        min_legitimate = data.get("min_legitimate_articles", 10)
        if legitimate_count < min_legitimate:
            raise StepError(
                "InsufficientLegitimateContent",
                f"Solo {legitimate_count} artículos legítimos de {total_articles} "
                f"(mínimo requerido: {min_legitimate}). "
                f"Razones: {rejection_analysis}"
            )
        
        # Generar reporte de verificación
        verification_report = {
            "total_verified": total_articles,
            "legitimate_count": legitimate_count,
            "illegitimate_count": illegitimate_count,
            "legitimacy_rate": legitimate_count / total_articles if total_articles > 0 else 0,
            "rejection_analysis": rejection_analysis,
            "verification_details": [
                {
                    "title": r.article.get("title", "Sin título"),
                    "is_legitimate": r.is_legitimate,
                    "confidence_score": r.confidence_score,
                    "ai_detection": r.ai_detection,
                    "temporal_coherence": r.temporal_coherence,
                    "metadata_integrity": r.metadata_integrity,
                    "source_reliability": r.source_reliability,
                    "reasons": r.verification_reasons
                }
                for r in verification_results
            ]
        }
        
        return {
            "legitimate_articles": legitimate_articles,
            "illegitimate_articles": illegitimate_articles,
            "verification_report": verification_report,
            "verification_passed": True,
            "legitimacy_confidence": sum(r.confidence_score for r in verification_results) / len(verification_results) if verification_results else 0
        }





