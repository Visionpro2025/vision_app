import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

st.set_page_config(
    page_title="Feedback - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title("FEEDBACK DEL USUARIO")
st.markdown("---")

# Simulacion de series
@st.cache_data
def get_sample_series():
    series = []
    for i in range(20):
        main_numbers = sorted(random.sample(range(1, 71), 5))
        special_number = random.randint(1, 25)
        series.append({
            'id': f"series_{i:03d}",
            'main_numbers': main_numbers,
            'special_number': special_number,
            'generated_at': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
            'source': random.choice(['gematria', 't70', 'subliminal', 'quantum', 'combined']),
            'confidence': round(random.uniform(0.6, 0.95), 3)
        })
    return series

series_data = get_sample_series()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Series", len(series_data))
    
with col2:
    total_feedback = random.randint(10, 50)
    st.metric("Total Feedback", total_feedback)
    
with col3:
    useful_series = random.randint(5, 25)
    st.metric("Series Utiles", useful_series)
    
with col4:
    utility_rate = round(useful_series / total_feedback * 100, 1) if total_feedback > 0 else 0
    st.metric("Tasa de Utilidad", f"{utility_rate}%")

st.markdown("---")

# Interfaz de feedback
st.subheader("INTERFAZ DE FEEDBACK")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Seleccionar Serie")
    selected_series = st.selectbox(
        "Seleccionar serie para evaluar:",
        options=[f"{s['id']}: {s['main_numbers']} + {s['special_number']}" for s in series_data]
    )
    
    if selected_series:
        series_id = selected_series.split(':')[0]
        series_info = next((s for s in series_data if s['id'] == series_id), None)
        
        if series_info:
            st.write(f"**Serie:** {series_info['main_numbers']} + {series_info['special_number']}")
            st.write(f"**Generada:** {series_info['generated_at']}")
            st.write(f"**Fuente:** {series_info['source']}")
            st.write(f"**Confianza:** {series_info['confidence']}")

with col2:
    st.subheader("Dar Feedback")
    
    if selected_series and series_info:
        useful = st.radio("¿Fue util esta serie?", ["Si", "No", "Parcialmente"])
        rating = st.slider("Calificacion (1-10):", min_value=1, max_value=10, value=5)
        comments = st.text_area("Comentarios adicionales:")
        
        if st.button("Enviar Feedback", use_container_width=True):
            feedback_data = {
                'series_id': series_id,
                'useful': useful,
                'rating': rating,
                'comments': comments,
                'timestamp': datetime.now().isoformat(),
                'user_id': 'user_001'
            }
            st.success("Feedback enviado exitosamente")
            st.json(feedback_data)

# Historial de feedback
st.markdown("---")
st.subheader("HISTORIAL DE FEEDBACK")

@st.cache_data
def get_feedback_history():
    feedback_history = []
    feedback_types = ["Si", "No", "Parcialmente"]
    feedback_sources = ["gematria", "t70", "subliminal", "quantum", "combined"]
    
    for i in range(30):
        feedback_history.append({
            'id': f"feedback_{i:03d}",
            'series_id': f"series_{random.randint(0, 19):03d}",
            'useful': random.choice(feedback_types),
            'rating': random.randint(1, 10),
            'comments': random.choice([
                "Excelente prediccion",
                "No fue util",
                "Mas o menos acertado",
                "Muy preciso",
                "Necesita mejora"
            ]),
            'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
            'source': random.choice(feedback_sources),
            'user_id': f"user_{random.randint(1, 5):03d}"
        })
    return feedback_history

feedback_history = get_feedback_history()

# Filtros
col1, col2, col3 = st.columns(3)

with col1:
    feedback_filter = st.selectbox("Filtrar por utilidad:", ["Todos"] + list(set([f['useful'] for f in feedback_history])))
    
with col2:
    source_filter = st.selectbox("Filtrar por fuente:", ["Todas"] + list(set([f['source'] for f in feedback_history])))
    
with col3:
    rating_filter = st.selectbox("Filtrar por calificacion:", ["Todas"] + ["1-3", "4-6", "7-10"])

# Aplicar filtros
filtered_feedback = feedback_history.copy()

if feedback_filter != "Todos":
    filtered_feedback = [f for f in filtered_feedback if f['useful'] == feedback_filter]

if source_filter != "Todas":
    filtered_feedback = [f for f in filtered_feedback if f['source'] == source_filter]

if rating_filter != "Todas":
    if rating_filter == "1-3":
        filtered_feedback = [f for f in filtered_feedback if f['rating'] <= 3]
    elif rating_filter == "4-6":
        filtered_feedback = [f for f in filtered_feedback if 4 <= f['rating'] <= 6]
    elif rating_filter == "7-10":
        filtered_feedback = [f for f in filtered_feedback if f['rating'] >= 7]

st.success(f"Mostrando {len(filtered_feedback)} feedbacks")

if filtered_feedback:
    df_feedback = pd.DataFrame(filtered_feedback)
    df_feedback['timestamp'] = pd.to_datetime(df_feedback['timestamp'])
    df_feedback = df_feedback.sort_values('timestamp', ascending=False)
    st.dataframe(df_feedback.head(15), use_container_width=True)

# Analisis
st.markdown("---")
st.subheader("ANALISIS DE FEEDBACK")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribucion por Utilidad")
    useful_counts = pd.Series([f['useful'] for f in feedback_history]).value_counts()
    st.bar_chart(useful_counts)
    
    st.subheader("Distribucion por Calificacion")
    rating_counts = pd.Series([f['rating'] for f in feedback_history]).value_counts().sort_index()
    st.bar_chart(rating_counts)

with col2:
    st.subheader("Feedback por Fuente")
    source_counts = pd.Series([f['source'] for f in feedback_history]).value_counts()
    st.bar_chart(source_counts)
    
    st.subheader("Tendencias Temporales")
    hourly_feedback = [datetime.fromisoformat(f['timestamp']).hour for f in feedback_history]
    hourly_counts = pd.Series(hourly_feedback).value_counts().sort_index()
    st.line_chart(hourly_counts)

# Metricas
st.markdown("---")
st.subheader("METRICAS DE CALIDAD")

col1, col2, col3 = st.columns(3)

with col1:
    avg_rating = sum(f['rating'] for f in feedback_history) / len(feedback_history)
    st.metric("Calificacion Promedio", f"{avg_rating:.2f}/10")

with col2:
    high_ratings = len([f for f in feedback_history if f['rating'] >= 7])
    satisfaction_rate = round(high_ratings / len(feedback_history) * 100, 1)
    st.metric("Tasa de Satisfaccion", f"{satisfaction_rate}%")

with col3:
    recent_feedback = len([f for f in feedback_history 
                          if datetime.fromisoformat(f['timestamp']) > datetime.now() - timedelta(hours=24)])
    st.metric("Feedback Ultimas 24h", recent_feedback)

# Acciones
st.markdown("---")
st.subheader("ACCIONES DE FEEDBACK")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generar Reporte", use_container_width=True):
        report = {
            "total_feedback": len(feedback_history),
            "avg_rating": round(avg_rating, 2),
            "satisfaction_rate": satisfaction_rate,
            "generated_at": datetime.now().isoformat()
        }
        st.json(report)

with col2:
    if st.button("Exportar Datos", use_container_width=True):
        csv_data = pd.DataFrame(feedback_history)
        st.download_button(
            label="Descargar CSV",
            data=csv_data.to_csv(index=False),
            file_name=f"feedback_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

with col3:
    if st.button("Limpiar Historial", use_container_width=True):
        st.warning("Historial limpiado")
        st.rerun()

st.markdown("---")
st.caption("Modulo de Feedback del Usuario - VISION Premium")








