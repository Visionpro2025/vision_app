# modules/feedback_module.py
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import streamlit as st
import hashlib
import uuid

@dataclass
class SeriesFeedback:
    """Feedback de una serie específica."""
    feedback_id: str
    series_numbers: List[int]
    useful: bool
    note: str
    user_rating: int  # 1-5 estrellas
    timestamp: datetime
    protocol_run: str
    feedback_type: str  # "manual", "auto", "correction"
    metadata: Dict[str, Any]

@dataclass
class FeedbackSummary:
    """Resumen de feedback del sistema."""
    total_feedback: int
    useful_series: int
    not_useful_series: int
    average_rating: float
    top_series: List[List[int]]
    recent_feedback: List[SeriesFeedback]
    improvement_suggestions: List[str]

class FeedbackModule:
    """Módulo para gestión de feedback del usuario sobre series generadas."""
    
    def __init__(self):
        self.feedback_file = Path("logs/feedback_data.json")
        self.feedback_file.parent.mkdir(exist_ok=True)
        self.feedback_history = []
        
        # Cargar feedback existente
        self._load_feedback()
    
    def _load_feedback(self):
        """Carga feedback desde archivo JSON."""
        try:
            if self.feedback_file.exists():
                with open(self.feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for feedback_data in data.get("feedback", []):
                        # Convertir fecha de string a datetime
                        feedback_data["timestamp"] = datetime.fromisoformat(feedback_data["timestamp"])
                        
                        # Crear objeto SeriesFeedback
                        feedback = SeriesFeedback(**feedback_data)
                        self.feedback_history.append(feedback)
                        
                st.success(f"✅ Cargados {len(self.feedback_history)} registros de feedback")
            else:
                st.info("ℹ️ No hay historial de feedback previo")
                
        except Exception as e:
            st.warning(f"⚠️ Error cargando feedback: {e}")
    
    def _save_feedback(self):
        """Guarda feedback en archivo JSON."""
        try:
            feedback_data = {
                "feedback": [asdict(feedback) for feedback in self.feedback_history],
                "last_updated": datetime.now().isoformat(),
                "total_records": len(self.feedback_history)
            }
            
            with open(self.feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            st.error(f"❌ Error guardando feedback: {e}")
    
    def record_feedback(self, series: List[int], useful: bool, note: str = "", 
                       user_rating: int = 3, protocol_run: str = "", 
                       feedback_type: str = "manual", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Registra feedback de una serie.
        
        Args:
            series: Lista de números de la serie
            useful: Si la serie fue útil
            note: Nota adicional del usuario
            user_rating: Calificación de 1-5 estrellas
            protocol_run: Identificador de la corrida del protocolo
            feedback_type: Tipo de feedback
            metadata: Metadatos adicionales
            
        Returns:
            ID del feedback registrado
        """
        try:
            # Validar rating
            if not 1 <= user_rating <= 5:
                user_rating = 3
                st.warning("⚠️ Rating debe estar entre 1-5, usando valor por defecto")
            
            # Crear feedback
            feedback = SeriesFeedback(
                feedback_id=str(uuid.uuid4())[:8],
                series_numbers=sorted(series),
                useful=useful,
                note=note.strip(),
                user_rating=user_rating,
                timestamp=datetime.now(),
                protocol_run=protocol_run or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                feedback_type=feedback_type,
                metadata=metadata or {}
            )
            
            # Añadir a historial
            self.feedback_history.append(feedback)
            
            # Guardar en archivo
            self._save_feedback()
            
            st.success(f"✅ Feedback registrado: Serie {series} marcada como {'útil' if useful else 'no útil'}")
            return feedback.feedback_id
            
        except Exception as e:
            st.error(f"❌ Error registrando feedback: {e}")
            return ""
    
    def get_feedback_by_series(self, series: List[int]) -> List[SeriesFeedback]:
        """Obtiene feedback para una serie específica."""
        series_sorted = sorted(series)
        return [
            feedback for feedback in self.feedback_history
            if sorted(feedback.series_numbers) == series_sorted
        ]
    
    def get_feedback_summary(self) -> FeedbackSummary:
        """Obtiene resumen del feedback del sistema."""
        if not self.feedback_history:
            return FeedbackSummary(
                total_feedback=0,
                useful_series=0,
                not_useful_series=0,
                average_rating=0.0,
                top_series=[],
                recent_feedback=[],
                improvement_suggestions=[]
            )
        
        # Calcular métricas
        total_feedback = len(self.feedback_history)
        useful_series = len([f for f in self.feedback_history if f.useful])
        not_useful_series = total_feedback - useful_series
        
        # Rating promedio
        ratings = [f.user_rating for f in self.feedback_history if f.user_rating > 0]
        average_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Series más útiles
        series_usefulness = {}
        for feedback in self.feedback_history:
            series_key = tuple(sorted(feedback.series_numbers))
            if series_key not in series_usefulness:
                series_usefulness[series_key] = {"useful": 0, "total": 0}
            
            series_usefulness[series_key]["total"] += 1
            if feedback.useful:
                series_usefulness[series_key]["useful"] += 1
        
        # Top series por utilidad
        top_series = []
        for series, stats in series_usefulness.items():
            if stats["total"] >= 2:  # Solo series con múltiples feedbacks
                usefulness_ratio = stats["useful"] / stats["total"]
                top_series.append((list(series), usefulness_ratio))
        
        top_series.sort(key=lambda x: x[1], reverse=True)
        top_series = [series for series, _ in top_series[:10]]  # Top 10
        
        # Feedback reciente
        recent_feedback = sorted(self.feedback_history, key=lambda x: x.timestamp, reverse=True)[:20]
        
        # Sugerencias de mejora
        improvement_suggestions = self._generate_improvement_suggestions()
        
        return FeedbackSummary(
            total_feedback=total_feedback,
            useful_series=useful_series,
            not_useful_series=not_useful_series,
            average_rating=average_rating,
            top_series=top_series,
            recent_feedback=recent_feedback,
            improvement_suggestions=improvement_suggestions
        )
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """Genera sugerencias de mejora basadas en el feedback."""
        suggestions = []
        
        if not self.feedback_history:
            return ["Comienza a registrar feedback para obtener sugerencias de mejora"]
        
        # Analizar patrones
        low_ratings = [f for f in self.feedback_history if f.user_rating <= 2]
        not_useful = [f for f in self.feedback_history if not f.useful]
        
        if len(low_ratings) > len(self.feedback_history) * 0.3:
            suggestions.append("Considerar revisar la calidad de las series generadas")
        
        if len(not_useful) > len(self.feedback_history) * 0.5:
            suggestions.append("Evaluar la relevancia de los criterios de selección")
        
        # Sugerencias basadas en feedback reciente
        recent_feedback = [f for f in self.feedback_history 
                          if f.timestamp > datetime.now() - timedelta(days=7)]
        
        if recent_feedback:
            avg_recent_rating = sum(f.user_rating for f in recent_feedback) / len(recent_feedback)
            if avg_recent_rating < 3.0:
                suggestions.append("Revisar cambios recientes en el protocolo")
        
        if not suggestions:
            suggestions.append("El sistema está funcionando bien según el feedback recibido")
        
        return suggestions
    
    def export_feedback_csv(self) -> str:
        """Exporta feedback a formato CSV."""
        if not self.feedback_history:
            return ""
        
        try:
            df = pd.DataFrame([
                {
                    'ID': f.feedback_id,
                    'Serie': ', '.join(map(str, f.series_numbers)),
                    'Útil': 'Sí' if f.useful else 'No',
                    'Nota': f.note,
                    'Rating': f.user_rating,
                    'Fecha': f.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Protocolo': f.protocol_run,
                    'Tipo': f.feedback_type
                }
                for f in self.feedback_history
            ])
            
            return df.to_csv(index=False, encoding='utf-8')
            
        except Exception as e:
            st.error(f"❌ Error exportando feedback: {e}")
            return ""
    
    def render_feedback_interface(self):
        """Renderiza la interfaz de feedback en Streamlit."""
        st.subheader("💬 **SISTEMA DE FEEDBACK DE SERIES**")
        
        # Resumen de feedback
        summary = self.get_feedback_summary()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Feedback", summary.total_feedback)
        with col2:
            st.metric("Series Útiles", summary.useful_series)
        with col3:
            st.metric("Series No Útiles", summary.not_useful_series)
        with col4:
            st.metric("Rating Promedio", f"{summary.average_rating:.1f}")
        
        # Formulario de feedback
        with st.form("feedback_form"):
            st.write("**📝 Registrar Feedback de Serie**")
            
            # Input de serie
            series_input = st.text_input(
                "🎯 **Números de la serie** (separados por comas)",
                placeholder="Ej: 15, 23, 42, 7, 31",
                help="Ingresa los números de la serie separados por comas"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                useful = st.radio(
                    "✅ **¿Fue útil esta serie?**",
                    ["Sí", "No"],
                    horizontal=True
                )
                
                user_rating = st.selectbox(
                    "⭐ **Calificación**",
                    [5, 4, 3, 2, 1],
                    format_func=lambda x: "⭐" * x
                )
            
            with col2:
                protocol_run = st.text_input(
                    "🔄 **Protocolo/Corrida**",
                    placeholder="Ej: T70_GEM_20241201",
                    help="Identificador de la corrida del protocolo"
                )
                
                feedback_type = st.selectbox(
                    "📋 **Tipo de Feedback**",
                    ["manual", "auto", "correction"],
                    help="Tipo de feedback registrado"
                )
            
            note = st.text_area(
                "💭 **Nota adicional**",
                placeholder="Comentarios, observaciones o sugerencias...",
                help="Notas adicionales sobre la serie"
            )
            
            submitted = st.form_submit_button("💾 **GUARDAR FEEDBACK**", use_container_width=True)
        
        # Procesar feedback
        if submitted and series_input:
            try:
                # Parsear serie
                series_str = series_input.replace(" ", "")
                series = [int(x.strip()) for x in series_str.split(",") if x.strip().isdigit()]
                
                if not series:
                    st.error("❌ Ingresa números válidos separados por comas")
                elif len(series) < 3:
                    st.error("❌ La serie debe tener al menos 3 números")
                else:
                    # Registrar feedback
                    useful_bool = useful == "Sí"
                    feedback_id = self.record_feedback(
                        series=series,
                        useful=useful_bool,
                        note=note,
                        user_rating=user_rating,
                        protocol_run=protocol_run,
                        feedback_type=feedback_type
                    )
                    
                    if feedback_id:
                        st.success(f"✅ Feedback registrado con ID: {feedback_id}")
                        
            except ValueError:
                st.error("❌ Formato inválido. Usa números separados por comas")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        
        # Series más útiles
        if summary.top_series:
            st.subheader("🏆 **Series Más Útiles**")
            for i, series in enumerate(summary.top_series[:5]):
                st.write(f"**{i+1}.** {', '.join(map(str, series))}")
        
        # Feedback reciente
        if summary.recent_feedback:
            st.subheader("📋 **Feedback Reciente**")
            for feedback in summary.recent_feedback[:10]:
                with st.expander(f"📊 Serie {', '.join(map(str, feedback.series_numbers))} - {feedback.timestamp.strftime('%H:%M:%S')}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Nota:** {feedback.note or 'Sin nota'}")
                        st.write(f"**Protocolo:** {feedback.protocol_run}")
                        st.write(f"**Tipo:** {feedback.feedback_type}")
                    
                    with col2:
                        st.write(f"**Útil:** {'✅ Sí' if feedback.useful else '❌ No'}")
                        st.write(f"**Rating:** {'⭐' * feedback.user_rating}")
                        st.write(f"**ID:** {feedback.feedback_id}")
        
        # Sugerencias de mejora
        if summary.improvement_suggestions:
            st.subheader("💡 **Sugerencias de Mejora**")
            for suggestion in summary.improvement_suggestions:
                st.info(f"💡 {suggestion}")
        
        # Exportar feedback
        if summary.total_feedback > 0:
            st.subheader("📥 **Exportar Feedback**")
            csv_data = self.export_feedback_csv()
            if csv_data:
                st.download_button(
                    label="⬇️ Descargar Feedback (CSV)",
                    data=csv_data,
                    file_name=f"feedback_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Instancia global
feedback_module = FeedbackModule()








