#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Métricas para el Sistema de Aprendizaje por Sorteo (SLL) de VISIÓN Premium
Calcula Hit@k, Brier Score, ECE y ablación por familia de señales
"""

import json
import numpy as np
from typing import Dict, List, Set, Any, Tuple
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SLLMetrics:
    """Calculador de métricas para aprendizaje por sorteo"""
    
    def __init__(self):
        pass
    
    def hit_at_k(self, y_true: Set[int], y_pred: List[int], k: int = 3) -> float:
        """
        Calcula Hit@k: si al menos un número real está en los top-k predichos
        
        Args:
            y_true: Conjunto de números reales del sorteo
            y_pred: Lista ordenada de números predichos (prioridad descendente)
            k: Top-k a considerar
        
        Returns:
            Float entre 0.0 y 1.0
        """
        try:
            if not y_true or not y_pred:
                return 0.0
            
            # Tomar top-k de predicciones
            top_k = set(y_pred[:k])
            
            # Verificar si hay intersección
            hits = len(y_true.intersection(top_k))
            
            return 1.0 if hits > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculando Hit@{k}: {e}")
            return 0.0
    
    def hit_at_k_multiple(self, y_true: Set[int], y_pred: List[int], k_values: List[int] = [1, 3, 5]) -> Dict[str, float]:
        """Calcula Hit@k para múltiples valores de k"""
        try:
            results = {}
            for k in k_values:
                results[f"hit@{k}"] = self.hit_at_k(y_true, y_pred, k)
            return results
        except Exception as e:
            logger.error(f"Error calculando Hit@k múltiple: {e}")
            return {f"hit@{k}": 0.0 for k in k_values}
    
    def brier_score(self, probs: List[float], outcomes: List[int]) -> float:
        """
        Calcula Brier Score para calibración de probabilidades
        
        Args:
            probs: Lista de probabilidades predichas
            outcomes: Lista de resultados reales (0 o 1)
        
        Returns:
            Brier Score (menor es mejor)
        """
        try:
            if len(probs) != len(outcomes):
                logger.error("Longitudes de probs y outcomes no coinciden")
                return float('inf')
            
            if not probs:
                return 0.0
            
            # Brier Score = (1/N) * Σ(p_i - o_i)²
            brier = np.mean([(p - o) ** 2 for p, o in zip(probs, outcomes)])
            return float(brier)
            
        except Exception as e:
            logger.error(f"Error calculando Brier Score: {e}")
            return float('inf')
    
    def expected_calibration_error(self, probs: List[float], outcomes: List[int], n_bins: int = 10) -> float:
        """
        Calcula Expected Calibration Error
        
        Args:
            probs: Lista de probabilidades predichas
            outcomes: Lista de resultados reales (0 o 1)
            n_bins: Número de bins para discretización
        
        Returns:
            ECE (menor es mejor)
        """
        try:
            if len(probs) != len(outcomes):
                logger.error("Longitudes de probs y outcomes no coinciden")
                return float('inf')
            
            if not probs:
                return 0.0
            
            # Crear bins
            bin_boundaries = np.linspace(0, 1, n_bins + 1)
            bin_lowers = bin_boundaries[:-1]
            bin_uppers = bin_boundaries[1:]
            
            ece = 0.0
            for bin_lower, bin_upper in zip(bin_lowers, bin_uppers):
                # Encontrar muestras en este bin
                in_bin = np.logical_and(probs >= bin_lower, probs < bin_upper)
                bin_size = np.sum(in_bin)
                
                if bin_size > 0:
                    bin_probs = np.array(probs)[in_bin]
                    bin_outcomes = np.array(outcomes)[in_bin]
                    
                    # Probabilidad promedio del bin
                    bin_prob = np.mean(bin_probs)
                    
                    # Frecuencia real del bin
                    bin_freq = np.mean(bin_outcomes)
                    
                    # Contribución al ECE
                    ece += (bin_size / len(probs)) * abs(bin_prob - bin_freq)
            
            return float(ece)
            
        except Exception as e:
            logger.error(f"Error calculando ECE: {e}")
            return float('inf')
    
    def coverage_at_confidence(self, probs: List[float], outcomes: List[int], confidence_threshold: float = 0.5) -> Dict[str, float]:
        """
        Calcula cobertura vs confianza
        
        Args:
            probs: Lista de probabilidades predichas
            outcomes: Lista de resultados reales (0 o 1)
            confidence_threshold: Umbral de confianza
        
        Returns:
            Dict con métricas de cobertura
        """
        try:
            if len(probs) != len(outcomes):
                logger.error("Longitudes de probs y outcomes no coinciden")
                return {"coverage": 0.0, "accuracy": 0.0, "confidence": 0.0}
            
            if not probs:
                return {"coverage": 0.0, "accuracy": 0.0, "confidence": 0.0}
            
            # Filtrar por confianza
            confident_mask = np.array(probs) >= confidence_threshold
            confident_probs = np.array(probs)[confident_mask]
            confident_outcomes = np.array(outcomes)[confident_mask]
            
            if len(confident_probs) == 0:
                return {"coverage": 0.0, "accuracy": 0.0, "confidence": 0.0}
            
            # Cobertura: qué fracción de predicciones supera el umbral
            coverage = len(confident_probs) / len(probs)
            
            # Precisión: de las predicciones confiadas, cuántas son correctas
            accuracy = np.mean(confident_outcomes)
            
            # Confianza promedio de las predicciones confiadas
            avg_confidence = np.mean(confident_probs)
            
            return {
                "coverage": float(coverage),
                "accuracy": float(accuracy),
                "confidence": float(avg_confidence)
            }
            
        except Exception as e:
            logger.error(f"Error calculando cobertura vs confianza: {e}")
            return {"coverage": 0.0, "accuracy": 0.0, "confidence": 0.0}
    
    def ablation_analysis(self, base_features: Dict[str, Any], base_score: float, 
                          feature_families: Dict[str, List[str]], evaluator_func) -> List[Dict[str, Any]]:
        """
        Análisis de ablación: qué pasa si apagamos cada familia de señales
        
        Args:
            base_features: Features completos del modelo
            base_score: Score base con todas las señales
            feature_families: Dict con familias de señales
            evaluator_func: Función que evalúa features y retorna score
        
        Returns:
            Lista de impactos por familia
        """
        try:
            ablation_results = []
            
            for family_name, feature_keys in feature_families.items():
                # Crear copia de features sin esta familia
                ablated_features = base_features.copy()
                
                # Apagar señales de esta familia
                for key in feature_keys:
                    if key in ablated_features:
                        if isinstance(ablated_features[key], (list, np.ndarray)):
                            ablated_features[key] = [0.0] * len(ablated_features[key])
                        else:
                            ablated_features[key] = 0.0
                
                # Evaluar sin esta familia
                try:
                    ablated_score = evaluator_func(ablated_features)
                    impact = base_score - ablated_score
                    impact_pct = (impact / base_score * 100) if base_score != 0 else 0
                    
                    ablation_results.append({
                        "family": family_name,
                        "features_removed": feature_keys,
                        "base_score": base_score,
                        "ablated_score": ablated_score,
                        "impact": impact,
                        "impact_percentage": impact_pct,
                        "status": "positive" if impact > 0 else "negative"
                    })
                    
                except Exception as e:
                    logger.warning(f"Error evaluando ablación para familia {family_name}: {e}")
                    ablation_results.append({
                        "family": family_name,
                        "features_removed": feature_keys,
                        "base_score": base_score,
                        "ablated_score": None,
                        "impact": None,
                        "impact_percentage": None,
                        "status": "error"
                    })
            
            # Ordenar por impacto absoluto
            ablation_results.sort(key=lambda x: abs(x.get("impact", 0)) if x.get("impact") is not None else 0, reverse=True)
            
            return ablation_results
            
        except Exception as e:
            logger.error(f"Error en análisis de ablación: {e}")
            return []
    
    def calculate_all_metrics(self, y_true: Set[int], y_pred: List[int], 
                             probs: List[float] = None, features: Dict[str, Any] = None,
                             feature_families: Dict[str, List[str]] = None,
                             evaluator_func = None) -> Dict[str, Any]:
        """
        Calcula todas las métricas disponibles
        
        Args:
            y_true: Números reales del sorteo
            y_pred: Números predichos ordenados
            probs: Probabilidades predichas (opcional)
            features: Features del modelo (opcional)
            feature_families: Familias de señales para ablación (opcional)
            evaluator_func: Función evaluadora para ablación (opcional)
        
        Returns:
            Dict con todas las métricas calculadas
        """
        try:
            metrics = {}
            
            # Hit@k
            metrics.update(self.hit_at_k_multiple(y_true, y_pred))
            
            # Si hay probabilidades, calcular métricas de calibración
            if probs and len(probs) == len(y_pred):
                # Convertir a formato binario para métricas
                binary_outcomes = [1 if pred in y_true else 0 for pred in y_pred]
                
                metrics["brier_score"] = self.brier_score(probs, binary_outcomes)
                metrics["ece"] = self.expected_calibration_error(probs, binary_outcomes)
                metrics["coverage_confidence"] = self.coverage_at_confidence(probs, binary_outcomes)
            
            # Ablación si hay features y evaluador
            if features and feature_families and evaluator_func:
                # Calcular score base
                try:
                    base_score = evaluator_func(features)
                    metrics["base_score"] = base_score
                    
                    # Análisis de ablación
                    ablation_results = self.ablation_analysis(features, base_score, feature_families, evaluator_func)
                    metrics["ablation"] = ablation_results
                    
                except Exception as e:
                    logger.warning(f"No se pudo calcular ablación: {e}")
                    metrics["ablation"] = []
            
            # Estadísticas básicas
            metrics["total_predictions"] = len(y_pred)
            metrics["total_real"] = len(y_true)
            metrics["hits_total"] = len(set(y_pred).intersection(y_true))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculando métricas completas: {e}")
            return {"error": str(e)}
    
    def save_metrics(self, metrics: Dict[str, Any], output_path: str) -> bool:
        """Guarda métricas en archivo JSON"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Métricas guardadas en {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando métricas: {e}")
            return False
    
    def load_metrics(self, input_path: str) -> Dict[str, Any]:
        """Carga métricas desde archivo JSON"""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                logger.warning(f"Archivo de métricas no encontrado: {input_path}")
                return {}
            
            with open(input_file, 'r', encoding='utf-8') as f:
                metrics = json.load(f)
            
            logger.info(f"Métricas cargadas desde {input_path}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error cargando métricas: {e}")
            return {}

# Funciones de conveniencia
def hit_at_k(y_true: Set[int], y_pred: List[int], k: int = 3) -> float:
    """Calcula Hit@k"""
    calculator = SLLMetrics()
    return calculator.hit_at_k(y_true, y_pred, k)

def calculate_all_metrics(y_true: Set[int], y_pred: List[int], **kwargs) -> Dict[str, Any]:
    """Calcula todas las métricas disponibles"""
    calculator = SLLMetrics()
    return calculator.calculate_all_metrics(y_true, y_pred, **kwargs)








