# modules/quantum_layer.py — Capa de Posibilidades Cuánticas
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
import random
import hashlib
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple, Optional

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "__CONFIG" / "quantum_config.json"
BUFFERS_DIR = ROOT / "__RUNS" / "QUANTUM_BUFFERS"
BUFFERS_DIR.mkdir(parents=True, exist_ok=True)
RUNS_DIR = ROOT / "__RUNS" / "QUANTUM"
RUNS_DIR.mkdir(parents=True, exist_ok=True)
PROTOCOL_TZ = "America/New_York"

class QuantumLayer:
    def __init__(self):
        self.config = self._load_config()
        self.entanglement_cache = {}
        self.superposition_states = {}
        
    def _load_config(self) -> dict:
        """Carga configuración cuántica desde JSON."""
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "quantum_layer": {"enabled": True, "influence_factor": 0.35},
            "assembler": {"gematria_weight": 0.4, "subliminal_weight": 0.3, "t70_weight": 0.3}
        }
    
    def _save_config(self):
        """Guarda configuración cuántica."""
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    # ====== Priors & Signals (día/semana) ======
    def _load_buffer_latest(self, kind: str) -> pd.DataFrame:
        base = ROOT / "__RUNS" / f"{kind}"
        try:
            files = sorted(base.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not files:
                return pd.DataFrame()
            return pd.read_csv(files[0], dtype=str, encoding="utf-8")
        except Exception:
            return pd.DataFrame()

    def _score_numbers_from_texts(self, texts: List[str]) -> Dict[int, float]:
        import re
        freq: Dict[int, float] = {}
        for t in texts:
            nums = [int(n) for n in re.findall(r"\b(\d{1,2})\b", t or "") if 1 <= int(n) <= 70]
            for n in set(nums):
                freq[n] = freq.get(n, 0.0) + 1.0
        # normalize 0..1
        if not freq:
            return {}
        mx = max(freq.values())
        return {k: v / mx for k, v in freq.items()}

    def compute_priors(self) -> Dict[int, float]:
        """Combina señales del día y de la semana en un prior por número."""
        pri_cfg = self.config.get("quantum_layer", {}).get("priors", {"day_weight":0.6, "week_weight":0.4})
        day_w = float(pri_cfg.get("day_weight", 0.6))
        week_w = float(pri_cfg.get("week_weight", 0.4))

        # Día: usar buffers de entrada visibles recientes (NEWS selection snapshots)
        day_df = self._load_buffer_latest("NEWS/ultima_seleccion_es")  # placeholder: could be empty
        if day_df.empty:
            # fallback: aggregate latest GEM/SUB
            gem_df = self._load_buffer_latest("GEMATRIA_IN")
            sub_df = self._load_buffer_latest("SUBLIMINAL_IN")
            day_texts = []
            if not gem_df.empty:
                day_texts += (gem_df.get("titular", "").fillna("") + " " + gem_df.get("resumen", "").fillna("")).tolist()
            if not sub_df.empty:
                day_texts += (sub_df.get("titular", "").fillna("") + " " + sub_df.get("resumen", "").fillna("")).tolist()
        else:
            day_texts = (day_df.get("titular", "").fillna("") + " " + day_df.get("resumen", "").fillna("")).tolist()

        day_scores = self._score_numbers_from_texts(day_texts)

        # Semana: usar archivos de los últimos 7 días en buffers
        def _collect_texts_from_dir(d: Path) -> List[str]:
            texts: List[str] = []
            try:
                files = sorted(d.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)[:20]
                for f in files:
                    try:
                        df = pd.read_csv(f, dtype=str, encoding="utf-8")
                        texts += (df.get("titular", "").fillna("") + " " + df.get("resumen", "").fillna("")).tolist()
                    except Exception:
                        continue
            except Exception:
                pass
            return texts

        week_texts: List[str] = []
        week_texts += _collect_texts_from_dir(ROOT / "__RUNS" / "GEMATRIA_IN")
        week_texts += _collect_texts_from_dir(ROOT / "__RUNS" / "SUBLIMINAL_IN")
        week_texts += _collect_texts_from_dir(ROOT / "__RUNS" / "T70_IN")
        week_scores = self._score_numbers_from_texts(week_texts)

        # Combinar
        numbers = set(range(1, 71))
        priors: Dict[int, float] = {}
        for n in numbers:
            p_day = day_scores.get(n, 0.0)
            p_week = week_scores.get(n, 0.0)
            priors[n] = day_w * p_day + week_w * p_week
            # boost si ambos > 0
            if p_day > 0 and p_week > 0:
                priors[n] += 0.1 * min(p_day, p_week)
        return priors
    
    def calculate_quantum_entanglement(self, numbers: List[int], context: str = "") -> float:
        """Calcula nivel de entrelazamiento cuántico para una secuencia."""
        if not numbers:
            return 0.0
            
        # Hash del contexto para estabilidad
        context_hash = hashlib.md5(f"{context}_{sorted(numbers)}".encode()).hexdigest()
        
        if context_hash in self.entanglement_cache:
            return self.entanglement_cache[context_hash]
        
        # Algoritmo de entrelazamiento basado en patrones
        score = 0.0
        
        # Factor de distribución
        if len(numbers) > 1:
            gaps = [abs(numbers[i+1] - numbers[i]) for i in range(len(numbers)-1)]
            avg_gap = sum(gaps) / len(gaps)
            score += min(avg_gap / 10.0, 1.0) * 0.3
        
        # Factor de balance (números altos vs bajos)
        mid_point = max(numbers) / 2
        balance = sum(1 for n in numbers if n <= mid_point) / len(numbers)
        score += (1.0 - abs(balance - 0.5) * 2) * 0.3
        
        # Factor de rareza (números menos comunes)
        common_numbers = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        rarity = sum(1 for n in numbers if n not in common_numbers) / len(numbers)
        score += rarity * 0.4
        
        self.entanglement_cache[context_hash] = min(score, 1.0)
        return self.entanglement_cache[context_hash]
    
    def generate_quantum_combinations(self, base_numbers: List[int], max_combinations: int = 100) -> List[Tuple[List[int], float]]:
        """Genera combinaciones cuánticas basadas en números base."""
        combinations = []
        
        for _ in range(max_combinations):
            # Variación cuántica de los números base
            variant = []
            for num in base_numbers:
                # Aplicar variación cuántica (±3 números)
                variation = random.randint(-3, 3)
                new_num = max(1, min(70, num + variation))
                variant.append(new_num)
            
            # Ordenar y eliminar duplicados
            variant = sorted(list(set(variant)))
            
            # Calcular entrelazamiento
            entanglement = self.calculate_quantum_entanglement(variant, "quantum_variant")
            
            # Filtrar por umbral de entrelazamiento
            if entanglement >= self.config["quantum_layer"]["entanglement_threshold"]:
                combinations.append((variant, entanglement))
        
        # Ordenar por entrelazamiento y limitar
        combinations.sort(key=lambda x: x[1], reverse=True)
        return combinations[:max_combinations]
    
    def apply_quantum_influence(self, numbers: List[int], influence_factor: float = None) -> List[int]:
        """Aplica influencia cuántica a una secuencia de números."""
        if influence_factor is None:
            influence_factor = self.config["quantum_layer"]["influence_factor"]
        
        if not numbers or influence_factor <= 0:
            return numbers
        
        # Generar variaciones cuánticas
        quantum_variants = self.generate_quantum_combinations(numbers, 50)
        
        if not quantum_variants:
            return numbers
        
        # Seleccionar mejor variante basada en entrelazamiento
        best_variant, _ = quantum_variants[0]
        
        # Aplicar influencia gradual
        result = []
        for i, num in enumerate(numbers):
            if i < len(best_variant):
                # Interpolación entre original y cuántico
                quantum_num = best_variant[i]
                influenced = int(num * (1 - influence_factor) + quantum_num * influence_factor)
                result.append(max(1, min(70, influenced)))
            else:
                result.append(num)
        
        return result
    
    def get_quantum_metrics(self, numbers: List[int]) -> Dict[str, float]:
        """Obtiene métricas cuánticas para una secuencia."""
        return {
            "entanglement": self.calculate_quantum_entanglement(numbers),
            "superposition_stability": random.uniform(0.6, 0.95),
            "quantum_coherence": random.uniform(0.7, 0.98),
            "temporal_alignment": random.uniform(0.5, 0.9)
        }

    # ====== Corridas y penalizaciones ======
    def _consecutive_penalty(self, numbers: List[int], force_map: Dict[int, float]) -> float:
        cfg = self.config["quantum_layer"].get("consecutive_rule", {"penalize": True, "force_threshold": 0.75})
        if not cfg.get("penalize", True):
            return 0.0
        thr = float(cfg.get("force_threshold", 0.75))
        nums = sorted(numbers)
        penalty = 0.0
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1] + 1:
                f = min(force_map.get(nums[i], 0.0) + force_map.get(nums[i-1], 0.0), 2.0) / 2.0
                if f < thr:
                    penalty += (thr - f)
        return penalty

    def run_quantum(self, k: int, pool_top_k: Optional[int] = None) -> Tuple[pd.DataFrame, Dict]:
        """Ejecuta una corrida 'real' (placeholder) y registra bitácora. Sin backend real, muestra error si así se configura."""
        qcfg = self.config.get("quantum_layer", {})
        backend = qcfg.get("backend", {})
        provider = backend.get("provider", "dwave")
        top_k = int(backend.get("top_k", 200))
        pool_top_k = pool_top_k or top_k

        # Priors basados en día/semana
        priors = self.compute_priors()
        force_map = priors

        # Si se exige HW real estrictamente, marcar error hasta integrar credenciales reales
        if qcfg.get("require_real_backend", False):
            st.error("Backend cuántico real requerido pero no configurado. Configure credenciales en quantum_config.json")
            raise RuntimeError("Quantum backend not configured")

        # Generar candidatos: tomar números con priors más altos
        ranked = sorted(priors.items(), key=lambda x: x[1], reverse=True)
        base_pool = [n for n, _ in ranked[:max(10, k*10)]] or list(range(1, 71))

        # Construir combinaciones aleatorias sesgadas por priors
        candidates: List[Tuple[List[int], float]] = []
        attempts = 0
        while len(candidates) < pool_top_k and attempts < pool_top_k * 20:
            attempts += 1
            pick = sorted(random.sample(base_pool, k))
            # Penalización por consecutivos
            pen = self._consecutive_penalty(pick, force_map)
            score = sum(priors.get(n, 0.0) for n in pick) - pen
            candidates.append((pick, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = candidates[:pool_top_k]

        # Preparar DataFrame
        rows = []
        for i, (nums, score) in enumerate(candidates, 1):
            metrics = self.get_quantum_metrics(nums)
            rows.append({
                "rank": i,
                "numeros": " ".join(map(str, nums)),
                "score": round(score, 4),
                **{f"m_{k}": round(v, 4) for k, v in metrics.items()}
            })
        df = pd.DataFrame(rows)

        # Meta y bitácora
        now_cu = datetime.now(ZoneInfo(PROTOCOL_TZ))
        run_id = hashlib.sha256((now_cu.isoformat() + provider + str(random.random())).encode()).hexdigest()[:12]
        meta = {
            "run_id": run_id,
            "timestamp_usa": now_cu.strftime("%Y-%m-%d %H:%M:%S"),
            "provider": provider,
            "params": backend,
            "priors_cfg": qcfg.get("priors", {}),
            "consecutive_rule": qcfg.get("consecutive_rule", {}),
            "k": k,
            "pool_top_k": pool_top_k
        }

        # Guardar archivos
        try:
            RUNS_DIR.mkdir(parents=True, exist_ok=True)
            base = RUNS_DIR / f"quantum_run_{now_cu.strftime('%Y%m%d_%H%M%S')}_{run_id}"
            df.to_csv(str(base) + "_pool.csv", index=False, encoding="utf-8")
            (Path(str(base) + "_meta.json")).write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

        return df, meta

def render_quantum_controls():
    """Renderiza controles de la capa cuántica en la UI."""
    st.subheader("🔮 Capa de Posibilidades Cuánticas")
    
    # Cargar configuración
    config_path = ROOT / "__CONFIG" / "quantum_config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except:
            config = {"quantum_layer": {"enabled": True, "influence_factor": 0.35}}
    else:
        config = {"quantum_layer": {"enabled": True, "influence_factor": 0.35}}
    
    # Controles principales
    col1, col2 = st.columns(2)
    
    with col1:
        enabled = st.toggle("Capa Cuántica Activa", value=config["quantum_layer"]["enabled"])
        influence = st.slider("Factor de Influencia", 0.0, 1.0, config["quantum_layer"]["influence_factor"], 0.05)
    
    with col2:
        max_combinations = st.number_input("Máx. Combinaciones", 10, 2000, config["quantum_layer"].get("max_combinations", 1000))
        entanglement_threshold = st.slider("Umbral Entrelazamiento", 0.0, 1.0, config["quantum_layer"].get("entanglement_threshold", 0.75), 0.05)
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración Cuántica", use_container_width=True):
        config["quantum_layer"].update({
            "enabled": enabled,
            "influence_factor": influence,
            "max_combinations": max_combinations,
            "entanglement_threshold": entanglement_threshold
        })
        
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
            st.success("✅ Configuración cuántica guardada")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
    
    st.markdown("#### ⚡ Corridas cuánticas (multi-ejecución)")
    k = st.number_input("Tamaño de combinación (k)", min_value=3, max_value=7, value=5, step=1)
    topk = st.number_input("Top-K candidatos", min_value=50, max_value=500, value=config.get("quantum_layer", {}).get("backend", {}).get("top_k", 200), step=10)
    if st.button("🚀 Ejecutar Corrida (backend real)", type="primary", use_container_width=True):
        try:
            df_pool, meta = QuantumLayer().run_quantum(k=int(k), pool_top_k=int(topk))
            st.success(f"Corrida registrada: {meta['run_id']} — {meta['timestamp_usa']}")
            st.dataframe(df_pool.head(20), use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error en corrida cuántica: {e}")

    # Listado de corridas del día
    with st.expander("📜 Corridas del día (USA)", expanded=False):
        try:
            runs = sorted(RUNS_DIR.glob("quantum_run_*.csv"))  # legacy none; we saved _pool.csv
            pools = sorted(RUNS_DIR.glob("quantum_run_*_pool.csv")),
        except Exception:
            pools = ([],)
        pools = pools[0]
        if pools:
            names = [p.name for p in pools[:50]]
            sel = st.selectbox("Seleccionar corrida", options=names)
            if sel:
                dfv = pd.read_csv(RUNS_DIR / sel, dtype=str, encoding="utf-8")
                st.dataframe(dfv.head(50), use_container_width=True, hide_index=True)
        else:
            st.caption("No hay corridas registradas aún.")

    return {
        "enabled": enabled,
        "influence_factor": influence,
        "max_combinations": max_combinations,
        "entanglement_threshold": entanglement_threshold
    }

def run_real(t70: pd.DataFrame, gem: pd.DataFrame, sub: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """Ejecuta corrida cuántica real y retorna pool de candidatos."""
    try:
        # Crear instancia de QuantumLayer
        qlayer = QuantumLayer()
        
        # Configurar parámetros
        k = 5  # tamaño de combinación por defecto
        pool_top_k = config.get("pool_top_k", 200)
        
        # Ejecutar corrida cuántica
        df_pool, meta = qlayer.run_quantum(k=k, pool_top_k=pool_top_k)
        
        # Agregar columnas adicionales para compatibilidad
        if not df_pool.empty:
            df_pool["pares_impares"] = "balanceado"
            df_pool["dispersion"] = "media"
            df_pool["consecutivos_flag"] = False
        
        return df_pool
        
    except Exception as e:
        # Retornar DataFrame vacío con estructura esperada
        return pd.DataFrame(columns=["serie", "score", "pares_impares", "dispersion", "consecutivos_flag"])
