# modules/transparency_module.py
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

@dataclass
class DecisionNode:
    """Nodo de decisión en el árbol de decisiones."""
    id: str
    layer: str
    decision_type: str
    input_data: Dict[str, Any]
    weights: Dict[str, float]
    output: Any
    confidence: float
    reasoning: str
    timestamp: datetime
    parent_id: Optional[str] = None
    children: List[str] = None

@dataclass
class TraceabilityPath:
    """Camino completo de trazabilidad desde datos fuente hasta resultado."""
    trace_id: str
    start_time: datetime
    end_time: datetime
    data_sources: List[str]
    processing_steps: List[DecisionNode]
    final_result: Any
    quality_metrics: Dict[str, float]
    confidence_score: float

class TransparencyModule:
    """Módulo para explicabilidad avanzada y trazabilidad completa."""
    
    def __init__(self):
        self.decision_tree = {}
        self.traceability_paths = {}
        self.current_trace = None
        
    def start_trace(self, trace_name: str = None) -> str:
        """Inicia un nuevo camino de trazabilidad."""
        trace_id = str(uuid.uuid4())
        self.current_trace = TraceabilityPath(
            trace_id=trace_id,
            start_time=datetime.now(),
            end_time=None,
            data_sources=[],
            processing_steps=[],
            final_result=None,
            quality_metrics={},
            confidence_score=0.0
        )
        self.traceability_paths[trace_id] = self.current_trace
        return trace_id
    
    def add_decision_node(self, layer: str, decision_type: str, input_data: Dict, 
                         weights: Dict[str, float], output: Any, confidence: float, 
                         reasoning: str, parent_id: str = None) -> str:
        """Añade un nodo de decisión al árbol."""
        node_id = str(uuid.uuid4())
        
        node = DecisionNode(
            id=node_id,
            layer=layer,
            decision_type=decision_type,
            input_data=input_data,
            weights=weights,
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now(),
            parent_id=parent_id,
            children=[]
        )
        
        if parent_id and parent_id in self.decision_tree:
            self.decision_tree[parent_id].children.append(node_id)
        
        self.decision_tree[node_id] = node
        
        if self.current_trace:
            self.current_trace.processing_steps.append(node)
        
        return node_id
    
    def end_trace(self, final_result: Any, quality_metrics: Dict[str, float], 
                  confidence_score: float):
        """Finaliza el camino de trazabilidad actual."""
        if self.current_trace:
            self.current_trace.end_time = datetime.now()
            self.current_trace.final_result = final_result
            self.current_trace.quality_metrics = quality_metrics
            self.current_trace.confidence_score = confidence_score
    
    def generate_explanation_report(self, trace_id: str) -> Dict[str, Any]:
        """Genera un reporte completo de explicación."""
        if trace_id not in self.traceability_paths:
            return {"error": "Trace ID no encontrado"}
        
        trace = self.traceability_paths[trace_id]
        
        # Calcular métricas de calidad
        total_steps = len(trace.processing_steps)
        avg_confidence = sum(step.confidence for step in trace.processing_steps) / total_steps if total_steps > 0 else 0
        
        # Agrupar por capas
        layer_summary = {}
        for step in trace.processing_steps:
            if step.layer not in layer_summary:
                layer_summary[step.layer] = {
                    "steps": 0,
                    "total_confidence": 0,
                    "decisions": []
                }
            layer_summary[step.layer]["steps"] += 1
            layer_summary[step.layer]["total_confidence"] += step.confidence
            layer_summary[step.layer]["decisions"].append({
                "type": step.decision_type,
                "confidence": step.confidence,
                "reasoning": step.reasoning
            })
        
        # Calcular confianza promedio por capa
        for layer in layer_summary:
            layer_summary[layer]["avg_confidence"] = (
                layer_summary[layer]["total_confidence"] / 
                layer_summary[layer]["steps"]
            )
        
        return {
            "trace_id": trace_id,
            "execution_time": (trace.end_time - trace.start_time).total_seconds(),
            "total_steps": total_steps,
            "overall_confidence": avg_confidence,
            "layer_summary": layer_summary,
            "quality_metrics": trace.quality_metrics,
            "data_sources": trace.data_sources,
            "processing_timeline": [
                {
                    "step": i + 1,
                    "layer": step.layer,
                    "decision": step.decision_type,
                    "confidence": step.confidence,
                    "timestamp": step.timestamp.isoformat(),
                    "reasoning": step.reasoning
                }
                for i, step in enumerate(trace.processing_steps)
            ]
        }
    
    def create_decision_tree_visualization(self, trace_id: str) -> go.Figure:
        """Crea visualización del árbol de decisiones."""
        if trace_id not in self.traceability_paths:
            return go.Figure()
        
        trace = self.traceability_paths[trace_id]
        
        # Crear subplot para el árbol
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Árbol de Decisiones", "Confianza por Capa"),
            specs=[[{"type": "treemap"}, {"type": "bar"}]]
        )
        
        # Árbol de decisiones como treemap
        labels = []
        parents = []
        values = []
        colors = []
        
        for step in trace.processing_steps:
            labels.append(f"{step.layer}: {step.decision_type}")
            parents.append(step.parent_id if step.parent_id else "ROOT")
            values.append(step.confidence * 100)
            
            # Color por capa
            layer_colors = {
                "T70": "#FF6B6B",
                "Gematría": "#4ECDC4", 
                "Subliminal": "#45B7D1",
                "Cuántico": "#96CEB4",
                "Correlación": "#FFEAA7",
                "Ensamblaje": "#DDA0DD"
            }
            colors.append(layer_colors.get(step.layer, "#95A5A6"))
        
        fig.add_trace(
            go.Treemap(
                labels=labels,
                parents=parents,
                values=values,
                marker_colors=colors,
                textinfo="label+value",
                hovertemplate="<b>%{label}</b><br>Confianza: %{value:.1f}%<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Gráfico de confianza por capa
        layer_confidence = {}
        for step in trace.processing_steps:
            if step.layer not in layer_confidence:
                layer_confidence[step.layer] = []
            layer_confidence[step.layer].append(step.confidence)
        
        layers = list(layer_confidence.keys())
        avg_confidences = [sum(conf) / len(conf) * 100 for conf in layer_confidence.values()]
        
        fig.add_trace(
            go.Bar(
                x=layers,
                y=avg_confidences,
                marker_color=colors[:len(layers)],
                text=[f"{conf:.1f}%" for conf in avg_confidences],
                textposition="auto",
                hovertemplate="<b>%{x}</b><br>Confianza Promedio: %{y:.1f}%<extra></extra>"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Análisis de Decisiones del Protocolo",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def create_correlation_heatmap(self, trace_id: str) -> go.Figure:
        """Crea heatmap de correlaciones entre capas."""
        if trace_id not in self.traceability_paths:
            return go.Figure()
        
        trace = self.traceability_paths[trace_id]
        
        # Extraer capas únicas
        layers = list(set(step.layer for step in trace.processing_steps))
        layers.sort()
        
        # Crear matriz de correlaciones (simulada para demo)
        correlation_matrix = []
        for i, layer1 in enumerate(layers):
            row = []
            for j, layer2 in enumerate(layers):
                if i == j:
                    row.append(1.0)  # Correlación perfecta consigo misma
                else:
                    # Simular correlación basada en confianza promedio
                    layer1_steps = [s for s in trace.processing_steps if s.layer == layer1]
                    layer2_steps = [s for s in trace.processing_steps if s.layer == layer2]
                    
                    if layer1_steps and layer2_steps:
                        avg_conf1 = sum(s.confidence for s in layer1_steps) / len(layer1_steps)
                        avg_conf2 = sum(s.confidence for s in layer2_steps) / len(layer2_steps)
                        # Correlación basada en similitud de confianza
                        correlation = 1 - abs(avg_conf1 - avg_conf2)
                        row.append(max(0, correlation))
                    else:
                        row.append(0.0)
            correlation_matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix,
            x=layers,
            y=layers,
            colorscale="Viridis",
            zmin=0,
            zmax=1,
            text=[[f"{val:.2f}" for val in row] for row in correlation_matrix],
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate="<b>%{x}</b> ↔ <b>%{y}</b><br>Correlación: %{z:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Correlaciones entre Capas del Protocolo",
            xaxis_title="Capas",
            yaxis_title="Capas",
            height=500
        )
        
        return fig
    
    def create_timeline_visualization(self, trace_id: str) -> go.Figure:
        """Crea visualización de timeline de ejecución."""
        if trace_id not in self.traceability_paths:
            return go.Figure()
        
        trace = self.traceability_paths[trace_id]
        
        # Crear timeline
        fig = go.Figure()
        
        for i, step in enumerate(trace.processing_steps):
            # Color por capa
            layer_colors = {
                "T70": "#FF6B6B",
                "Gematría": "#4ECDC4", 
                "Subliminal": "#45B7D1",
                "Cuántico": "#96CEB4",
                "Correlación": "#FFEAA7",
                "Ensamblaje": "#DDA0DD"
            }
            
            fig.add_trace(go.Scatter(
                x=[step.timestamp],
                y=[step.layer],
                mode="markers+text",
                marker=dict(
                    size=20,
                    color=layer_colors.get(step.layer, "#95A5A6"),
                    symbol="circle"
                ),
                text=f"{step.decision_type}<br>{step.confidence:.1%}",
                textposition="middle right",
                name=step.layer,
                showlegend=False,
                hovertemplate="<b>%{y}</b><br>%{text}<br>Timestamp: %{x}<extra></extra>"
            ))
        
        fig.update_layout(
            title="Timeline de Ejecución del Protocolo",
            xaxis_title="Tiempo",
            yaxis_title="Capas",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def render_explanation_ui(self, trace_id: str):
        """Renderiza la interfaz de explicación en Streamlit."""
        if trace_id not in self.traceability_paths:
            st.error("Trace ID no encontrado")
            return
        
        report = self.generate_explanation_report(trace_id)
        
        st.subheader("🔍 **Reporte de Explicabilidad y Trazabilidad**")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tiempo Total", f"{report['execution_time']:.1f}s")
        with col2:
            st.metric("Pasos Totales", report['total_steps'])
        with col3:
            st.metric("Confianza General", f"{report['overall_confidence']:.1%}")
        with col4:
            st.metric("Calidad", f"{report['quality_metrics'].get('overall_quality', 0):.1%}")
        
        # Resumen por capas
        st.subheader("📊 **Resumen por Capas**")
        layer_data = []
        for layer, data in report['layer_summary'].items():
            layer_data.append({
                "Capa": layer,
                "Pasos": data['steps'],
                "Confianza Promedio": f"{data['avg_confidence']:.1%}",
                "Decisiones": len(data['decisions'])
            })
        
        if layer_data:
            import pandas as pd
            layer_df = pd.DataFrame(layer_data)
            st.dataframe(layer_df, use_container_width=True, hide_index=True)
        
        # Visualizaciones
        st.subheader("📈 **Visualizaciones de Análisis**")
        
        tab1, tab2, tab3 = st.tabs(["🌳 Árbol de Decisiones", "🔥 Correlaciones", "⏰ Timeline"])
        
        with tab1:
            fig_tree = self.create_decision_tree_visualization(trace_id)
            st.plotly_chart(fig_tree, use_container_width=True)
        
        with tab2:
            fig_heatmap = self.create_correlation_heatmap(trace_id)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with tab3:
            fig_timeline = self.create_timeline_visualization(trace_id)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Detalles de procesamiento
        st.subheader("🔍 **Detalles de Procesamiento**")
        with st.expander("Ver Timeline Completo", expanded=False):
            timeline_df = pd.DataFrame(report['processing_timeline'])
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
        
        # Métricas de calidad
        st.subheader("📊 **Métricas de Calidad**")
        quality_df = pd.DataFrame([
            {"Métrica": k, "Valor": f"{v:.2f}" if isinstance(v, float) else str(v)}
            for k, v in report['quality_metrics'].items()
        ])
        st.dataframe(quality_df, use_container_width=True, hide_index=True)

# Instancia global
transparency_module = TransparencyModule()









