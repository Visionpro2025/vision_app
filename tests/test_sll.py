#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests básicos para el Sistema de Aprendizaje por Sorteo (SLL)
"""

import unittest
import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from services.sll_metrics import SLLMetrics
    from services.sll_proposals import SLLProposalGenerator
    from services.lexicon import CorpusLexiconBuilder
    from services.news_enricher import NewsEnricher
except ImportError as e:
    print(f"Error importando servicios para tests: {e}")
    sys.exit(1)

class TestSLLMetrics(unittest.TestCase):
    """Tests para el servicio de métricas SLL"""
    
    def setUp(self):
        """Configuración inicial"""
        self.metrics = SLLMetrics()
        
        # Datos de prueba
        self.y_true = {5, 12, 23, 45, 67}
        self.y_pred = [5, 23, 12, 67, 45, 89, 34, 78, 91, 15]
        self.probs = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05]
    
    def test_hit_at_k(self):
        """Test de cálculo de Hit@k"""
        # Hit@1 debería ser 1.0 (el primer número está en y_true)
        hit_1 = self.metrics.hit_at_k(self.y_true, self.y_pred, 1)
        self.assertEqual(hit_1, 1.0)
        
        # Hit@3 debería ser 1.0 (todos los primeros 3 están en y_true)
        hit_3 = self.metrics.hit_at_k(self.y_true, self.y_pred, 3)
        self.assertEqual(hit_3, 1.0)
        
        # Hit@5 debería ser 1.0 (todos los primeros 5 están en y_true)
        hit_5 = self.metrics.hit_at_k(self.y_true, self.y_pred, 5)
        self.assertEqual(hit_5, 1.0)
    
    def test_hit_at_k_multiple(self):
        """Test de cálculo de Hit@k múltiple"""
        results = self.metrics.hit_at_k_multiple(self.y_true, self.y_pred, [1, 3, 5])
        
        self.assertIn("hit@1", results)
        self.assertIn("hit@3", results)
        self.assertIn("hit@5", results)
        
        self.assertEqual(results["hit@1"], 1.0)
        self.assertEqual(results["hit@3"], 1.0)
        self.assertEqual(results["hit@5"], 1.0)
    
    def test_brier_score(self):
        """Test de cálculo de Brier Score"""
        # Crear outcomes binarios
        outcomes = [1 if pred in self.y_true else 0 for pred in self.y_pred]
        
        brier = self.metrics.brier_score(self.probs, outcomes)
        
        # Brier score debe ser un float válido
        self.assertIsInstance(brier, float)
        self.assertGreaterEqual(brier, 0.0)
        self.assertLessEqual(brier, 1.0)
    
    def test_expected_calibration_error(self):
        """Test de cálculo de ECE"""
        outcomes = [1 if pred in self.y_true else 0 for pred in self.y_pred]
        
        ece = self.metrics.expected_calibration_error(self.probs, outcomes)
        
        # ECE debe ser un float válido
        self.assertIsInstance(ece, float)
        self.assertGreaterEqual(ece, 0.0)
    
    def test_coverage_at_confidence(self):
        """Test de cobertura vs confianza"""
        outcomes = [1 if pred in self.y_true else 0 for pred in self.y_pred]
        
        cc = self.metrics.coverage_at_confidence(self.probs, outcomes, confidence_threshold=0.5)
        
        self.assertIn("coverage", cc)
        self.assertIn("accuracy", cc)
        self.assertIn("confidence", cc)
        
        # Todos los valores deben ser floats entre 0 y 1
        for value in cc.values():
            self.assertIsInstance(value, float)
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

class TestSLLProposals(unittest.TestCase):
    """Tests para el generador de propuestas SLL"""
    
    def setUp(self):
        """Configuración inicial"""
        self.proposal_generator = SLLProposalGenerator()
        
        # Métricas de prueba
        self.test_metrics = {
            "hit@1": 0.0,
            "hit@3": 0.33,
            "hit@5": 0.67,
            "brier_score": 0.28,
            "ece": 0.15,
            "coverage_confidence": {
                "coverage": 0.45,
                "accuracy": 0.62,
                "confidence": 0.58
            }
        }
        
        # Resultados de ablación de prueba
        self.test_ablation = [
            {
                "family": "S_gematria",
                "impact_percentage": 25.5,
                "status": "positive"
            },
            {
                "family": "S_news_sem",
                "impact_percentage": -12.3,
                "status": "negative"
            }
        ]
    
    def test_generate_proposals(self):
        """Test de generación de propuestas"""
        proposals = self.proposal_generator.generate_proposals(
            self.test_metrics,
            self.test_ablation
        )
        
        # Debe generar al menos una propuesta
        self.assertGreater(len(proposals), 0)
        
        # Cada propuesta debe tener campos requeridos
        for proposal in proposals:
            self.assertIn("id", proposal)
            self.assertIn("tipo", proposal)
            self.assertIn("target", proposal)
            self.assertIn("action", proposal)
            self.assertIn("justification", proposal)
            self.assertIn("impact", proposal)
            self.assertIn("category", proposal)
            self.assertIn("priority", proposal)
    
    def test_proposal_priority_calculation(self):
        """Test de cálculo de prioridad de propuestas"""
        proposals = self.proposal_generator.generate_proposals(
            self.test_metrics,
            self.test_ablation
        )
        
        for proposal in proposals:
            priority = proposal.get("priority", 0)
            
            # Prioridad debe ser float entre 0 y 1
            self.assertIsInstance(priority, float)
            self.assertGreaterEqual(priority, 0.0)
            self.assertLessEqual(priority, 1.0)
    
    def test_proposal_saving_and_loading(self):
        """Test de guardado y carga de propuestas"""
        proposals = self.proposal_generator.generate_proposals(
            self.test_metrics,
            self.test_ablation
        )
        
        # Guardar propuestas
        test_file = "test_proposals.jsonl"
        success = self.proposal_generator.save_proposals(proposals, test_file)
        self.assertTrue(success)
        
        # Cargar propuestas
        loaded_proposals = self.proposal_generator.load_proposals(test_file)
        self.assertEqual(len(loaded_proposals), len(proposals))
        
        # Limpiar archivo de prueba
        try:
            os.remove(test_file)
        except:
            pass

class TestCorpusLexiconBuilder(unittest.TestCase):
    """Tests para el constructor de léxicos del corpus"""
    
    def setUp(self):
        """Configuración inicial"""
        self.lexicon_builder = CorpusLexiconBuilder()
    
    def test_build_lexicons(self):
        """Test de construcción de léxicos"""
        lexicons = self.lexicon_builder.build_lexicons()
        
        # Debe tener los dominios esperados
        self.assertIn("jung", lexicons)
        self.assertIn("subliminal", lexicons)
        self.assertIn("gematria", lexicons)
        
        # Cada dominio debe tener categorías
        for domain, categories in lexicons.items():
            self.assertIsInstance(categories, dict)
            self.assertGreater(len(categories), 0)
            
            for category, terms in categories.items():
                self.assertIsInstance(terms, list)
                self.assertGreater(len(terms), 0)
    
    def test_get_domain_lexicon(self):
        """Test de obtención de léxico por dominio"""
        jung_terms = self.lexicon_builder.get_domain_lexicon("jung")
        
        self.assertIsInstance(jung_terms, list)
        self.assertGreater(len(jung_terms), 0)
        
        # Debe contener términos esperados
        expected_terms = ["sombra", "persona", "arquetipo"]
        for term in expected_terms:
            self.assertIn(term, jung_terms)
    
    def test_search_terms(self):
        """Test de búsqueda de términos"""
        results = self.lexicon_builder.search_terms("sombra")
        
        # Debe encontrar resultados
        self.assertGreater(len(results), 0)
        
        # Debe contener el dominio jung
        self.assertIn("jung", results)
        
        # Debe contener el término buscado
        self.assertIn("sombra", results["jung"])

class TestNewsEnricher(unittest.TestCase):
    """Tests para el enriquecedor de noticias"""
    
    def setUp(self):
        """Configuración inicial"""
        self.enricher = NewsEnricher()
        
        # Texto de prueba
        self.test_text = "Este documento aborda aspectos de psicología analítica y operaciones psicológicas en el contexto de defensa nacional."
    
    def test_detect_frames(self):
        """Test de detección de frames"""
        frame_analysis = self.enricher.detect_frames(self.test_text)
        
        # Debe tener la estructura esperada
        self.assertIn("frames", frame_analysis)
        self.assertIn("total_frames_detected", frame_analysis)
        self.assertIn("overall_confidence", frame_analysis)
        
        # Debe detectar frames
        frames = frame_analysis["frames"]
        self.assertIn("priming", frames)
        self.assertIn("framing", frames)
        self.assertIn("nudge", frames)
        self.assertIn("double_bind", frames)
        
        # Cada frame debe tener la estructura correcta
        for frame_info in frames.values():
            self.assertIn("detected", frame_info)
            self.assertIn("pattern_count", frame_info)
            self.assertIn("patterns", frame_info)
            self.assertIn("confidence", frame_info)
    
    def test_expand_query(self):
        """Test de expansión de queries"""
        base_query = "psicología analítica"
        
        expansion = self.enricher.expand_query(base_query)
        
        # Debe tener la estructura esperada
        self.assertIn("original_query", expansion)
        self.assertIn("expanded_query", expansion)
        self.assertIn("expansions", expansion)
        self.assertIn("domain", expansion)
        
        # Query original debe mantenerse
        self.assertEqual(expansion["original_query"], base_query)
    
    def test_rerank_news(self):
        """Test de reranking de noticias"""
        news_items = [
            {
                "title": "Psicología analítica en defensa",
                "content": "Documento sobre operaciones psicológicas",
                "summary": "Análisis de técnicas subliminales"
            },
            {
                "title": "Noticia general",
                "content": "Contenido sin términos especializados",
                "summary": "Resumen genérico"
            }
        ]
        
        reranked = self.enricher.rerank_news(news_items)
        
        # Debe mantener el número de items
        self.assertEqual(len(reranked), len(news_items))
        
        # Debe tener scores
        for item in reranked:
            self.assertIn("_lexicon_score", item)
            self.assertIn("_frame_score", item)
            self.assertIn("_clickbait_penalty", item)
            self.assertIn("_total_score", item)
            
            # Scores deben ser floats entre 0 y 1
            for score_key in ["_lexicon_score", "_frame_score", "_total_score"]:
                score = item[score_key]
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0.0)
                self.assertLessEqual(score, 1.0)

def run_tests():
    """Ejecuta todos los tests"""
    # Crear suite de tests
    test_suite = unittest.TestSuite()
    
    # Agregar tests
    test_suite.addTest(unittest.makeSuite(TestSLLMetrics))
    test_suite.addTest(unittest.makeSuite(TestSLLProposals))
    test_suite.addTest(unittest.makeSuite(TestCorpusLexiconBuilder))
    test_suite.addTest(unittest.makeSuite(TestNewsEnricher))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Retornar código de salida
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    # Ejecutar tests
    exit_code = run_tests()
    
    print("\n" + "="*50)
    if exit_code == 0:
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("="*50)
    
    sys.exit(exit_code)







