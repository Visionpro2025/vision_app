# app_vision/steps/step_fetch_real_sources.py
"""
Step para obtener datos reales de fuentes externas
Integra Florida Lottery oficial, LotteryUSA backup y Bolita Cubana
"""

from __future__ import annotations
from typing import Dict, Any, List
from datetime import datetime
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails

# Importar conectores
try:
    from connectors.florida_official import fetch_pick3_latest_html, fetch_pick4_latest_html, merge_p3_p4
    FLORIDA_OFFICIAL_AVAILABLE = True
except ImportError:
    FLORIDA_OFFICIAL_AVAILABLE = False

try:
    from connectors.lotteryusa_backup import fetch_pick3_pick4_backup
    LOTTERYUSA_AVAILABLE = True
except ImportError:
    LOTTERYUSA_AVAILABLE = False

try:
    from connectors.bolita_cuba import fetch_directorio_cubano, fetch_labolitacubana
    BOLITA_CUBA_AVAILABLE = True
except ImportError:
    BOLITA_CUBA_AVAILABLE = False

@register_step("FetchExternalSourcesStep")
class FetchExternalSourcesStep(Step):
    """
    Step para obtener datos reales de fuentes externas
    - Florida Lottery oficial (primaria)
    - LotteryUSA backup (secundaria)
    - Bolita Cubana (referencia)
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        min_results = data.get("min_results", 10)
        timeout_s = data.get("timeout_s", 20)
        
        results = {
            "step_name": "FetchExternalSourcesStep",
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "sources_used": [],
            "florida_draws": [],
            "bolita_refs": [],
            "errors": []
        }
        
        try:
            # 1. Obtener datos de Florida Lottery (fuente primaria)
            florida_draws = self._fetch_florida_data(timeout_s)
            if florida_draws:
                results["florida_draws"] = florida_draws
                results["sources_used"].append("florida_official")
            else:
                results["errors"].append("No se pudieron obtener datos de Florida Lottery oficial")
                # Si no hay datos de la fuente primaria, intentar backup inmediatamente
                if LOTTERYUSA_AVAILABLE:
                    try:
                        backup_draws = fetch_pick3_pick4_backup()
                        if backup_draws:
                            results["florida_draws"] = backup_draws
                            results["sources_used"].append("lotteryusa_backup")
                            results["errors"].append("Usando fuente de respaldo LotteryUSA")
                    except Exception as e:
                        results["errors"].append(f"Error en backup LotteryUSA: {str(e)}")
            
            # 2. Si no hay suficientes datos, intentar backup adicional
            if len(results["florida_draws"]) < min_results and LOTTERYUSA_AVAILABLE and "lotteryusa_backup" not in results["sources_used"]:
                try:
                    backup_draws = fetch_pick3_pick4_backup()
                    if backup_draws:
                        results["florida_draws"].extend(backup_draws)
                        results["sources_used"].append("lotteryusa_backup")
                        results["errors"].append("Usando fuente de respaldo LotteryUSA adicional")
                except Exception as e:
                    results["errors"].append(f"Error en backup LotteryUSA adicional: {str(e)}")
            
            # 3. Obtener referencias de Bolita Cubana
            if BOLITA_CUBA_AVAILABLE:
                bolita_refs = self._fetch_bolita_data(timeout_s)
                results["bolita_refs"] = bolita_refs
            
            # 4. Validar que tenemos suficientes datos REALES
            if len(results["florida_draws"]) < min_results:
                error_msg = f"Solo se obtuvieron {len(results['florida_draws'])} resultados reales, se necesitan {min_results}. Fuentes intentadas: {results['sources_used']}"
                if results["errors"]:
                    error_msg += f". Errores: {'; '.join(results['errors'])}"
                raise StepError("SourceError", error_msg)
            
            # 5. Normalizar y limpiar datos
            results["florida_draws"] = self._normalize_draws(results["florida_draws"])
            
            # 6. Agregar metadatos
            results["metadata"] = {
                "total_draws": len(results["florida_draws"]),
                "sources_count": len(results["sources_used"]),
                "bolita_refs_count": len(results["bolita_refs"]),
                "errors_count": len(results["errors"]),
                "fetch_successful": True
            }
            
            # Validar output con guardrails
            apply_basic_guardrails(
                step_name="FetchExternalSourcesStep",
                input_data=data,
                output_data=results,
                required_output_keys=["step_name", "timestamp", "status", "florida_draws", "sources_used"],
                sources_allowlist=["flalottery.com", "floridalottery.com", "lotteryusa.com"]
            )
            
            return results
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            raise StepError("SourceError", f"Error obteniendo datos de fuentes externas: {e}")
    
    def _fetch_florida_data(self, timeout_s: int) -> List[Dict[str, Any]]:
        """Obtiene datos de Florida Lottery oficial"""
        if not FLORIDA_OFFICIAL_AVAILABLE:
            return []
        
        try:
            # Obtener Pick 3
            p3_data = fetch_pick3_latest_html(timeout=timeout_s)
            
            # Obtener Pick 4
            p4_data = fetch_pick4_latest_html(timeout=timeout_s)
            
            # Combinar datos
            combined = merge_p3_p4(p3_data, p4_data, source="flalottery.com")
            
            return combined
            
        except Exception as e:
            print(f"Error obteniendo datos de Florida Lottery: {e}")
            return []
    
    def _fetch_bolita_data(self, timeout_s: int) -> List[Dict[str, Any]]:
        """Obtiene datos de referencia de Bolita Cubana"""
        bolita_refs = []
        
        try:
            dc_data = fetch_directorio_cubano(timeout=timeout_s)
            bolita_refs.append(dc_data)
        except Exception as e:
            print(f"Error obteniendo Directorio Cubano: {e}")
        
        try:
            lbc_data = fetch_labolitacubana(timeout=timeout_s)
            bolita_refs.append(lbc_data)
        except Exception as e:
            print(f"Error obteniendo LaBolitaCubana: {e}")
        
        return bolita_refs
    
    def _normalize_draws(self, draws: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normaliza los datos de sorteos"""
        normalized = []
        
        for draw in draws:
            # Asegurar que tiene los campos requeridos
            normalized_draw = {
                "date": draw.get("date", ""),
                "block": draw.get("block", ""),
                "source": draw.get("source", "unknown"),
                "fetched_at": draw.get("fetched_at", datetime.now().isoformat())
            }
            
            # Agregar Pick 3 si existe
            if "pick3" in draw:
                normalized_draw["numbers"] = draw["pick3"]  # Para compatibilidad
                normalized_draw["pick3"] = draw["pick3"]
            
            # Agregar Pick 4 si existe
            if "pick4" in draw:
                normalized_draw["pick4"] = draw["pick4"]
            
            # Agregar Fireball si existe
            if "fireball" in draw:
                normalized_draw["fireball"] = draw["fireball"]
            
            # Agregar confianza si existe
            if "confidence" in draw:
                normalized_draw["confidence"] = draw["confidence"]
            
            normalized.append(normalized_draw)
        
        return normalized
