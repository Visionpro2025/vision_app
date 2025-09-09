import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json
import time

st.set_page_config(
    page_title="Observabilidad - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title("OBSERVABILIDAD Y MONITOREO")
st.markdown("---")

# Simulacion de metricas de observabilidad
@st.cache_data
def get_sample_metrics():
    """Genera metricas de muestra para demostrar la funcionalidad."""
    metrics = []
    
    endpoints = ["/api/news", "/api/gematria", "/api/subliminal", "/api/quantum", "/api/results"]
    
    for i in range(100):
        endpoint = random.choice(endpoints)
        timestamp = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        
        # Simular metricas de requests
        request_count = random.randint(1, 50)
        avg_latency = random.uniform(0.1, 2.0)
        error_rate = random.uniform(0, 0.1)
        
        metrics.append({
            'timestamp': timestamp.isoformat(),
            'endpoint': endpoint,
            'requests_total': request_count,
            'latency_seconds': avg_latency,
            'error_count': int(request_count * error_rate),
            'success_count': request_count - int(request_count * error_rate)
        })
    
    return metrics

# Obtener metricas
metrics = get_sample_metrics()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_requests = sum(m['requests_total'] for m in metrics)
    st.metric("Total Requests", total_requests)
    
with col2:
    avg_latency = sum(m['latency_seconds'] for m in metrics) / len(metrics)
    st.metric("Latencia Promedio", f"{avg_latency:.3f}s")
    
with col3:
    total_errors = sum(m['error_count'] for m in metrics)
    st.metric("Total Errores", total_errors)
    
with col4:
    success_rate = (total_requests - total_errors) / total_requests * 100
    st.metric("Tasa de Exito", f"{success_rate:.1f}%")

st.markdown("---")

# Metricas por endpoint
st.subheader("METRICAS POR ENDPOINT")

# Agrupar metricas por endpoint
endpoint_data = {}
for metric in metrics:
    endpoint = metric['endpoint']
    if endpoint not in endpoint_data:
        endpoint_data[endpoint] = {
            'requests': [],
            'latencies': [],
            'errors': []
        }
    
    endpoint_data[endpoint]['requests'].append(metric['requests_total'])
    endpoint_data[endpoint]['latencies'].append(metric['latency_seconds'])
    endpoint_data[endpoint]['errors'].append(metric['error_count'])

# Mostrar metricas por endpoint
col1, col2 = st.columns(2)

with col1:
    st.subheader("Requests por Endpoint")
    endpoint_requests = {ep: sum(data['requests']) for ep, data in endpoint_data.items()}
    st.bar_chart(endpoint_requests)
    
    # Tabla de metricas por endpoint
    st.subheader("Resumen por Endpoint")
    endpoint_summary = []
    for endpoint, data in endpoint_data.items():
        endpoint_summary.append({
            'Endpoint': endpoint,
            'Total Requests': sum(data['requests']),
            'Latencia Promedio': f"{sum(data['latencies'])/len(data['latencies']):.3f}s",
            'Total Errores': sum(data['errors'])
        })
    
    df_summary = pd.DataFrame(endpoint_summary)
    st.dataframe(df_summary, use_container_width=True)

with col2:
    st.subheader("Latencia por Endpoint")
    endpoint_latencies = {ep: sum(data['latencies'])/len(data['latencies']) for ep, data in endpoint_data.items()}
    st.bar_chart(endpoint_latencies)
    
    st.subheader("Errores por Endpoint")
    endpoint_errors = {ep: sum(data['errors']) for ep, data in endpoint_data.items()}
    st.bar_chart(endpoint_errors)

# Analisis temporal
st.markdown("---")
st.subheader("ANALISIS TEMPORAL")

# Agrupar metricas por hora
hourly_data = {}
for metric in metrics:
    hour = datetime.fromisoformat(metric['timestamp']).hour
    if hour not in hourly_data:
        hourly_data[hour] = {
            'requests': 0,
            'latencies': [],
            'errors': 0
        }
    
    hourly_data[hour]['requests'] += metric['requests_total']
    hourly_data[hour]['latencies'].append(metric['latency_seconds'])
    hourly_data[hour]['errors'] += metric['error_count']

# Ordenar por hora
sorted_hours = sorted(hourly_data.keys())
hourly_requests = [hourly_data[hour]['requests'] for hour in sorted_hours]
hourly_errors = [hourly_data[hour]['errors'] for hour in sorted_hours]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Requests por Hora")
    hourly_df = pd.DataFrame({
        'Hora': sorted_hours,
        'Requests': hourly_requests
    })
    st.line_chart(hourly_df.set_index('Hora'))

with col2:
    st.subheader("Errores por Hora")
    hourly_errors_df = pd.DataFrame({
        'Hora': sorted_hours,
        'Errores': hourly_errors
    })
    st.line_chart(hourly_errors_df.set_index('Hora'))

# Alertas y umbrales
st.markdown("---")
st.subheader("ALERTAS Y UMBRALES")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Configuracion de Umbrales")
    
    latency_threshold = st.slider("Umbral de Latencia (segundos)", 0.1, 5.0, 1.0, 0.1)
    error_threshold = st.slider("Umbral de Tasa de Error (%)", 0.0, 20.0, 5.0, 0.5)
    
    # Verificar umbrales
    high_latency_endpoints = []
    high_error_endpoints = []
    
    for endpoint, data in endpoint_data.items():
        avg_latency = sum(data['latencies']) / len(data['latencies'])
        error_rate = (sum(data['errors']) / sum(data['requests'])) * 100
        
        if avg_latency > latency_threshold:
            high_latency_endpoints.append(endpoint)
        
        if error_rate > error_threshold:
            high_error_endpoints.append(endpoint)
    
    if high_latency_endpoints:
        st.warning(f"Endpoints con latencia alta: {', '.join(high_latency_endpoints)}")
    else:
        st.success("Todos los endpoints estan dentro del umbral de latencia")
    
    if high_error_endpoints:
        st.error(f"Endpoints con tasa de error alta: {', '.join(high_error_endpoints)}")
    else:
        st.success("Todos los endpoints estan dentro del umbral de error")

with col2:
    st.subheader("Estado del Sistema")
    
    # Simular estado del sistema
    system_status = {
        "CPU Usage": random.uniform(20, 80),
        "Memory Usage": random.uniform(30, 90),
        "Disk Usage": random.uniform(40, 85),
        "Network I/O": random.uniform(10, 60)
    }
    
    for metric, value in system_status.items():
        if value > 80:
            st.error(f"{metric}: {value:.1f}% - CRITICO")
        elif value > 60:
            st.warning(f"{metric}: {value:.1f}% - ADVERTENCIA")
        else:
            st.success(f"{metric}: {value:.1f}% - NORMAL")

# Logs en tiempo real
st.markdown("---")
st.subheader("LOGS EN TIEMPO REAL")

# Simular logs
if st.button("Actualizar Logs"):
    st.session_state.logs_updated = True

if 'logs_updated' in st.session_state and st.session_state.logs_updated:
    # Simular logs recientes
    recent_logs = [
        {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Sistema funcionando normalmente"},
        {"timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(), "level": "WARNING", "message": "Latencia alta detectada en /api/gematria"},
        {"timestamp": (datetime.now() - timedelta(minutes=2)).isoformat(), "level": "INFO", "message": "Backup completado exitosamente"},
        {"timestamp": (datetime.now() - timedelta(minutes=3)).isoformat(), "level": "ERROR", "message": "Error de conexion a base de datos"},
        {"timestamp": (datetime.now() - timedelta(minutes=4)).isoformat(), "level": "INFO", "message": "Nuevo usuario registrado"}
    ]
    
    for log in recent_logs:
        if log["level"] == "ERROR":
            st.error(f"{log['timestamp']} - {log['level']}: {log['message']}")
        elif log["level"] == "WARNING":
            st.warning(f"{log['timestamp']} - {log['level']}: {log['message']}")
        else:
            st.info(f"{log['timestamp']} - {log['level']}: {log['message']}")

# Acciones de observabilidad
st.markdown("---")
st.subheader("ACCIONES DE OBSERVABILIDAD")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generar Reporte", use_container_width=True):
        report = {
            "total_requests": total_requests,
            "avg_latency": round(avg_latency, 3),
            "success_rate": round(success_rate, 1),
            "endpoints_monitored": len(endpoint_data),
            "generated_at": datetime.now().isoformat()
        }
        st.json(report)

with col2:
    if st.button("Limpiar Metricas", use_container_width=True):
        st.success("Metricas limpiadas")
        st.rerun()

with col3:
    if st.button("Exportar Datos", use_container_width=True):
        # Simular exportacion
        csv_data = pd.DataFrame(metrics)
        st.download_button(
            label="Descargar CSV",
            data=csv_data.to_csv(index=False),
            file_name=f"metricas_observabilidad_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.caption("Modulo de Observabilidad y Monitoreo - VISION Premium")
