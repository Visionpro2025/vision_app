# modules/pipeline_controller.py
import logging
from typing import Dict, Any
from datetime import datetime
from modules.schemas import FinalOutcome, CorrelationReport, SeriesProposal
from modules.validation_module import *
from modules.correlation_module import correlate
from modules.assembly_module import generate_series
from modules.acopio_module import acopio_masivo
from config.settings import THRESH, WEIGHTS

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineController:
    """Controlador principal del pipeline completo VISIÓN PREMIUM."""
    
    def __init__(self):
        self.current_run = None
        self.run_log = []
    
    def run_full_pipeline(self, fetch_batch_fn=None, gematria_mode="predictiva", backtest_numbers=None) -> FinalOutcome:
        """
        Ejecuta el pipeline completo del protocolo.
        
        Args:
            fetch_batch_fn: Función que devuelve lotes de noticias
            gematria_mode: "predictiva" o "backtest"
            backtest_numbers: Lista de números para modo backtest
        
        Returns:
            FinalOutcome con resultado completo
        """
        try:
            logger.info("🚀 Iniciando pipeline completo VISIÓN PREMIUM")
            self.current_run = datetime.now()
            
            # 1) Acopio masivo de noticias
            logger.info("📰 Fase 1: Acopio masivo de noticias")
            news = acopio_masivo(fetch_batch_fn, target=THRESH.min_news)
            assert_news_minimum(news)
            logger.info(f"✅ Acopio completado: {len(news)} noticias")
            
            # 2) Mapeo T70
            logger.info("🔢 Fase 2: Mapeo T70")
            t70_result = self._run_t70_layer(news)
            assert_t70(t70_result)
            logger.info(f"✅ T70 completado: {len(t70_result.categories)} categorías")
            
            # 3) Análisis Gematría
            logger.info("🔡 Fase 3: Análisis Gematría")
            gematria_result = self._run_gematria_layer(t70_result, mode=gematria_mode, numbers=backtest_numbers)
            assert_gematria(gematria_result)
            logger.info(f"✅ Gematría completado: {len(gematria_result.archetypes)} arquetipos")
            
            # 4) Análisis Subliminal
            logger.info("🧠 Fase 4: Análisis Subliminal")
            subliminal_result = self._run_subliminal_layer(news, t70_result, gematria_result)
            assert_subliminal(subliminal_result)
            logger.info(f"✅ Subliminal completado: {len(subliminal_result.messages)} mensajes")
            
            # 5) Análisis Cuántico
            logger.info("🔮 Fase 5: Análisis Cuántico")
            quantum_result = self._run_quantum_layer(news, t70_result, gematria_result)
            assert_quantum(quantum_result)
            logger.info(f"✅ Cuántico completado: {len(quantum_result.states)} estados")
            
            # 6) Correlación entre capas
            logger.info("🔗 Fase 6: Correlación entre capas")
            correlation = correlate(t70_result, gematria_result, subliminal_result, quantum_result)
            logger.info(f"✅ Correlación completada: score global {correlation.global_score:.2%}")
            
            # 7) Ensamblaje de series
            logger.info("⚙️ Fase 7: Ensamblaje de series")
            series = generate_series(t70_result, gematria_result, subliminal_result, quantum_result, k=5)
            logger.info(f"✅ Ensamblaje completado: {len(series)} series generadas")
            
            # 8) Resultado final
            logger.info("📊 Fase 8: Generando resultado final")
            outcome = self._generate_final_outcome(
                series, correlation, t70_result, gematria_result, 
                subliminal_result, quantum_result
            )
            logger.info("✅ Pipeline completo finalizado exitosamente")
            
            return outcome
            
        except Exception as e:
            logger.error(f"❌ Error en pipeline: {str(e)}")
            raise
    
    def _run_t70_layer(self, news) -> Any:
        """Ejecuta la capa T70."""
        # TODO: Implementar llamada real al módulo T70
        # Por ahora retornamos mock data
        return type('T70Result', (), {
            'categories': {'economia': 10, 'politica': 8, 'seguridad': 6},
            'keyword_map': {'economia': 15, 'politica': 23, 'seguridad': 42}
        })()
    
    def _run_gematria_layer(self, t70_result, mode="predictiva", numbers=None) -> Any:
        """Ejecuta la capa Gematría."""
        # TODO: Implementar llamada real al módulo Gematría
        # Por ahora retornamos mock data
        return type('GematriaResult', (), {
            'hebrew_conversion': ['א', 'ב', 'ג'],
            'numbers': [1, 2, 3],
            'archetypes': ['Sabio', 'Héroe', 'Sombra'],
            'seed': type('GematriaSeed', (), {'mode': mode, 'source_info': {}})()
        })()
    
    def _run_subliminal_layer(self, news, t70_result, gematria_result) -> Any:
        """Ejecuta la capa Subliminal."""
        # TODO: Implementar llamada real al módulo Subliminal
        # Por ahora retornamos mock data
        return type('SubliminalResult', (), {
            'messages': ['Mensaje subliminal 1', 'Mensaje subliminal 2'],
            'impact_scores': [0.8, 0.6],
            'features': {'feature1': 0.7, 'feature2': 0.5}
        })()
    
    def _run_quantum_layer(self, news, t70_result, gematria_result) -> Any:
        """Ejecuta la capa Cuántica."""
        # TODO: Implementar llamada real al módulo Cuántico
        # Por ahora retornamos mock data
        return type('QuantumResult', (), {
            'states': {'estado1', 'estado2', 'estado3'},
            'entanglements': [('estado1', 'estado2', 0.8)],
            'probabilities': {'estado1': 0.4, 'estado2': 0.3, 'estado3': 0.3}
        })()
    
    def _generate_final_outcome(self, series, correlation, t70_result, gematria_result, 
                               subliminal_result, quantum_result) -> FinalOutcome:
        """Genera el resultado final del protocolo."""
        
        # Determinar patrones dominantes
        dominant_category = max(t70_result.categories.items(), key=lambda x: x[1])[0]
        dominant_archetype = gematria_result.archetypes[0] if gematria_result.archetypes else "Desconocido"
        dominant_pattern = f"Patrón {dominant_category}-{dominant_archetype}"
        
        # Mensaje subliminal dominante
        subliminal_msg = subliminal_result.messages[0] if subliminal_result.messages else None
        
        # Estado cuántico dominante
        quantum_state = max(quantum_result.probabilities.items(), key=lambda x: x[1])[0] if quantum_result.probabilities else None
        
        return FinalOutcome(
            proposals=series,
            correlation=correlation,
            dominant_pattern=dominant_pattern,
            dominant_category=dominant_category,
            dominant_archetype=dominant_archetype,
            subliminal_msg=subliminal_msg,
            quantum_state=quantum_state
        )

# Instancia global del controlador
pipeline_controller = PipelineController()

def run_full_pipeline(**kwargs) -> FinalOutcome:
    """Función de alto nivel para ejecutar el pipeline completo."""
    return pipeline_controller.run_full_pipeline(**kwargs)









