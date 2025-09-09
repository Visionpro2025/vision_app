# modules/orchestrator.py — Orquestador de Protocolos Premium
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import time
import hashlib
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "__CONFIG" / "quantum_config.json"
PROTOCOLS_DIR = ROOT / "__RUNS" / "PROTOCOLS"
PROTOCOLS_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ProtocolStep:
    name: str
    description: str
    function: Callable
    dependencies: List[str]
    estimated_time: int  # segundos
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict] = None
    error: Optional[str] = None

class ProtocolOrchestrator:
    def __init__(self):
        self.config = self._load_config()
        self.steps: Dict[str, ProtocolStep] = {}
        self.execution_log: List[Dict] = []
        self.current_step: Optional[str] = None
        
    def _load_config(self) -> dict:
        """Carga configuración del orquestador."""
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "protocols": {
                "step_by_step": True,
                "auto_execute": False,
                "validation_required": True
            }
        }
    
    def add_step(self, step: ProtocolStep):
        """Añade un paso al protocolo."""
        self.steps[step.name] = step
    
    def get_step_dependencies(self, step_name: str) -> List[str]:
        """Obtiene las dependencias de un paso."""
        step = self.steps.get(step_name)
        if not step:
            return []
        return step.dependencies
    
    def can_execute_step(self, step_name: str) -> bool:
        """Verifica si un paso puede ejecutarse."""
        step = self.steps.get(step_name)
        if not step:
            return False
        
        # Verificar que todas las dependencias estén completadas
        for dep in step.dependencies:
            dep_step = self.steps.get(dep)
            if not dep_step or dep_step.status != "completed":
                return False
        
        return True
    
    def execute_step(self, step_name: str) -> Dict:
        """Ejecuta un paso específico."""
        step = self.steps.get(step_name)
        if not step:
            return {"success": False, "error": f"Paso '{step_name}' no encontrado"}
        
        if not self.can_execute_step(step_name):
            return {"success": False, "error": f"Dependencias no satisfechas para '{step_name}'"}
        
        # Marcar como ejecutándose
        step.status = "running"
        self.current_step = step_name
        
        # Registrar inicio
        self.execution_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step_name,
            "action": "started",
            "status": "running"
        })
        
        try:
            # Ejecutar función
            start_time = time.time()
            result = step.function()
            execution_time = time.time() - start_time
            
            # Marcar como completado
            step.status = "completed"
            step.result = result
            
            # Registrar éxito
            self.execution_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": step_name,
                "action": "completed",
                "status": "success",
                "execution_time": execution_time,
                "result": result
            })
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Marcar como fallido
            step.status = "failed"
            step.error = str(e)
            
            # Registrar error
            self.execution_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": step_name,
                "action": "failed",
                "status": "error",
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            self.current_step = None
    
    def execute_all_steps(self) -> Dict:
        """Ejecuta todos los pasos en orden de dependencias."""
        # Ordenar pasos por dependencias
        execution_order = self._get_execution_order()
        
        results = {}
        for step_name in execution_order:
            result = self.execute_step(step_name)
            results[step_name] = result
            
            if not result["success"]:
                break  # Detener si hay un error
        
        return results
    
    def _get_execution_order(self) -> List[str]:
        """Obtiene el orden de ejecución basado en dependencias."""
        # Algoritmo de ordenamiento topológico simple
        visited = set()
        order = []
        
        def visit(step_name: str):
            if step_name in visited:
                return
            visited.add(step_name)
            
            # Visitar dependencias primero
            step = self.steps.get(step_name)
            if step:
                for dep in step.dependencies:
                    visit(dep)
            
            order.append(step_name)
        
        # Visitar todos los pasos
        for step_name in self.steps:
            visit(step_name)
        
        return order
    
    def reset_protocol(self):
        """Reinicia el estado del protocolo."""
        for step in self.steps.values():
            step.status = "pending"
            step.result = None
            step.error = None
        self.execution_log.clear()
        self.current_step = None
    
    def get_protocol_status(self) -> Dict:
        """Obtiene el estado actual del protocolo."""
        total_steps = len(self.steps)
        completed_steps = sum(1 for s in self.steps.values() if s.status == "completed")
        failed_steps = sum(1 for s in self.steps.values() if s.status == "failed")
        running_steps = sum(1 for s in self.steps.values() if s.status == "running")
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "failed_steps": failed_steps,
            "running_steps": running_steps,
            "progress": completed_steps / total_steps if total_steps > 0 else 0,
            "current_step": self.current_step
        }
    
    def save_protocol_state(self, lottery: str):
        """Guarda el estado del protocolo."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        state_file = PROTOCOLS_DIR / f"protocol_{lottery}_{timestamp}.json"
        
        state = {
            "lottery": lottery,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "steps": {
                name: {
                    "status": step.status,
                    "result": step.result,
                    "error": step.error
                }
                for name, step in self.steps.items()
            },
            "execution_log": self.execution_log,
            "current_step": self.current_step
        }
        
        try:
            state_file.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            return str(state_file)
        except Exception as e:
            return None

def create_default_protocol() -> ProtocolOrchestrator:
    """Crea un protocolo por defecto con pasos básicos."""
    orchestrator = ProtocolOrchestrator()
    
    # Paso 1: Acopio de noticias
    def step_news_acquisition():
        # Simular acopio de noticias
        time.sleep(1)
        return {"news_count": 25, "sources": 8}
    
    orchestrator.add_step(ProtocolStep(
        name="news_acquisition",
        description="Acopio de noticias de emoción social",
        function=step_news_acquisition,
        dependencies=[],
        estimated_time=30
    ))
    
    # Paso 2: Procesamiento Gematría
    def step_gematria_processing():
        # Simular procesamiento gematría
        time.sleep(1)
        return {"gematria_numbers": [7, 13, 22, 31, 45], "confidence": 0.85}
    
    orchestrator.add_step(ProtocolStep(
        name="gematria_processing",
        description="Procesamiento de capa gematría",
        function=step_gematria_processing,
        dependencies=["news_acquisition"],
        estimated_time=45
    ))
    
    # Paso 3: Procesamiento Subliminal
    def step_subliminal_processing():
        # Simular procesamiento subliminal
        time.sleep(1)
        return {"subliminal_numbers": [3, 11, 19, 28, 42], "influence": 0.72}
    
    orchestrator.add_step(ProtocolStep(
        name="subliminal_processing",
        description="Procesamiento de capa subliminal",
        function=step_subliminal_processing,
        dependencies=["news_acquisition"],
        estimated_time=40
    ))
    
    # Paso 4: Análisis T70
    def step_t70_analysis():
        # Simular análisis T70
        time.sleep(1)
        return {"t70_numbers": [5, 17, 24, 33, 48], "correlation": 0.78}
    
    orchestrator.add_step(ProtocolStep(
        name="t70_analysis",
        description="Análisis de correlaciones T70",
        function=step_t70_analysis,
        dependencies=["news_acquisition"],
        estimated_time=35
    ))
    
    # Paso 5: Ensamblado de series
    def step_series_assembly():
        # Simular ensamblado
        time.sleep(1)
        return {"series_count": 5, "numbers_per_series": 6, "quality_score": 0.88}
    
    orchestrator.add_step(ProtocolStep(
        name="series_assembly",
        description="Ensamblado final de series",
        function=step_series_assembly,
        dependencies=["gematria_processing", "subliminal_processing", "t70_analysis"],
        estimated_time=60
    ))
    
    return orchestrator

def render_orchestrator_ui(current_lottery: str):
    """Renderiza la UI del orquestador."""
    st.subheader("🎼 Orquestador de Protocolos Premium")
    
    # Inicializar orquestador
    orchestrator = create_default_protocol()
    
    # Controles principales
    col1, col2 = st.columns(2)
    with col1:
        execution_mode = st.selectbox(
            "Modo de ejecución",
            ["Paso a paso", "Ejecución completa"],
            help="Controla si ejecutar todo automáticamente o paso por paso"
        )
    with col2:
        auto_validate = st.checkbox(
            "Validación automática",
            value=orchestrator.config["protocols"]["validation_required"],
            help="Validar resultados después de cada paso"
        )
    
    # Estado del protocolo
    status = orchestrator.get_protocol_status()
    
    st.markdown("#### 📊 Estado del Protocolo")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pasos", status["total_steps"])
    col2.metric("Completados", status["completed_steps"])
    col3.metric("Fallidos", status["failed_steps"])
    col4.metric("Progreso", f"{status['progress']:.1%}")
    
    # Barra de progreso
    st.progress(status["progress"])
    
    # Lista de pasos
    st.markdown("#### 📋 Pasos del Protocolo")
    
    for step_name, step in orchestrator.steps.items():
        with st.expander(f"{step_name}: {step.description}", expanded=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                # Estado visual
                if step.status == "completed":
                    st.success("✅ Completado")
                elif step.status == "failed":
                    st.error("❌ Fallido")
                elif step.status == "running":
                    st.info("🔄 Ejecutándose...")
                else:
                    st.info("⏳ Pendiente")
            
            with col2:
                st.write(f"⏱️ {step.estimated_time}s")
            
            with col3:
                if step.dependencies:
                    st.write(f"🔗 {', '.join(step.dependencies)}")
                else:
                    st.write("🔗 Sin dependencias")
            
            with col4:
                if step.status == "pending" and orchestrator.can_execute_step(step_name):
                    if st.button("▶️", key=f"exec_{step_name}"):
                        result = orchestrator.execute_step(step_name)
                        if result["success"]:
                            st.success("✅ Completado")
                        else:
                            st.error(f"❌ Error: {result['error']}")
                        st.rerun()
                elif step.status == "completed":
                    st.write("✅")
                elif step.status == "failed":
                    st.write("❌")
                elif step.status == "running":
                    st.write("🔄")
                else:
                    st.write("⏳")
            
            # Mostrar resultado si está disponible
            if step.result:
                st.json(step.result)
            
            # Mostrar error si está disponible
            if step.error:
                st.error(f"Error: {step.error}")
    
    # Controles de ejecución
    st.markdown("#### 🎮 Controles de Ejecución")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Ejecutar Todo", use_container_width=True, type="primary"):
            with st.spinner("Ejecutando protocolo completo..."):
                results = orchestrator.execute_all_steps()
            
            # Mostrar resultados
            success_count = sum(1 for r in results.values() if r["success"])
            st.success(f"✅ Completados {success_count}/{len(results)} pasos")
            
            if success_count < len(results):
                failed_steps = [name for name, result in results.items() if not result["success"]]
                st.error(f"❌ Fallidos: {', '.join(failed_steps)}")
            
            st.rerun()
    
    with col2:
        if st.button("🔄 Reiniciar Protocolo", use_container_width=True):
            orchestrator.reset_protocol()
            st.success("✅ Protocolo reiniciado")
            st.rerun()
    
    with col3:
        if st.button("💾 Guardar Estado", use_container_width=True):
            state_file = orchestrator.save_protocol_state(current_lottery)
            if state_file:
                st.success(f"✅ Estado guardado: {state_file}")
            else:
                st.error("❌ Error al guardar estado")
    
    # Log de ejecución
    if orchestrator.execution_log:
        st.markdown("#### 📝 Log de Ejecución")
        log_df = pd.DataFrame(orchestrator.execution_log)
        st.dataframe(log_df, use_container_width=True, hide_index=True)

def assemble(pool: pd.DataFrame, k: int, rules: Dict) -> pd.DataFrame:
    """Ensambla series finales desde pool cuántico."""
    try:
        if pool.empty:
            return pd.DataFrame()
        
        # Simular ensamblaje de series
        results = []
        lottery = rules.get("lottery", "GENERAL")
        
        # Tomar las primeras k series del pool
        for i, (_, row) in enumerate(pool.head(k).iterrows()):
            serie = row.get("serie", "")
            score = row.get("score", 0.0)
            
            # Generar serie simulada si no existe
            if not serie:
                import random
                serie = "-".join([str(random.randint(1, 70)) for _ in range(5)])
            
            results.append({
                "id_serie": f"serie_{i+1:03d}",
                "serie": serie,
                "score": score,
                "lottery": lottery,
                "timestamp": datetime.now().isoformat(),
                "fuente": "quantum_pool",
                "balance_pares_impares": "balanceado",
                "dispersion": "media",
                "consecutivos": False
            })
        
        return pd.DataFrame(results)
        
    except Exception as e:
        # Retornar DataFrame vacío con estructura esperada
        return pd.DataFrame(columns=["id_serie", "serie", "score", "lottery", "timestamp", "fuente"])
