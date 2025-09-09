import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json

st.set_page_config(
    page_title="QA Healthcheck - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title("QA HEALTHCHECK")
st.markdown("---")

# Simulacion de estado del sistema
@st.cache_data
def get_system_status():
    """Genera estado del sistema para demostrar la funcionalidad."""
    components = [
        "news_collection",
        "data_quality",
        "t70_processing",
        "gematria_analysis",
        "subliminal_processing",
        "quantum_layer",
        "correlation_engine",
        "result_generation",
        "feedback_system",
        "observability"
    ]
    
    system_status = {}
    for component in components:
        system_status[component] = {
            'status': random.choice(['healthy', 'warning', 'critical']),
            'last_check': (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            'response_time': random.uniform(0.1, 2.0),
            'error_count': random.randint(0, 5),
            'warning_count': random.randint(0, 10)
        }
    
    return system_status

# Obtener estado del sistema
system_status = get_system_status()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_components = len(system_status)
    st.metric("Total Componentes", total_components)
    
with col2:
    healthy_components = len([c for c in system_status.values() if c['status'] == 'healthy'])
    st.metric("Componentes Sanos", healthy_components)
    
with col3:
    warning_components = len([c for c in system_status.values() if c['status'] == 'warning'])
    st.metric("Advertencias", warning_components)
    
with col4:
    critical_components = len([c for c in system_status.values() if c['status'] == 'critical'])
    st.metric("Criticos", critical_components)

st.markdown("---")

# Estado de componentes
st.subheader("ESTADO DE COMPONENTES")

# Mostrar cada componente
for component_name, component_info in system_status.items():
    status_icon = {
        'healthy': 'SANO',
        'warning': 'ADVERTENCIA',
        'critical': 'CRITICO'
    }.get(component_info['status'], 'DESCONOCIDO')
    
    status_color = {
        'healthy': 'success',
        'warning': 'warning',
        'critical': 'error'
    }.get(component_info['status'], 'info')
    
    with st.expander(f"{status_icon} - {component_name.replace('_', ' ').title()}"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**Estado:** {component_info['status'].upper()}")
            st.write(f"**Ultima verificacion:** {component_info['last_check']}")
            st.write(f"**Tiempo de respuesta:** {component_info['response_time']:.3f}s")
            st.write(f"**Errores:** {component_info['error_count']}")
            st.write(f"**Advertencias:** {component_info['warning_count']}")
        
        with col2:
            # Metricas del componente
            st.metric("Estado", status_icon)
            st.metric("Respuesta", f"{component_info['response_time']:.3f}s")
            
            # Botones de accion segun el estado
            if component_info['status'] == 'critical':
                if st.button(f"Reiniciar {component_name}", key=f"restart_{component_name}"):
                    st.success(f"Reiniciando {component_name}")
                    st.rerun()
                
                if st.button(f"Ver Logs {component_name}", key=f"logs_{component_name}"):
                    st.info(f"Mostrando logs de {component_name}")
            
            elif component_info['status'] == 'warning':
                if st.button(f"Diagnosticar {component_name}", key=f"diagnose_{component_name}"):
                    st.info(f"Diagnosticando {component_name}")
            
            else:
                st.success("Componente funcionando correctamente")

# Pruebas de salud
st.markdown("---")
st.subheader("PRUEBAS DE SALUD")

# Simular pruebas de salud
@st.cache_data
def get_health_tests():
    """Genera pruebas de salud de muestra."""
    tests = [
        {
            'name': 'Conectividad de Base de Datos',
            'status': random.choice(['passed', 'failed', 'warning']),
            'duration': random.uniform(0.1, 1.0),
            'message': 'Conexion exitosa a la base de datos'
        },
        {
            'name': 'API de Noticias',
            'status': random.choice(['passed', 'failed', 'warning']),
            'duration': random.uniform(0.2, 2.0),
            'message': 'API respondiendo correctamente'
        },
        {
            'name': 'Procesamiento T70',
            'status': random.choice(['passed', 'failed', 'warning']),
            'duration': random.uniform(0.5, 3.0),
            'message': 'Procesamiento T70 funcionando'
        },
        {
            'name': 'Analisis Gematria',
            'status': random.choice(['passed', 'failed', 'warning']),
            'duration': random.uniform(0.3, 2.5),
            'message': 'Analisis gematria operativo'
        },
        {
            'name': 'Sistema de Feedback',
            'status': random.choice(['passed', 'failed', 'warning']),
            'duration': random.uniform(0.1, 1.5),
            'message': 'Sistema de feedback activo'
        }
    ]
    
    # Agregar mensajes de error para pruebas fallidas
    for test in tests:
        if test['status'] == 'failed':
            test['message'] = random.choice([
                'Error de conexion',
                'Timeout en operacion',
                'Datos insuficientes',
                'Error de autenticacion',
                'Servicio no disponible'
            ])
        elif test['status'] == 'warning':
            test['message'] = random.choice([
                'Respuesta lenta',
                'Algunos datos faltantes',
                'Uso alto de memoria',
                'Latencia elevada'
            ])
    
    return tests

health_tests = get_health_tests()

# Mostrar resultados de pruebas
col1, col2 = st.columns(2)

with col1:
    st.subheader("Resultados de Pruebas")
    
    for test in health_tests:
        if test['status'] == 'passed':
            st.success(f"{test['name']} - {test['duration']:.3f}s")
        elif test['status'] == 'failed':
            st.error(f"{test['name']} - {test['duration']:.3f}s")
        else:
            st.warning(f"{test['name']} - {test['duration']:.3f}s")
        
        st.caption(f"  {test['message']}")

with col2:
    st.subheader("Resumen de Pruebas")
    
    passed_tests = len([t for t in health_tests if t['status'] == 'passed'])
    failed_tests = len([t for t in health_tests if t['status'] == 'failed'])
    warning_tests = len([t for t in health_tests if t['status'] == 'warning'])
    
    st.metric("Pruebas Exitosas", passed_tests)
    st.metric("Pruebas Fallidas", failed_tests)
    st.metric("Pruebas con Advertencia", warning_tests)
    
    # Calcular porcentaje de exito
    success_rate = (passed_tests / len(health_tests)) * 100
    st.metric("Tasa de Exito", f"{success_rate:.1f}%")

# Metricas de rendimiento
st.markdown("---")
st.subheader("METRICAS DE RENDIMIENTO")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Tiempo de Respuesta por Componente")
    
    # Crear grafico de tiempo de respuesta
    response_times = {name: info['response_time'] for name, info in system_status.items()}
    st.bar_chart(response_times)
    
    # Tabla de metricas
    st.subheader("Metricas Detalladas")
    metrics_df = pd.DataFrame([
        {
            'Componente': name,
            'Estado': info['status'],
            'Respuesta (s)': f"{info['response_time']:.3f}",
            'Errores': info['error_count'],
            'Advertencias': info['warning_count']
        }
        for name, info in system_status.items()
    ])
    
    st.dataframe(metrics_df, use_container_width=True)

with col2:
    st.subheader("Distribucion de Estados")
    
    # Grafico de distribucion de estados
    status_counts = pd.Series([info['status'] for info in system_status.values()]).value_counts()
    st.bar_chart(status_counts)
    
    # Tendencias temporales
    st.subheader("Tendencias de Errores")
    
    # Simular tendencias de errores
    error_trends = []
    for i in range(24):
        error_trends.append({
            'hora': i,
            'errores': random.randint(0, 10),
            'advertencias': random.randint(0, 20)
        })
    
    error_df = pd.DataFrame(error_trends)
    st.line_chart(error_df.set_index('hora'))

# Alertas y notificaciones
st.markdown("---")
st.subheader("ALERTAS Y NOTIFICACIONES")

# Simular alertas del sistema
if st.button("Verificar Alertas"):
    st.session_state.alerts_checked = True

if 'alerts_checked' in st.session_state and st.session_state.alerts_checked:
    # Simular alertas
    alerts = [
        {
            "severity": "critical",
            "component": "news_collection",
            "message": "Error de conexion a fuentes de noticias",
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        },
        {
            "severity": "warning",
            "component": "t70_processing",
            "message": "Tiempo de procesamiento alto",
            "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
            "status": "resolved"
        },
        {
            "severity": "info",
            "component": "data_quality",
            "message": "Nuevos filtros aplicados",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "status": "active"
        }
    ]
    
    for alert in alerts:
        severity_color = {
            "critical": "CRITICO",
            "warning": "ADVERTENCIA",
            "info": "INFORMACION"
        }.get(alert["severity"], "DESCONOCIDO")
        
        status_icon = "RESUELTO" if alert["status"] == "resolved" else "ACTIVO"
        
        with st.expander(f"{severity_color} - {alert['component']} - {status_icon}"):
            st.write(f"**Severidad:** {alert['severity'].upper()}")
            st.write(f"**Componente:** {alert['component']}")
            st.write(f"**Mensaje:** {alert['message']}")
            st.write(f"**Timestamp:** {alert['timestamp']}")
            st.write(f"**Estado:** {alert['status']}")
            
            if alert["status"] == "active":
                if st.button(f"Marcar Resuelto", key=f"resolve_alert_{alert['timestamp']}"):
                    alert["status"] = "resolved"
                    st.success("Alerta marcada como resuelta")
                    st.rerun()

# Acciones de QA
st.markdown("---")
st.subheader("ACCIONES DE QA")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Ejecutar Todas las Pruebas", use_container_width=True):
        st.info("Ejecutando todas las pruebas de salud...")
        st.rerun()

with col2:
    if st.button("Generar Reporte de Salud", use_container_width=True):
        health_report = {
            "system_status": system_status,
            "health_tests": health_tests,
            "total_components": total_components,
            "healthy_components": healthy_components,
            "success_rate": round(success_rate, 1),
            "generated_at": datetime.now().isoformat()
        }
        st.json(health_report)

with col3:
    if st.button("Limpiar Logs", use_container_width=True):
        st.success("Logs limpiados")
        st.rerun()

# Footer
st.markdown("---")
st.caption("Modulo de QA Healthcheck - VISION Premium")
