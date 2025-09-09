# modules/force_panel.py — Panel de Fuerza Comparada
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd
import streamlit as st
from typing import List, Dict, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "__CONFIG" / "quantum_config.json"

class ForcePanel:
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Carga configuración del panel."""
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {
            "force_panel": {
                "t70_weight": 0.33,
                "gematria_weight": 0.33,
                "subliminal_weight": 0.34,
                "convergence_threshold": 0.7
            }
        }
    
    def _load_buffer_data(self, buffer_type: str) -> pd.DataFrame:
        """Carga datos de los buffers."""
        buffer_paths = {
            "GEM": ROOT / "__RUNS" / "GEMATRIA_IN",
            "SUB": ROOT / "__RUNS" / "SUBLIMINAL_IN", 
            "T70": ROOT / "__RUNS" / "T70_IN"
        }
        
        path = buffer_paths.get(buffer_type)
        if not path or not path.exists():
            return pd.DataFrame()
        
        # Cargar archivos más recientes
        files = sorted(path.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
        if not files:
            return pd.DataFrame()
        
        try:
            return pd.read_csv(files[0], dtype=str, encoding="utf-8")
        except Exception:
            return pd.DataFrame()
    
    def _extract_numbers_from_text(self, text: str) -> List[int]:
        """Extrae números del texto."""
        import re
        numbers = []
        
        # Números directos
        direct_numbers = re.findall(r'\b(\d{1,2})\b', text)
        numbers.extend([int(n) for n in direct_numbers if 1 <= int(n) <= 70])
        
        # Gematría básica
        if len(text) > 0:
            gematria_sum = sum(ord(c) for c in text) % 70 + 1
            numbers.append(gematria_sum)
        
        return list(set(numbers))
    
    def _calculate_layer_metrics(self, data: pd.DataFrame, layer_name: str) -> Dict:
        """Calcula métricas para una capa específica."""
        if data.empty:
            return {
                "layer": layer_name,
                "data_count": 0,
                "numbers": [],
                "frequency": {},
                "confidence": 0.0,
                "strength": 0.0
            }
        
        all_numbers = []
        for _, row in data.iterrows():
            text = f"{row.get('titular', '')} {row.get('resumen', '')}"
            numbers = self._extract_numbers_from_text(text)
            all_numbers.extend(numbers)
        
        # Calcular frecuencia
        frequency = {}
        for num in all_numbers:
            frequency[num] = frequency.get(num, 0) + 1
        
        # Calcular métricas
        total_numbers = len(all_numbers)
        unique_numbers = len(set(all_numbers))
        confidence = min(unique_numbers / 70.0, 1.0) if total_numbers > 0 else 0.0
        strength = min(total_numbers / 100.0, 1.0) if total_numbers > 0 else 0.0
        
        return {
            "layer": layer_name,
            "data_count": len(data),
            "numbers": all_numbers,
            "frequency": frequency,
            "confidence": confidence,
            "strength": strength
        }
    
    def _calculate_convergence(self, t70_metrics: Dict, gematria_metrics: Dict, subliminal_metrics: Dict) -> Dict:
        """Calcula convergencia entre las tres capas."""
        # Obtener números más frecuentes de cada capa
        t70_top = sorted(t70_metrics["frequency"].items(), key=lambda x: x[1], reverse=True)[:10]
        gematria_top = sorted(gematria_metrics["frequency"].items(), key=lambda x: x[1], reverse=True)[:10]
        subliminal_top = sorted(subliminal_metrics["frequency"].items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Encontrar números comunes
        t70_numbers = set(t70_metrics["frequency"].keys())
        gematria_numbers = set(gematria_metrics["frequency"].keys())
        subliminal_numbers = set(subliminal_metrics["frequency"].keys())
        
        common_numbers = t70_numbers & gematria_numbers & subliminal_numbers
        t70_gem_common = t70_numbers & gematria_numbers
        t70_sub_common = t70_numbers & subliminal_numbers
        gem_sub_common = gematria_numbers & subliminal_numbers
        
        # Calcular scores de convergencia
        convergence_score = len(common_numbers) / 70.0
        partial_convergence = (len(t70_gem_common) + len(t70_sub_common) + len(gem_sub_common)) / (3 * 70.0)
        
        # Números convergentes con sus frecuencias combinadas
        convergent_numbers = {}
        for num in common_numbers:
            freq_sum = (t70_metrics["frequency"].get(num, 0) + 
                       gematria_metrics["frequency"].get(num, 0) + 
                       subliminal_metrics["frequency"].get(num, 0))
            convergent_numbers[num] = freq_sum
        
        return {
            "convergence_score": convergence_score,
            "partial_convergence": partial_convergence,
            "common_numbers": list(common_numbers),
            "convergent_numbers": convergent_numbers,
            "t70_gem_common": list(t70_gem_common),
            "t70_sub_common": list(t70_sub_common),
            "gem_sub_common": list(gem_sub_common),
            "t70_top": t70_top,
            "gematria_top": gematria_top,
            "subliminal_top": subliminal_top
        }
    
    def generate_force_report(self, lottery: str) -> Dict:
        """Genera reporte completo de fuerza comparada."""
        # Cargar datos de las tres capas
        t70_data = self._load_buffer_data("T70")
        gematria_data = self._load_buffer_data("GEM")
        subliminal_data = self._load_buffer_data("SUB")
        
        # Calcular métricas por capa
        t70_metrics = self._calculate_layer_metrics(t70_data, "T70")
        gematria_metrics = self._calculate_layer_metrics(gematria_data, "Gematría")
        subliminal_metrics = self._calculate_layer_metrics(subliminal_data, "Subliminal")
        
        # Calcular convergencia
        convergence = self._calculate_convergence(t70_metrics, gematria_metrics, subliminal_metrics)
        
        # Calcular fuerza total
        total_strength = (
            t70_metrics["strength"] * self.config["force_panel"]["t70_weight"] +
            gematria_metrics["strength"] * self.config["force_panel"]["gematria_weight"] +
            subliminal_metrics["strength"] * self.config["force_panel"]["subliminal_weight"]
        )
        
        return {
            "lottery": lottery,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "layers": {
                "t70": t70_metrics,
                "gematria": gematria_metrics,
                "subliminal": subliminal_metrics
            },
            "convergence": convergence,
            "total_strength": total_strength,
            "recommendations": self._generate_recommendations(convergence, total_strength)
        }
    
    def _generate_recommendations(self, convergence: Dict, total_strength: float) -> List[str]:
        """Genera recomendaciones basadas en convergencia y fuerza."""
        recommendations = []
        
        # Recomendaciones basadas en convergencia
        if convergence["convergence_score"] > 0.1:
            recommendations.append(f"Alta convergencia detectada ({convergence['convergence_score']:.3f}). Los números {convergence['common_numbers']} aparecen en todas las capas.")
        
        if convergence["partial_convergence"] > 0.2:
            recommendations.append(f"Convergencia parcial significativa ({convergence['partial_convergence']:.3f}). Considerar números que aparecen en múltiples capas.")
        
        # Recomendaciones basadas en fuerza total
        if total_strength > 0.7:
            recommendations.append("Fuerza total alta. El sistema está bien alimentado con datos de todas las capas.")
        elif total_strength < 0.3:
            recommendations.append("Fuerza total baja. Considerar recargar datos de las capas antes de generar series.")
        
        # Recomendaciones específicas
        if convergence["common_numbers"]:
            top_convergent = sorted(convergence["convergent_numbers"].items(), key=lambda x: x[1], reverse=True)[:3]
            recommendations.append(f"Priorizar números convergentes: {[num for num, _ in top_convergent]}")
        
        if not recommendations:
            recommendations.append("No hay recomendaciones específicas en este momento. Continuar con el análisis estándar.")
        
        return recommendations

def render_force_panel(current_lottery: str):
    """Renderiza el panel de fuerza comparada."""
    st.subheader("📊 Panel de Fuerza Comparada")
    
    # Inicializar panel
    panel = ForcePanel()
    
    # Configuración
    st.markdown("#### ⚙️ Configuración de Pesos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        t70_weight = st.slider("Peso T70", 0.0, 1.0, panel.config["force_panel"]["t70_weight"], 0.01)
    with col2:
        gematria_weight = st.slider("Peso Gematría", 0.0, 1.0, panel.config["force_panel"]["gematria_weight"], 0.01)
    with col3:
        subliminal_weight = st.slider("Peso Subliminal", 0.0, 1.0, panel.config["force_panel"]["subliminal_weight"], 0.01)
    
    # Normalizar pesos
    total_weight = t70_weight + gematria_weight + subliminal_weight
    if total_weight > 0:
        t70_weight /= total_weight
        gematria_weight /= total_weight
        subliminal_weight /= total_weight
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración", use_container_width=True):
        panel.config["force_panel"].update({
            "t70_weight": t70_weight,
            "gematria_weight": gematria_weight,
            "subliminal_weight": subliminal_weight
        })
        
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(panel.config, indent=2, ensure_ascii=False), encoding="utf-8")
            st.success("✅ Configuración guardada")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
    
    # Generar reporte
    if st.button("📊 Generar Reporte de Fuerza", type="primary", use_container_width=True):
        with st.spinner("Analizando convergencia de capas..."):
            report = panel.generate_force_report(current_lottery)
        
        # Mostrar métricas principales
        st.markdown("#### 📈 Métricas Principales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Fuerza Total", f"{report['total_strength']:.3f}")
        with col2:
            st.metric("Convergencia", f"{report['convergence']['convergence_score']:.3f}")
        with col3:
            st.metric("Números Comunes", len(report['convergence']['common_numbers']))
        with col4:
            st.metric("Convergencia Parcial", f"{report['convergence']['partial_convergence']:.3f}")
        
        # Gráfico de fuerza por capa
        st.markdown("#### 📊 Fuerza por Capa")
        layers_data = report["layers"]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=["T70", "Gematría", "Subliminal"],
            y=[layers_data["t70"]["strength"], layers_data["gematria"]["strength"], layers_data["subliminal"]["strength"]],
            name="Fuerza",
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c']
        ))
        
        fig.update_layout(
            title="Fuerza Relativa por Capa",
            xaxis_title="Capa",
            yaxis_title="Fuerza (0-1)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Números convergentes
        st.markdown("#### 🎯 Números Convergentes")
        convergent_numbers = report['convergence']['convergent_numbers']
        
        if convergent_numbers:
            # Crear DataFrame para mostrar
            conv_df = pd.DataFrame([
                {"Número": num, "Frecuencia Total": freq}
                for num, freq in sorted(convergent_numbers.items(), key=lambda x: x[1], reverse=True)
            ])
            
            st.dataframe(conv_df, use_container_width=True, hide_index=True)
            
            # Gráfico de números convergentes
            fig2 = px.bar(
                conv_df.head(10),
                x="Número",
                y="Frecuencia Total",
                title="Top 10 Números Convergentes"
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No hay números convergentes entre las tres capas")
        
        # Análisis detallado por capa
        st.markdown("#### 🔍 Análisis Detallado por Capa")
        
        for layer_name, layer_data in layers_data.items():
            with st.expander(f"{layer_name} - {layer_data['data_count']} registros"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Confianza", f"{layer_data['confidence']:.3f}")
                    st.metric("Fuerza", f"{layer_data['strength']:.3f}")
                
                with col2:
                    # Top números de esta capa
                    top_numbers = sorted(layer_data["frequency"].items(), key=lambda x: x[1], reverse=True)[:5]
                    if top_numbers:
                        st.write("**Top 5 números:**")
                        for num, freq in top_numbers:
                            st.write(f"• {num}: {freq} veces")
        
        # Recomendaciones
        st.markdown("#### 💡 Recomendaciones")
        recommendations = report.get("recommendations", [])
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        else:
            st.info("No hay recomendaciones específicas en este momento")
        
        # Guardar reporte
        if st.button("💾 Guardar Reporte", use_container_width=True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = ROOT / "__RUNS" / f"force_report_{current_lottery}_{timestamp}.json"
            
            try:
                report_file.parent.mkdir(parents=True, exist_ok=True)
                report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
                st.success(f"✅ Reporte guardado: {report_file.name}")
            except Exception as e:
                st.error(f"❌ Error al guardar: {e}")
    
    # Estado de buffers
    st.markdown("#### 📊 Estado de Buffers")
    t70_data = panel._load_buffer_data("T70")
    gematria_data = panel._load_buffer_data("GEM")
    subliminal_data = panel._load_buffer_data("SUB")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 T70", f"{len(t70_data)} registros" if not t70_data.empty else "Vacío")
    col2.metric("🔡 Gematría", f"{len(gematria_data)} registros" if not gematria_data.empty else "Vacío")
    col3.metric("🌀 Subliminal", f"{len(subliminal_data)} registros" if not subliminal_data.empty else "Vacío")
