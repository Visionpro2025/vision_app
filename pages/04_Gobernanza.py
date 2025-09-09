import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json

st.set_page_config(
    page_title="Gobernanza - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title("GOBERNANZA Y SEGURIDAD")
st.markdown("---")

# Simulacion de eventos de auditoria
@st.cache_data
def get_sample_audit_events():
    """Genera eventos de auditoria de muestra para demostrar la funcionalidad."""
    events = []
    
    actors = ["admin", "user_001", "system", "api_gateway"]
    actions = ["login", "logout", "data_access", "data_modify", "config_change", "export_data"]
    resources = ["news_data", "user_profile", "system_config", "analytics_report", "gematria_results"]
    outcomes = ["success", "failure", "warning"]
    
    for i in range(50):
        event = {
            'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
            'actor': random.choice(actors),
            'action': random.choice(actions),
            'resource': random.choice(resources),
            'outcome': random.choice(outcomes),
            'ip_address': f"192.168.1.{random.randint(1, 255)}",
            'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            'session_id': f"session_{random.randint(1000, 9999)}"
        }
        events.append(event)
    
    return events

# Obtener eventos de auditoria
audit_events = get_sample_audit_events()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Eventos", len(audit_events))
    
with col2:
    success_events = len([e for e in audit_events if e['outcome'] == 'success'])
    st.metric("Eventos Exitosos", success_events)
    
with col3:
    failure_events = len([e for e in audit_events if e['outcome'] == 'failure'])
    st.metric("Eventos Fallidos", failure_events)
    
with col4:
    warning_events = len([e for e in audit_events if e['outcome'] == 'warning'])
    st.metric("Advertencias", warning_events)

st.markdown("---")

# Panel de auditoria
st.subheader("REGISTRO DE AUDITORIA")

# Filtros
col1, col2, col3, col4 = st.columns(4)

with col1:
    actor_filter = st.selectbox("Actor", ["Todos"] + list(set([e['actor'] for e in audit_events])))
    
with col2:
    action_filter = st.selectbox("Accion", ["Todas"] + list(set([e['action'] for e in audit_events])))
    
with col3:
    resource_filter = st.selectbox("Recurso", ["Todos"] + list(set([e['resource'] for e in audit_events])))
    
with col4:
    outcome_filter = st.selectbox("Resultado", ["Todos"] + list(set([e['outcome'] for e in audit_events])))

# Aplicar filtros
filtered_events = audit_events.copy()

if actor_filter != "Todos":
    filtered_events = [e for e in filtered_events if e['actor'] == actor_filter]

if action_filter != "Todas":
    filtered_events = [e for e in filtered_events if e['action'] == action_filter]

if resource_filter != "Todos":
    filtered_events = [e for e in filtered_events if e['resource'] == resource_filter]

if outcome_filter != "Todos":
    filtered_events = [e for e in filtered_events if e['outcome'] == outcome_filter]

# Mostrar eventos filtrados
st.success(f"Mostrando {len(filtered_events)} eventos")

# Tabla de eventos
if filtered_events:
    df_events = pd.DataFrame(filtered_events)
    df_events['timestamp'] = pd.to_datetime(df_events['timestamp'])
    df_events = df_events.sort_values('timestamp', ascending=False)
    
    # Mostrar solo las primeras 20 filas para evitar sobrecarga
    st.dataframe(df_events.head(20), use_container_width=True)
    
    if len(filtered_events) > 20:
        st.info(f"Mostrando 20 de {len(filtered_events)} eventos. Use los filtros para reducir resultados.")

# Analisis de seguridad
st.markdown("---")
st.subheader("ANALISIS DE SEGURIDAD")

col1, col2 = st.columns(2)

with col1:
    # Distribucion por actor
    st.subheader("Actividad por Actor")
    actor_counts = pd.Series([e['actor'] for e in audit_events]).value_counts()
    st.bar_chart(actor_counts)
    
    # Distribucion por accion
    st.subheader("Acciones Mas Comunes")
    action_counts = pd.Series([e['action'] for e in audit_events]).value_counts()
    st.bar_chart(action_counts)

with col2:
    # Distribucion por resultado
    st.subheader("Distribucion de Resultados")
    outcome_counts = pd.Series([e['outcome'] for e in audit_events]).value_counts()
    # Usar bar_chart en lugar de pie_chart
    st.bar_chart(outcome_counts)
    
    # Analisis temporal
    st.subheader("Actividad Temporal")
    hourly_events = [datetime.fromisoformat(e['timestamp']).hour for e in audit_events]
    hourly_counts = pd.Series(hourly_events).value_counts().sort_index()
    st.line_chart(hourly_counts)

# PII Masking Demo
st.markdown("---")
st.subheader("DEMOSTRACION DE ENMASCARADO PII")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Texto Original")
    sample_texts = [
        "El usuario admin@vision.com accedio al sistema",
        "Contacto: +53 5 123 4567 para mas informacion",
        "Direccion: 123 Main Street, New York, NY 10001, USA",
        "ID de tarjeta: 1234-5678-9012-3456"
    ]
    
    selected_text = st.selectbox("Seleccionar texto de ejemplo:", sample_texts)
    st.text_area("Texto original:", selected_text, height=100)

with col2:
    st.subheader("Texto Enmascarado")
    # Simular enmascarado PII
    masked_text = selected_text
    masked_text = masked_text.replace("@", "[at]")
    masked_text = masked_text.replace("+53 5 123 4567", "[PHONE]")
    masked_text = masked_text.replace("123 Main Street, New York, NY 10001, USA", "[ADDRESS]")
    masked_text = masked_text.replace("1234-5678-9012-3456", "[CARD_ID]")
    
    st.text_area("Texto enmascarado:", masked_text, height=100)
    
    if st.button("Aplicar Enmascarado", use_container_width=True):
        st.success("Enmascarado aplicado")

# Alertas de seguridad
st.markdown("---")
st.subheader("ALERTAS DE SEGURIDAD")

# Simular alertas
security_alerts = [
    {
        "severity": "high",
        "message": "Multiples intentos de login fallidos desde IP 192.168.1.100",
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    },
    {
        "severity": "medium",
        "message": "Acceso a datos sensibles fuera de horario laboral",
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "status": "resolved"
    },
    {
        "severity": "low",
        "message": "Nueva sesion iniciada desde dispositivo no reconocido",
        "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        "status": "active"
    }
]

for alert in security_alerts:
    severity_color = {
        "high": "ALTO",
        "medium": "MEDIO",
        "low": "BAJO"
    }.get(alert["severity"], "DESCONOCIDO")
    
    status_icon = "RESUELTO" if alert["status"] == "resolved" else "ACTIVO"
    
    with st.expander(f"{severity_color} - {alert['message']} - {status_icon}"):
        st.write(f"**Severidad:** {alert['severity'].upper()}")
        st.write(f"**Timestamp:** {alert['timestamp']}")
        st.write(f"**Estado:** {alert['status']}")
        
        if alert["status"] == "active":
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Marcar Resuelto", key=f"resolve_{alert['timestamp']}"):
                    alert["status"] = "resolved"
                    st.success("Alerta marcada como resuelta")
                    st.rerun()
            with col2:
                if st.button(f"Notificar", key=f"notify_{alert['timestamp']}"):
                    st.info("Notificacion enviada al equipo de seguridad")

# Acciones de gobernanza
st.markdown("---")
st.subheader("ACCIONES DE GOBERNANZA")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Generar Reporte de Auditoria", use_container_width=True):
        audit_report = {
            "total_events": len(audit_events),
            "success_rate": round(success_events / len(audit_events) * 100, 2),
            "security_alerts": len([a for a in security_alerts if a["status"] == "active"]),
            "generated_at": datetime.now().isoformat()
        }
        st.json(audit_report)

with col2:
    if st.button("Analisis de Anomalias", use_container_width=True):
        st.info("Analisis de anomalias iniciado")

with col3:
    if st.button("Configuracion de Seguridad", use_container_width=True):
        st.info("Panel de configuracion de seguridad")

# Footer
st.markdown("---")
st.caption("Modulo de Gobernanza y Seguridad - VISION Premium")
