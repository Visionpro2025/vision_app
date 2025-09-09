from __future__ import annotations
from typing import Dict, Any, List, Optional, Type
from .contracts import Step, StepContext, StepError
import json
import re

# Registry global de pasos
_step_registry: Dict[str, Type[Step]] = {}

def register_step(step_name: str):
    """Decorator para registrar un paso en el sistema"""
    def decorator(step_class: Type[Step]):
        _step_registry[step_name] = step_class
        return step_class
    return decorator

def get_step_class(step_name: str) -> Optional[Type[Step]]:
    """Obtiene la clase de un paso por nombre"""
    return _step_registry.get(step_name)

def list_registered_steps() -> List[str]:
    """Lista todos los pasos registrados"""
    return list(_step_registry.keys())

class PipelineExecutor:
    """Ejecutor de pipelines basado en FSM"""
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.current_state: Dict[str, Any] = {}
    
    def execute_pipeline(self, pipeline_config: Dict[str, Any], initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ejecuta un pipeline completo"""
        steps = pipeline_config.get("steps", [])
        execution_id = f"exec_{len(self.execution_history)}"
        
        # Estado inicial
        self.current_state = {
            "execution_id": execution_id,
            "step_results": {},
            "global_data": initial_data or {},
            "current_step": 0,
            "status": "running"
        }
        
        try:
            for i, step_config in enumerate(steps):
                step_name = step_config.get("name")
                step_class_name = step_config.get("class")
                step_inputs = step_config.get("inputs", {})
                
                # Crear contexto del paso
                ctx = StepContext(
                    step_name=step_name,
                    step_id=f"{execution_id}_{i}",
                    pipeline_id=execution_id,
                    execution_id=execution_id,
                    metadata={"step_index": i}
                )
                
                # Obtener clase del paso
                step_class = get_step_class(step_class_name)
                if not step_class:
                    raise StepError("StepNotFound", f"Paso no encontrado: {step_class_name}")
                
                # Resolver variables en inputs
                resolved_inputs = self._resolve_variables(step_inputs)
                
                # Ejecutar paso
                step_instance = step_class()
                result = step_instance.run(ctx, resolved_inputs)
                
                # Guardar resultado
                self.current_state["step_results"][step_name] = result
                self.current_state["current_step"] = i + 1
                
                # Actualizar datos globales
                self.current_state["global_data"].update(result)
            
            self.current_state["status"] = "completed"
            
        except Exception as e:
            self.current_state["status"] = "error"
            self.current_state["error"] = str(e)
            raise
        
        finally:
            # Guardar en historial
            self.execution_history.append(self.current_state.copy())
        
        return self.current_state
    
    def _resolve_variables(self, data: Any) -> Any:
        """Resuelve variables del tipo ${step.step_name.field} en los datos"""
        if isinstance(data, dict):
            return {k: self._resolve_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_variables(item) for item in data]
        elif isinstance(data, str):
            # Check if it's a variable reference
            if data.startswith('${') and data.endswith('}'):
                return self._resolve_string_variables(data)
            else:
                return data
        else:
            return data
    
    def _resolve_string_variables(self, text: str) -> Any:
        """Resuelve variables en strings y retorna el valor real"""
        pattern = r'\$\{step\.([^.]+)\.([^}]+)\}'
        
        # Check if the entire string is a single variable reference
        match = re.fullmatch(pattern, text)
        if match:
            step_name = match.group(1)
            field_path = match.group(2)
            
            # Buscar resultado del paso
            if step_name in self.current_state["step_results"]:
                step_result = self.current_state["step_results"][step_name]
                
                # Navegar por el path del campo
                try:
                    value = self._get_nested_value(step_result, field_path)
                    return value  # Retornar el valor real, no string
                except (KeyError, IndexError, TypeError) as e:
                    print(f"Warning: Could not resolve {text}: {e}")
                    return text  # Mantener original si no se puede resolver
            else:
                print(f"Warning: Step {step_name} not found in results")
                return text  # Mantener original si no se encuentra el paso
        
        # If it's not a single variable, treat as string and do substitution
        def replace_var(match):
            step_name = match.group(1)
            field_path = match.group(2)
            
            # Buscar resultado del paso
            if step_name in self.current_state["step_results"]:
                step_result = self.current_state["step_results"][step_name]
                
                # Navegar por el path del campo
                try:
                    value = self._get_nested_value(step_result, field_path)
                    return str(value)
                except (KeyError, IndexError, TypeError) as e:
                    print(f"Warning: Could not resolve {match.group(0)}: {e}")
                    return match.group(0)  # Mantener original si no se puede resolver
            else:
                print(f"Warning: Step {step_name} not found in results")
                return match.group(0)  # Mantener original si no se encuentra el paso
        
        return re.sub(pattern, replace_var, text)
    
    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Obtiene un valor anidado usando notación de punto con soporte para arrays"""
        parts = path.split('.')
        current = data
        
        for part in parts:
            # Handle array indexing like "draws[0]"
            if '[' in part and ']' in part:
                key = part[:part.index('[')]
                index = int(part[part.index('[')+1:part.index(']')])
                
                if isinstance(current, dict):
                    current = current[key]
                else:
                    raise KeyError(f"No se puede acceder a {key} en {type(current)}")
                
                if isinstance(current, list):
                    current = current[index]
                else:
                    raise KeyError(f"No se puede acceder al índice {index} en {type(current)}")
            else:
                # Regular key access
                if isinstance(current, dict):
                    current = current[part]
                elif isinstance(current, list):
                    current = current[int(part)]
                else:
                    raise KeyError(f"No se puede acceder a {part} en {type(current)}")
        
        return current
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene el estado de una ejecución específica"""
        for execution in self.execution_history:
            if execution["execution_id"] == execution_id:
                return execution
        return None
    
    def get_all_executions(self) -> List[Dict[str, Any]]:
        """Obtiene todas las ejecuciones"""
        return self.execution_history.copy()

# Instancia global del ejecutor
pipeline_executor = PipelineExecutor()