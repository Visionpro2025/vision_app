import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json

st.set_page_config(
    page_title="Catalogo - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title(" **CATALOGO DE DATASETS**")
st.markdown("---")

# Simulacion de versiones de dataset
@st.cache_data
def get_sample_datasets():
    """Genera datasets de muestra para demostrar la funcionalidad."""
    datasets = []
    
    sources = ["RSS", "GoogleNews", "Bing", "Twitter"]
    filters_options = [
        {"tz": "America/New_York", "fresh<=h": 48},
        {"tz": "UTC", "fresh<=h": 24},
        {"category": "economy", "fresh<=h": 72},
        {"source": "Granma", "fresh<=h": 24},
        {"category": "politics", "fresh<=h": 48}
    ]
    
    for i in range(10):
        filters = random.choice(filters_options)
        source_summary = {
            "providers": random.sample(sources, random.randint(1, 3)),
            "last_update": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "total_sources": random.randint(5, 20)
        }
        
        datasets.append({
            'id': f"dataset_{i:03d}",
            'created_at': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat(),
            'source_summary': source_summary,
            'filters': filters,
            'record_count': random.randint(50, 500)
        })
    
    return datasets

# Obtener datasets de muestra
datasets = get_sample_datasets()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(" Total Datasets", len(datasets))
    
with col2:
    total_records = sum(d['record_count'] for d in datasets)
    st.metric(" Total Registros", total_records)
    
with col3:
    avg_records = round(total_records / len(datasets), 1)
    st.metric(" Promedio por Dataset", avg_records)
    
with col4:
    latest_dataset = max(datasets, key=lambda x: x['created_at'])
    hours_ago = (datetime.now() - datetime.fromisoformat(latest_dataset['created_at'])).total_seconds() / 3600
    st.metric(" Ultimo Dataset", f"{int(hours_ago)}h")

st.markdown("---")

# Lista de datasets
st.subheader(" **DATASETS DISPONIBLES**")

# Filtros
col1, col2, col3 = st.columns(3)

with col1:
    min_records = st.slider(" Minimo de registros", 0, 500, 0)
    
with col2:
    source_filter = st.selectbox(" Fuente", ["Todas"] + list(set([s for d in datasets for s in d['source_summary']['providers']])))
    
with col3:
    date_filter = st.selectbox(" Fecha", ["Todas", "Ultimas 24h", "Ultimas 48h", "Ultima semana"])

# Aplicar filtros
filtered_datasets = datasets.copy()

if min_records > 0:
    filtered_datasets = [d for d in filtered_datasets if d['record_count'] >= min_records]

if source_filter != "Todas":
    filtered_datasets = [d for d in filtered_datasets if source_filter in d['source_summary']['providers']]

if date_filter != "Todas":
    now = datetime.now()
    if date_filter == "Ultimas 24h":
        cutoff = now - timedelta(hours=24)
    elif date_filter == "Ultimas 48h":
        cutoff = now - timedelta(hours=48)
    elif date_filter == "Ultima semana":
        cutoff = now - timedelta(days=7)
    
    filtered_datasets = [d for d in filtered_datasets if datetime.fromisoformat(d['created_at']) >= cutoff]

# Mostrar datasets filtrados
st.success(f" Mostrando {len(filtered_datasets)} datasets")

for i, dataset in enumerate(filtered_datasets):
    with st.expander(f" Dataset {dataset['id']} - {dataset['record_count']} registros"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write(f"**ID:** {dataset['id']}")
            st.write(f"**Creado:** {dataset['created_at']}")
            st.write(f"**Registros:** {dataset['record_count']}")
            
            # Filtros aplicados
            st.write("**Filtros:**")
            for key, value in dataset['filters'].items():
                st.write(f"  - {key}: {value}")
            
            # Resumen de fuentes
            st.write("**Fuentes:**")
            for provider in dataset['source_summary']['providers']:
                st.write(f"  - {provider}")
        
        with col2:
            # Metricas del dataset
            st.metric("Registros", dataset['record_count'])
            st.metric("Fuentes", len(dataset['source_summary']['providers']))
            
            # Botones de accion
            if st.button(f" Descargar {dataset['id']}", key=f"download_{i}"):
                st.success(f" Dataset {dataset['id']} descargado")
            
            if st.button(f" Analizar {dataset['id']}", key=f"analyze_{i}"):
                st.info(f" Analisis iniciado para {dataset['id']}")

# Estadisticas
st.markdown("---")
st.subheader(" **ESTADISTICAS DEL CATALOGO**")

col1, col2 = st.columns(2)

with col1:
    # Distribucion por numero de registros
    st.subheader(" Distribucion por Tamano")
    record_counts = [d['record_count'] for d in datasets]
    # Crear histograma usando bar_chart
    import numpy as np
    hist, bins = np.histogram(record_counts, bins=10)
    hist_data = pd.DataFrame({
        'Rango': [f"{bins[i]:.0f}-{bins[i+1]:.0f}" for i in range(len(bins)-1)],
        'Frecuencia': hist
    })
    st.bar_chart(hist_data.set_index('Rango'))
    
    # Top datasets por tamano
    st.subheader(" Top 5 por Tamano")
    top_datasets = sorted(datasets, key=lambda x: x['record_count'], reverse=True)[:5]
    for i, dataset in enumerate(top_datasets, 1):
        st.write(f"{i}. {dataset['id']}: {dataset['record_count']} registros")

with col2:
    # Distribucion temporal
    st.subheader(" Creacion de Datasets")
    creation_hours = [datetime.fromisoformat(d['created_at']).hour for d in datasets]
    hourly_counts = pd.Series(creation_hours).value_counts().sort_index()
    st.line_chart(hourly_counts)
    
    # Fuentes mas utilizadas
    st.subheader(" Fuentes Mas Utilizadas")
    all_providers = [p for d in datasets for p in d['source_summary']['providers']]
    provider_counts = pd.Series(all_providers).value_counts()
    st.bar_chart(provider_counts)

# Acciones del catalogo
st.markdown("---")
st.subheader(" **ACCIONES DEL CATALOGO**")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Actualizar Catalogo", use_container_width=True):
        st.success(" Catalogo actualizado")
        st.rerun()

with col2:
    if st.button(" Generar Reporte", use_container_width=True):
        # Simular generacion de reporte
        report = {
            "total_datasets": len(datasets),
            "total_records": total_records,
            "avg_records_per_dataset": avg_records,
            "generated_at": datetime.now().isoformat()
        }
        st.json(report)

with col3:
    if st.button(" Configuracion", use_container_width=True):
        st.info(" Panel de configuracion del catalogo")

# Footer
st.markdown("---")
st.caption(" Modulo de Catalogo - VISION Premium")
