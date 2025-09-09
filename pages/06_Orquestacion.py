import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json

st.set_page_config(
    page_title="Orquestacion - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title("ORQUESTACION Y PIPELINE")
st.markdown("---")

# Simulacion de estado del pipeline
@st.cache_data
def get_pipeline_status():
    """Genera estado del pipeline para demostrar la funcionalidad."""
    stages = [
        "acopio_bruto",
        "calidad_datos", 
        "t70_processing",
        "gematria_analysis",
        "subliminal_processing",
        "quantum_layer",
        "correlation",
        "assembly",
        "result_generation"
    ]
    
    pipeline_status = {}
    for stage in stages:
        pipeline_status[stage] = {
            'status': random.choice(['completed', 'running', 'failed', 'pending']),
            'start_time': (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat(),
            'duration': random.randint(10, 300),
            'retry_count': random.randint(0, 3),
            'error_message': None
        }
        
        if pipeline_status[stage]['status'] == 'failed':
            pipeline_status[stage]['error_message'] = random.choice([
                "Timeout en operacion",
                "Error de conexion a API",
                "Datos insuficientes",
                "Error de validacion"
            ])
    
    return pipeline_status

# Obtener estado del pipeline
pipeline_status = get_pipeline_status()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stages = len(pipeline_status)
    st.metric("Total Etapas", total_stages)
    
with col2:
    completed_stages = len([s for s in pipeline_status.values() if s['status'] == 'completed'])
    st.metric("Completadas", completed_stages)
    
with col3:
    running_stages = len([s for s in pipeline_status.values() if s['status'] == 'running'])
    st.metric("En Ejecucion", running_stages)
    
with col4:
    failed_stages = len([s for s in pipeline_status.values() if s['status'] == 'failed'])
    st.metric("Fallidas", failed_stages)

st.markdown("---")

# Estado del pipeline
st.subheader("ESTADO DEL PIPELINE")

# Mostrar cada etapa del pipeline
for stage_name, stage_info in pipeline_status.items():
    status_icon = {
        'completed': 'COMPLETADO',
        'running': 'EJECUTANDO',
        'failed': 'FALLIDO',
        'pending': 'PENDIENTE'
    }.get(stage_info['status'], 'DESCONOCIDO')
    
    status_color = {
        'completed': 'success',
        'running': 'info',
        'failed': 'error',
        'pending': 'warning'
    }.get(stage_info['status'], 'info')
    
    with st.expander(f"{status_icon} - {stage_name.replace('_', ' ').title()}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Estado:** {stage_info['status'].upper()}")
            st.write(f"**Inicio:** {stage_info['start_time']}")
            st.write(f"**Duracion:** {stage_info['duration']} segundos")
            st.write(f"**Reintentos:** {stage_info['retry_count']}")
            
            if stage_info['error_message']:
                st.error(f"**Error:** {stage_info['error_message']}")
        
        with col2:
            if stage_info['status'] == 'failed':
                if st.button(f"Reintentar {stage_name}", key=f"retry_{stage_name}"):
                    st.success(f"Reintentando {stage_name}")
                    st.rerun()
            
            if stage_info['status'] == 'running':
                st.info("En ejecucion...")
                if st.button(f"Detener {stage_name}", key=f"stop_{stage_name}"):
                    st.warning(f"Deteniendo {stage_name}")
                    st.rerun()

# Logs del pipeline
st.markdown("---")
st.subheader("LOGS DEL PIPELINE")

# Simular logs del pipeline
if st.button("Actualizar Logs"):
    st.session_state.pipeline_logs_updated = True

if 'pipeline_logs_updated' in st.session_state and st.session_state.pipeline_logs_updated:
    # Simular logs recientes
    pipeline_logs = [
        {"timestamp": datetime.now().isoformat(), "stage": "acopio_bruto", "level": "INFO", "message": "Iniciando acopio de noticias"},
        {"timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(), "stage": "calidad_datos", "level": "INFO", "message": "Validando calidad de datos"},
        {"timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(), "stage": "t70_processing", "level": "WARNING", "message": "Tiempo de procesamiento alto"},
        {"timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(), "stage": "gematria_analysis", "level": "INFO", "message": "Analisis gematria completado"},
        {"timestamp": (datetime.now() - timedelta(minutes=4)).isoformat(), "stage": "subliminal_processing", "level": "ERROR", "message": "Error en procesamiento subliminal"},
        {"timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(), "stage": "quantum_layer", "level": "INFO", "message": "Capa cuantica inicializada"}
    ]
    
    for log in pipeline_logs:
        if log["level"] == "ERROR":
            st.error(f"{log['timestamp']} - {log['stage']} - {log['level']}: {log['message']}")
        elif log["level"] == "WARNING":
            st.warning(f"{log['timestamp']} - {log['stage']} - {log['level']}: {log['message']}")
        else:
            st.info(f"{log['timestamp']} - {log['stage']} - {log['level']}: {log['message']}")

# Configuracion de reintentos
st.markdown("---")
st.subheader("CONFIGURACION DE REINTENTOS")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Parametros de Reintento")
    
    max_retries = st.number_input("Maximo de reintentos", value=3, min_value=1, max_value=10)
    backoff_seconds = st.number_input("Tiempo entre reintentos (segundos)", value=5, min_value=1, max_value=60)
    timeout_seconds = st.number_input("Timeout por operacion (segundos)", value=300, min_value=30, max_value=3600)
    
    if st.button("Guardar Configuracion", use_container_width=True):
        st.success("Configuracion guardada")

with col2:
    st.subheader("Estadisticas de Reintentos")
    
    # Simular estadisticas
    retry_stats = {
        "Total operaciones": 150,
        "Reintentos realizados": 23,
        "Tasa de exito": "87.3%",
        "Tiempo promedio de recuperacion": "45 segundos"
    }
    
    for metric, value in retry_stats.items():
        st.metric(metric, value)

# Monitoreo en tiempo real
st.markdown("---")
st.subheader("MONITOREO EN TIEMPO REAL")

# Simular monitoreo
if st.button("Iniciar Monitoreo"):
    st.session_state.monitoring_active = True

if 'monitoring_active' in st.session_state and st.session_state.monitoring_active:
    # Simular metricas en tiempo real
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CPU Pipeline", f"{random.randint(20, 80)}%")
    
    with col2:
        st.metric("Memoria Pipeline", f"{random.randint(30, 90)}%")
    
    with col3:
        st.metric("Throughput", f"{random.randint(100, 500)} ops/min")
    
    # Grafico de rendimiento
    st.subheader("Rendimiento del Pipeline")
    
    # Simular datos de rendimiento
    performance_data = pd.DataFrame({
        'Tiempo': [datetime.now() - timedelta(minutes=i) for i in range(10, 0, -1)],
        'Throughput': [random.randint(100, 500) for _ in range(10)],
        'Latencia': [random.uniform(0.1, 2.0) for _ in range(10)]
    })
    
    st.line_chart(performance_data.set_index('Tiempo'))

# Acciones del pipeline
st.markdown("---")
st.subheader("ACCIONES DEL PIPELINE")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Iniciar Pipeline", use_container_width=True):
        st.success("Pipeline iniciado")
        st.rerun()

with col2:
    if st.button("Pausar Pipeline", use_container_width=True):
        st.warning("Pipeline pausado")

with col3:
    if st.button("Reiniciar Pipeline", use_container_width=True):
        st.info("Pipeline reiniciado")
        st.rerun()

# Footer
st.markdown("---")
st.caption("Modulo de Orquestacion y Pipeline - VISION Premium")
