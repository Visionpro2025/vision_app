#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de propuestas automáticas para el Sistema de Aprendizaje por Sorteo (SLL)
Analiza métricas y ablación para sugerir cambios concretos en el sistema
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SLLProposalGenerator:
    """Generador de propuestas automáticas basadas en análisis SLL"""
    
    def __init__(self):
        # Reglas de generación de propuestas
        self.proposal_rules = {
            "weight_adjustment": {
                "threshold": 10.0,  # % de impacto para sugerir ajuste
                "delta_range": (0.05, 0.25),  # Rango de ajuste
                "max_delta": 0.3  # Máximo ajuste permitido
            },
            "ensemble_activation": {
                "threshold": 15.0,  # % de impacto para activar ensemble
                "min_confidence": 0.6  # Confianza mínima para activar
            },
            "query_expansion": {
                "coverage_threshold": 0.3,  # Cobertura baja para expandir queries
                "lexicon_boost": 0.2  # Boost por léxico del corpus
            },
            "source_addition": {
                "jurisdiction_gaps": ["jur:us", "jur:uk", "jur:ru", "jur:eu"],
                "source_type_gaps": ["src:foia", "src:academic", "src:policy"]
            },
            "safety_clips": {
                "overweight_threshold": 0.4,  # Peso excesivo para aplicar clip
                "clip_factor": 0.25  # Factor de recorte
            }
        }
    
    def generate_proposals(self, metrics: Dict[str, Any], ablation_results: List[Dict[str, Any]] = None,
                          drift_analysis: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Genera propuestas automáticas basadas en métricas y análisis
        
        Args:
            metrics: Métricas calculadas del sorteo
            ablation_results: Resultados del análisis de ablación
            drift_analysis: Análisis de drift de features
        
        Returns:
            Lista de propuestas ordenadas por prioridad
        """
        try:
            proposals = []
            
            # Generar propuestas basadas en métricas básicas
            proposals.extend(self._generate_basic_proposals(metrics))
            
            # Generar propuestas basadas en ablación
            if ablation_results:
                proposals.extend(self._generate_ablation_proposals(ablation_results))
            
            # Generar propuestas basadas en drift
            if drift_analysis:
                proposals.extend(self._generate_drift_proposals(drift_analysis))
            
            # Generar propuestas de seguridad
            proposals.extend(self._generate_safety_proposals(metrics))
            
            # Asignar IDs y prioridades
            for i, proposal in enumerate(proposals):
                proposal["id"] = f"PROP-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
                proposal["created_at"] = datetime.now().isoformat()
                proposal["priority"] = self._calculate_priority(proposal)
            
            # Ordenar por prioridad
            proposals.sort(key=lambda x: x["priority"], reverse=True)
            
            logger.info(f"Generadas {len(proposals)} propuestas automáticas")
            return proposals
            
        except Exception as e:
            logger.error(f"Error generando propuestas: {e}")
            return []
    
    def _generate_basic_proposals(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera propuestas basadas en métricas básicas"""
        proposals = []
        
        # Propuestas basadas en Hit@k
        hit_metrics = {k: v for k, v in metrics.items() if k.startswith("hit@")}
        for metric, value in hit_metrics.items():
            if value < 0.3:  # Hit rate muy bajo
                proposals.append({
                    "tipo": "ajuste_sistema",
                    "target": "general",
                    "action": "revisar_pesos",
                    "justification": f"{metric} muy bajo ({value:.2f}), revisar distribución de señales",
                    "impact": "high",
                    "category": "performance"
                })
        
        # Propuestas basadas en calibración
        if "brier_score" in metrics:
            brier = metrics["brier_score"]
            if brier > 0.25:  # Brier score alto = mala calibración
                proposals.append({
                    "tipo": "calibracion",
                    "target": "probabilidades",
                    "action": "recalibrar_modelo",
                    "justification": f"Brier score alto ({brier:.3f}), recalibrar probabilidades",
                    "impact": "medium",
                    "category": "calibration"
                })
        
        # Propuestas basadas en cobertura vs confianza
        if "coverage_confidence" in metrics:
            cc = metrics["coverage_confidence"]
            if cc.get("coverage", 0) < 0.2:  # Cobertura muy baja
                proposals.append({
                    "tipo": "cobertura",
                    "target": "fuentes",
                    "action": "expandir_fuentes",
                    "justification": f"Cobertura muy baja ({cc['coverage']:.2f}), expandir fuentes de noticias",
                    "impact": "high",
                    "category": "coverage"
                })
        
        return proposals
    
    def _generate_ablation_proposals(self, ablation_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Genera propuestas basadas en análisis de ablación"""
        proposals = []
        
        for result in ablation_results:
            if result.get("status") == "error":
                continue
            
            impact_pct = result.get("impact_percentage", 0)
            family = result.get("family", "")
            
            # Regla: si impacto > threshold, sugerir ajuste de peso
            if abs(impact_pct) > self.proposal_rules["weight_adjustment"]["threshold"]:
                # Calcular delta de ajuste
                base_delta = min(abs(impact_pct) / 100, self.proposal_rules["weight_adjustment"]["max_delta"])
                delta = max(base_delta, self.proposal_rules["weight_adjustment"]["delta_range"][0])
                
                if impact_pct > 0:  # Impacto positivo, aumentar peso
                    proposals.append({
                        "tipo": "ajuste_peso",
                        "target": family,
                        "action": "aumentar_peso",
                        "delta": delta,
                        "justification": f"Ablación {family}: +{impact_pct:.1f}% impacto, aumentar peso en {delta:.2f}",
                        "impact": "medium",
                        "category": "weight_adjustment"
                    })
                else:  # Impacto negativo, reducir peso
                    proposals.append({
                        "tipo": "ajuste_peso",
                        "target": family,
                        "action": "reducir_peso",
                        "delta": -delta,
                        "justification": f"Ablación {family}: {impact_pct:.1f}% impacto, reducir peso en {delta:.2f}",
                        "impact": "medium",
                        "category": "weight_adjustment"
                    })
            
            # Regla: si impacto muy alto, activar ensemble
            if abs(impact_pct) > self.proposal_rules["ensemble_activation"]["threshold"]:
                proposals.append({
                    "tipo": "ensemble_activation",
                    "target": family,
                    "action": "activar_ensemble",
                    "justification": f"Impacto alto en {family} ({impact_pct:.1f}%), activar ensemble de modelos",
                    "impact": "high",
                    "category": "ensemble"
                })
        
        return proposals
    
    def _generate_drift_proposals(self, drift_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera propuestas basadas en análisis de drift"""
        proposals = []
        
        # Drift de distribución de features
        if "feature_drift" in drift_analysis:
            for feature, drift_info in drift_analysis["feature_drift"].items():
                drift_score = drift_info.get("drift_score", 0)
                
                if drift_score > 0.3:  # Drift significativo
                    proposals.append({
                        "tipo": "drift_detection",
                        "target": feature,
                        "action": "recalibrar_feature",
                        "justification": f"Drift detectado en {feature} (score: {drift_score:.2f}), recalibrar",
                        "impact": "medium",
                        "category": "drift"
                    })
        
        # Cambios en fuentes de noticias
        if "source_changes" in drift_analysis:
            for source, change_info in drift_analysis["source_changes"].items():
                if change_info.get("status") == "inactive":
                    proposals.append({
                        "tipo": "fuente",
                        "target": source,
                        "action": "revisar_fuente",
                        "justification": f"Fuente {source} inactiva, revisar estado y configuración",
                        "impact": "low",
                        "category": "source_maintenance"
                    })
        
        return proposals
    
    def _generate_safety_proposals(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera propuestas de seguridad y estabilidad"""
        proposals = []
        
        # Verificar sobrepeso de señales
        if "ablation" in metrics:
            for ablation in metrics["ablation"]:
                if ablation.get("status") == "positive":
                    impact_pct = abs(ablation.get("impact_percentage", 0))
                    
                    if impact_pct > 50:  # Una señal domina demasiado
                        proposals.append({
                            "tipo": "seguridad",
                            "target": ablation.get("family", ""),
                            "action": "aplicar_clip",
                            "cap": self.proposal_rules["safety_clips"]["clip_factor"],
                            "justification": f"Señal {ablation.get('family')} domina ({impact_pct:.1f}%), aplicar clip de seguridad",
                            "impact": "high",
                            "category": "safety"
                        })
        
        # Verificar calibración extrema
        if "ece" in metrics and metrics["ece"] > 0.5:
            proposals.append({
                "tipo": "seguridad",
                "target": "calibracion",
                "action": "forzar_recalibracion",
                "justification": f"ECE extremo ({metrics['ece']:.3f}), forzar recalibración del sistema",
                "impact": "high",
                "category": "safety"
            })
        
        return proposals
    
    def _calculate_priority(self, proposal: Dict[str, Any]) -> float:
        """Calcula prioridad de una propuesta (0.0 a 1.0)"""
        priority = 0.0
        
        # Impacto base
        impact_scores = {"low": 0.3, "medium": 0.6, "high": 1.0}
        priority += impact_scores.get(proposal.get("impact", "low"), 0.3)
        
        # Categoría
        category_weights = {
            "safety": 1.0,
            "performance": 0.8,
            "weight_adjustment": 0.7,
            "calibration": 0.6,
            "coverage": 0.5,
            "ensemble": 0.4,
            "drift": 0.3,
            "source_maintenance": 0.2
        }
        priority += category_weights.get(proposal.get("category", "general"), 0.1)
        
        # Normalizar a [0, 1]
        return min(priority / 2.0, 1.0)
    
    def save_proposals(self, proposals: List[Dict[str, Any]], output_path: str) -> bool:
        """Guarda propuestas en archivo JSONL"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for proposal in proposals:
                    f.write(json.dumps(proposal, ensure_ascii=False, default=str) + '\n')
            
            logger.info(f"Propuestas guardadas en {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando propuestas: {e}")
            return False
    
    def load_proposals(self, input_path: str) -> List[Dict[str, Any]]:
        """Carga propuestas desde archivo JSONL"""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                logger.warning(f"Archivo de propuestas no encontrado: {input_path}")
                return []
            
            proposals = []
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            proposal = json.loads(line)
                            proposals.append(proposal)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Error parseando propuesta: {e}")
                            continue
            
            logger.info(f"Propuestas cargadas desde {input_path}: {len(proposals)} encontradas")
            return proposals
            
        except Exception as e:
            logger.error(f"Error cargando propuestas: {e}")
            return []
    
    def apply_proposal(self, proposal: Dict[str, Any], config_path: str) -> bool:
        """
        Aplica una propuesta específica a la configuración
        
        Args:
            proposal: Propuesta a aplicar
            config_path: Ruta al archivo de configuración
        
        Returns:
            True si se aplicó exitosamente
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.error(f"Archivo de configuración no encontrado: {config_path}")
                return False
            
            # Cargar configuración actual
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Aplicar cambios según tipo de propuesta
            if proposal["tipo"] == "ajuste_peso":
                target = proposal["target"]
                delta = proposal["delta"]
                
                if target in config:
                    if isinstance(config[target], dict) and "weight" in config[target]:
                        config[target]["weight"] += delta
                        config[target]["weight"] = max(0.0, min(1.0, config[target]["weight"]))
                    elif isinstance(config[target], (int, float)):
                        config[target] += delta
                        config[target] = max(0.0, min(1.0, config[target]))
            
            elif proposal["tipo"] == "seguridad" and proposal["action"] == "aplicar_clip":
                target = proposal["target"]
                cap = proposal["cap"]
                
                if target in config:
                    if isinstance(config[target], dict) and "weight" in config[target]:
                        config[target]["weight"] = min(config[target]["weight"], cap)
                    elif isinstance(config[target], (int, float)):
                        config[target] = min(config[target], cap)
            
            # Guardar configuración actualizada
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"Propuesta {proposal['id']} aplicada a {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error aplicando propuesta {proposal.get('id', 'unknown')}: {e}")
            return False
    
    def generate_summary_report(self, proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera resumen ejecutivo de las propuestas"""
        try:
            if not proposals:
                return {"total": 0, "summary": "No hay propuestas"}
            
            # Contar por categoría
            categories = {}
            impact_levels = {"low": 0, "medium": 0, "high": 0}
            
            for proposal in proposals:
                cat = proposal.get("category", "unknown")
                impact = proposal.get("impact", "low")
                
                categories[cat] = categories.get(cat, 0) + 1
                impact_levels[impact] = impact_levels.get(impact, 0) + 1
            
            # Top 3 propuestas por prioridad
            top_proposals = sorted(proposals, key=lambda x: x.get("priority", 0), reverse=True)[:3]
            
            return {
                "total": len(proposals),
                "categories": categories,
                "impact_distribution": impact_levels,
                "top_proposals": [
                    {
                        "id": p["id"],
                        "tipo": p["tipo"],
                        "target": p["target"],
                        "action": p["action"],
                        "priority": p["priority"],
                        "justification": p["justification"]
                    }
                    for p in top_proposals
                ],
                "summary": f"{len(proposals)} propuestas generadas, {impact_levels['high']} de alta prioridad"
            }
            
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return {"error": str(e)}

# Funciones de conveniencia
def generate_proposals(metrics: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
    """Genera propuestas automáticas"""
    generator = SLLProposalGenerator()
    return generator.generate_proposals(metrics, **kwargs)

def save_proposals(proposals: List[Dict[str, Any]], output_path: str) -> bool:
    """Guarda propuestas en archivo"""
    generator = SLLProposalGenerator()
    return generator.save_proposals(proposals, output_path)








