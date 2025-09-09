from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from app_vision.engine.contracts import Step, StepContext, StepError
from app_vision.engine.fsm import register_step
from app_vision.modules.guardrails import apply_basic_guardrails, forbid_sim_source, assert_nonempty_list
from modules.bolita_transform import FLDraw, derive_bolita
import requests
import json
from datetime import datetime, timedelta

def _as_tuple3(x) -> Tuple[int, int, int]:
    assert isinstance(x, (list, tuple)) and len(x) == 3
    a, b, c = x
    assert all(isinstance(d, int) and 0 <= d <= 9 for d in (a, b, c))
    return (a, b, c)

def _as_tuple4(x) -> Tuple[int, int, int, int]:
    assert isinstance(x, (list, tuple)) and len(x) == 4
    a, b, c, d = x
    assert all(isinstance(n, int) and 0 <= n <= 9 for n in (a, b, c, d))
    return (a, b, c, d)

@register_step("BolitaFromFloridaStep")
class BolitaFromFloridaStep(Step):
    """
    CANDADO fijo:
      - FIJO = last2(Pick3 del bloque)
      - CORRIDO = last2(Pick4 del bloque) si existe
      - TERCERO opcional = last2(Pick3 del otro bloque)
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        # Aplicar guardrails de entrada
        apply_basic_guardrails(
            step_name="BolitaFromFloridaStep",
            input_data=data,
            output_data={},
            required_input_keys=["focus"],
            sources_allowlist=["flalottery.com", "floridalottery.com"]
        )
        
        focus_raw = data.get("focus") or {}
        try:
            date  = str(focus_raw["date"])
            block = str(focus_raw["block"]).upper()
            if block not in ("MID","EVE"):
                raise ValueError("block debe ser MID|EVE")
            pick3 = _as_tuple3(focus_raw["pick3"])
            pick4 = _as_tuple4(focus_raw["pick4"]) if focus_raw.get("pick4") else None
        except Exception as e:
            raise StepError("InputError", f"focus inválido: {e}")

        other = data.get("other_pick3_last2")
        if other is not None:
            s = str(other)
            if not (len(s)==2 and s.isdigit()):
                raise StepError("InputError", f"other_pick3_last2 inválido: {other}")

        try:
            bolita = derive_bolita(
                focus=FLDraw(date=date, block=block, pick3=pick3, pick4=pick4),
                other_block_pick3_last2=other,
                force_min_candado=bool(data.get("force_min_candado", True))
            )
        except ValueError as ve:
            # Candado insuficiente → error ruidoso si así lo quieres
            raise StepError("InputError", str(ve))
        
        # Validar output con guardrails
        output = {"bolita": bolita}
        apply_basic_guardrails(
            step_name="BolitaFromFloridaStep",
            input_data=data,
            output_data=output,
            required_output_keys=["bolita"]
        )
        
        return output

@register_step("FetchFLPick3RealStep")
class FetchFLPick3RealStep(Step):
    """
    Obtiene sorteos reales de Florida Pick 3/4 usando fuentes externas.
    Inputs:
      - min_results: int (mínimo de resultados a obtener)
      - days_back: int (días hacia atrás, default 7)
    Output:
      - draws: List[Dict] con los sorteos obtenidos
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        min_results = data.get("min_results", 2)
        days_back = data.get("days_back", 7)
        
        try:
            # Usar el nuevo step de fuentes reales
            from app_vision.steps.step_fetch_real_sources import FetchExternalSourcesStep
            
            # Crear instancia del step de fuentes externas
            fetch_step = FetchExternalSourcesStep()
            
            # Ejecutar con los parámetros requeridos
            source_data = fetch_step.run(ctx, {
                "min_results": min_results,
                "timeout_s": 20
            })
            
            if source_data["status"] != "success":
                raise StepError("SourceError", f"Error en fuentes externas: {source_data.get('error', 'Error desconocido')}")
            
            draws = source_data.get("florida_draws", [])
            
            if len(draws) < min_results:
                raise StepError("InsufficientData", f"Solo se obtuvieron {len(draws)} sorteos, se necesitan {min_results}")
            
            # Aplicar guardrails
            apply_basic_guardrails(
                step_name="FetchFLPick3RealStep",
                input_data=data,
                output_data={"draws": draws},
                required_output_keys=["draws"],
                sources_allowlist=["flalottery.com", "floridalottery.com", "lotteryusa.com"]
            )
            
            return {"draws": draws}
            
        except Exception as e:
            # NO HAY FALLBACK - Solo fuentes reales
            raise StepError("SourceError", f"Error obteniendo datos reales de Florida: {e}")
    

