# ============================================
# 📌 STEP CUÁNTICO DE NOTICIAS
# Análisis cuántico de noticias con simulación cuántica
# ============================================

from __future__ import annotations
from typing import Dict, Any, List
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.quantum_news import QuantumNewsAnalyzer
from app_vision.modules.role_guard import enforce_orchestrator_role

@register_step("QuantumNewsStep")
class QuantumNewsStep(Step):
    """
    Step que aplica análisis cuántico de noticias:
    - Simulación cuántica de relevancia
    - Algoritmos cuánticos para ranking
    - Interferencia de patrones semánticos
    - Evolución temporal cuántica
    """
    
    def __init__(self):
        self.quantum_analyzer = QuantumNewsAnalyzer()
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Verificar rol de orquestador
        enforce_orchestrator_role(ctx, data, "QuantumNewsStep")
        
        # Obtener artículos validados
        valid_articles = data.get("valid_news_urls", [])
        if not valid_articles:
            raise StepError("InputError", "No hay artículos válidos para análisis cuántico de noticias.")
        
        # Obtener guía subliminal
        subliminal_guidance = {
            "topics": data.get("subliminal_topics", []),
            "keywords_used": data.get("subliminal_keywords", []),
            "families_used": data.get("subliminal_families", [])
        }
        
        # Obtener top_k
        top_k = int(data.get("top_k", 24))
        
        try:
            # Aplicar análisis cuántico de noticias
            quantum_result = self.quantum_analyzer.analyze_quantum_news(valid_articles, subliminal_guidance, top_k)
            
            return {
                "quantum_selected_articles": quantum_result.quantum_selected_articles,
                "quantum_ranking_scores": quantum_result.quantum_ranking_scores,
                "quantum_relevance_scores": quantum_result.quantum_relevance_scores,
                "quantum_semantic_coherence": quantum_result.quantum_semantic_coherence,
                "quantum_temporal_evolution": quantum_result.quantum_temporal_evolution,
                "quantum_interference_analysis": quantum_result.quantum_interference_analysis,
                "quantum_entanglement_network": quantum_result.quantum_entanglement_network.tolist()
            }
            
        except Exception as e:
            raise StepError("QuantumNewsAnalysisError", f"Error en análisis cuántico de noticias: {e}")