@register_step("AnalyzeBolitaPatternsStep")
class AnalyzeBolitaPatternsStep(Step):
    """
    Analiza patrones en los resultados de bolita.
    Inputs:
      - bolita_results: List[Dict] con resultados de bolita
    Output:
      - patterns: Dict con análisis de patrones
    """
    
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        bolita_results = data.get("bolita_results", [])
        
        if not bolita_results:
            return {"patterns": {"error": "No hay resultados de bolita para analizar"}}
        
        try:
            patterns = self._analyze_patterns(bolita_results)
            return {"patterns": patterns}
            
        except Exception as e:
            raise StepError("AnalysisError", f"Error analizando patrones: {e}")
    
    def _analyze_patterns(self, bolita_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analiza patrones en los resultados de bolita"""
        patterns = {
            "total_analyses": len(bolita_results),
            "fijo_2d_frequency": {},
            "corridos_frequency": {},
            "empuje_frequency": 0,
            "candado_patterns": {},
            "parles_combinations": set()
        }
        
        for result in bolita_results:
            bolita = result.get("bolita", {})
            
            # Frecuencia de FIJO 2D
            fijo_2d = bolita.get("fijo", {}).get("2d", "")
            if fijo_2d:
                patterns["fijo_2d_frequency"][fijo_2d] = patterns["fijo_2d_frequency"].get(fijo_2d, 0) + 1
            
            # Frecuencia de corridos
            for corrido in bolita.get("corridos", []):
                patterns["corridos_frequency"][corrido] = patterns["corridos_frequency"].get(corrido, 0) + 1
            
            # Frecuencia de empuje
            if bolita.get("empuje"):
                patterns["empuje_frequency"] += 1
            
            # Patrones de candado
            candado = bolita.get("candado", [])
            candado_key = tuple(candado)
            patterns["candado_patterns"][candado_key] = patterns["candado_patterns"].get(candado_key, 0) + 1
            
            # Combinaciones de parlés
            for parles in bolita.get("parles", []):
                patterns["parles_combinations"].add(tuple(parles))
        
        # Convertir set a list para serialización
        patterns["parles_combinations"] = list(patterns["parles_combinations"])
        
        return patterns

@register_step("CandadoExportStep")
class CandadoExportStep(Step):
    """
    Entrega 'solo CANDADO' (y opcionalmente parlés) para modo Florida→Bolita.
    Inputs:
      - bolita: payload de BolitaFromFloridaStep
      - include_parles: bool (default False)
    Output:
      - deliverable: {
          mode: "FL_BOLITA_CANDADO",
          date, block,
          candado: [NN, NN, NN?(opcional)],
          parles?: [[NN,NN], ...],
          fuente: {pick3_block, pick4_block?, other_pick3_last2?}
        }
    """
    def run(self, ctx: StepContext, data: Dict[str, Any]) -> Dict[str, Any]:
        b = data.get("bolita") or {}
        if not b or "fijo" not in b or "candado" not in b:
            raise StepError("InputError", "CandadoExportStep: falta payload 'bolita' válido.")

        candado = [str(x) for x in (b.get("candado") or []) if isinstance(x,(str,int)) and str(x).isdigit()]
        if not candado:
            raise StepError("InputError", "Candado vacío: no hay 2D disponibles.")

        # Garantiza 2–3 elementos, sin duplicados
        seen = set(); candado = [x.zfill(2) for x in candado if (x not in seen and not seen.add(x))]
        if len(candado) < 2:
            raise StepError("InputError", f"Candado insuficiente ({len(candado)}). Se requieren ≥2 elementos reales.")

        deliver = {
            "mode": "FL_BOLITA_CANDADO",
            "date": b.get("date"),
            "block": b.get("block"),
            "candado": candado[:3],
            "fuente": b.get("origen", {})
        }
        if bool(data.get("include_parles", False)) and b.get("parles"):
            # Normaliza parlés a pares de strings NN
            parles = []
            for p in b["parles"]:
                if isinstance(p,(list,tuple)) and len(p)==2:
                    a, c = str(p[0]).zfill(2), str(p[1]).zfill(2)
                    parles.append([a,c])
            deliver["parles"] = parles

        return {"deliverable": deliver}
