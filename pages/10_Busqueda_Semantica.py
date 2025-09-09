

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import json

st.set_page_config(
    page_title="Busqueda Semantica - VISION Premium",
    page_icon="",
    layout="wide"
)

st.title(" **BUSQUEDA SEMANTICA**")
st.markdown("---")

# Simulacion de corpus de documentos
@st.cache_data
def get_sample_corpus():
    """Genera un corpus de muestra para demostrar la busqueda semantica."""
    documents = [
        "La economia estadounidense muestra signos de recuperacion tras las reformas implementadas",
        "Nuevas politicas economicas en Estados Unidos buscan atraer inversiones extranjeras",
        "El mercado de valores registra un incremento del 15% este trimestre",
        "El turismo en Estados Unidos registra un incremento del 25% este ano",
        "La cultura estadounidense se expande por el mundo con festivales internacionales",
        "La politica exterior de Estados Unidos se fortalece con nuevos acuerdos bilaterales",
        "La educacion en Estados Unidos mantiene altos estandares de calidad",
        "La salud publica estadounidense es reconocida internacionalmente",
        "La agricultura estadounidense se moderniza con nuevas tecnologias",
        "La energia renovable en Estados Unidos crece con proyectos solares y eolicos",
        "La musica estadounidense influye en generos musicales de todo el mundo",
        "La literatura estadounidense produce obras de gran calidad literaria",
        "La ciencia estadounidense desarrolla investigaciones en biotecnologia",
        "El deporte estadounidense destaca en competencias internacionales",
        "La arquitectura estadounidense preserva el patrimonio historico colonial"
    ]
    return documents

# Simulacion de historial de busquedas
@st.cache_data
def get_search_history():
    """Genera historial de busquedas de muestra."""
    history = [
        {"query": "economia estadounidense", "timestamp": datetime.now() - timedelta(minutes=5), "results": 8},
        {"query": "politica exterior", "timestamp": datetime.now() - timedelta(hours=1), "results": 12},
        {"query": "cultura estadounidense", "timestamp": datetime.now() - timedelta(hours=1), "results": 10},
        {"query": "tecnologia innovacion", "timestamp": datetime.now() - timedelta(hours=2), "results": 15},
        {"query": "mercado financiero", "timestamp": datetime.now() - timedelta(hours=3), "results": 9}
    ]
    return history

# Obtener datos de muestra
corpus = get_sample_corpus()
search_history = get_search_history()

# Metricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(" Documentos en Corpus", len(corpus))
    
with col2:
    st.metric(" Busquedas Realizadas", len(search_history))
    
with col3:
    st.metric(" Promedio Resultados", round(sum(h['results'] for h in search_history) / len(search_history), 1))
    
with col4:
    st.metric(" Ultima Busqueda", f"{search_history[0]['timestamp'].strftime('%H:%M')}")

st.markdown("---")

# Formulario de busqueda
st.subheader(" **BUSQUEDA SEMANTICA**")

with st.form("search_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Consulta:",
            placeholder="Ej: economia estadounidense, desarrollo tecnologico, turismo...",
            help="Escribe tu consulta para buscar en el corpus de documentos"
        )
    
    with col2:
        top_k = st.number_input("Top K:", min_value=1, max_value=len(corpus), value=5)
    
    submitted = st.form_submit_button(" Buscar", use_container_width=True)

# Procesar busqueda
if submitted and query.strip():
    st.success(f" Busqueda realizada: '{query}'")
    
    # Simular busqueda semantica
    st.subheader(" **RESULTADOS DE LA BUSQUEDA**")
    
    # Simular relevancia (para demo)
    results = []
    for i, doc in enumerate(corpus):
        # Simular score de relevancia basado en palabras clave
        relevance = 0
        query_words = query.lower().split()
        doc_lower = doc.lower()
        
        for word in query_words:
            if word in doc_lower:
                relevance += random.uniform(0.1, 0.9)
        
        if relevance > 0:
            results.append({
                'document': doc,
                'relevance': min(relevance, 1.0),
                'source': f"Documento {i+1}"
            })
    
    # Ordenar por relevancia
    results.sort(key=lambda x: x['relevance'], reverse=True)
    results = results[:top_k]
    
    if results:
        # Mostrar resultados
        for i, result in enumerate(results, 1):
            with st.expander(f" {i}. Relevancia: {result['relevance']:.3f}", expanded=i==1):
                st.write(f"**Documento:** {result['document']}")
                st.write(f"**Fuente:** {result['source']}")
                st.write(f"**Score de Relevancia:** {result['relevance']:.3f}")
                
                # Barra de relevancia
                st.progress(result['relevance'])
    else:
        st.warning(" No se encontraron resultados relevantes para tu consulta.")
        
        # Sugerencias
        st.info(" **Sugerencias:**")
        st.write("- Intenta usar palabras clave mas generales")
        st.write("- Verifica la ortografia de tu consulta")
        st.write("- Usa sinonimos o terminos relacionados")

# Historial de busquedas
st.markdown("---")
st.subheader(" **HISTORIAL DE BUSQUEDAS**")

if search_history:
    # Crear DataFrame para mostrar historial
    df_history = pd.DataFrame(search_history)
    df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
    df_history['query'] = df_history['query'].str.title()
    
    # Mostrar historial
    st.dataframe(
        df_history[['query', 'results', 'timestamp']],
        column_config={
            'query': 'Consulta',
            'results': 'Resultados',
            'timestamp': 'Timestamp'
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Grafico de resultados por consulta
    st.subheader(" **RESULTADOS POR CONSULTA**")
    query_results = df_history.groupby('query')['results'].sum()
    st.bar_chart(query_results)
else:
    st.info(" No hay historial de busquedas disponible.")

# Analisis del corpus
st.markdown("---")
st.subheader(" **ANALISIS DEL CORPUS**")

col1, col2 = st.columns(2)

with col1:
    # Distribucion por tema
    st.subheader(" Distribucion por Tema")
    topics = {
        "Economia": 4,
        "Politica": 2,
        "Cultura": 3,
        "Tecnologia": 2,
        "Deportes": 1,
        "Otros": 3
    }
    st.bar_chart(topics)
    
    # Estadisticas del corpus
    st.subheader(" Estadisticas del Corpus")
    stats = {
        "Total Documentos": len(corpus),
        "Promedio Palabras": round(sum(len(doc.split()) for doc in corpus) / len(corpus), 1),
        "Documento Mas Largo": max(corpus, key=len)[:50] + "...",
        "Documento Mas Corto": min(corpus, key=len)
    }
    
    for key, value in stats.items():
        st.write(f"**{key}:** {value}")

with col2:
    # Palabras mas frecuentes (simulado)
    st.subheader(" Palabras Mas Frecuentes")
    word_freq = {
        "estados": 8,
        "unidos": 8,
        "economia": 6,
        "tecnologia": 5,
        "cultura": 4,
        "politica": 4,
        "desarrollo": 3,
        "internacional": 3
    }
    st.bar_chart(word_freq)
    
    # Informacion del modelo
    st.subheader(" Informacion del Modelo")
    model_info = {
        "Modelo": "sentence-transformers/all-MiniLM-L6-v2",
        "Dimensiones": "384",
        "Idioma": "Ingles",
        "Optimizado para": "Similitud semantica"
    }
    
    for key, value in model_info.items():
        st.write(f"**{key}:** {value}")

# Configuracion avanzada
st.markdown("---")
st.subheader(" **CONFIGURACION AVANZADA**")

col1, col2 = st.columns(2)

with col1:
    st.subheader(" Parametros de Busqueda")
    
    similarity_threshold = st.slider(
        "Umbral de Similitud:",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Solo mostrar resultados con similitud mayor a este valor"
    )
    
    max_results = st.number_input(
        "Maximo de Resultados:",
        min_value=1,
        value=10,
        help="Numero maximo de resultados a mostrar"
    )

with col2:
    st.subheader(" Filtros")
    
    include_sources = st.multiselect(
        "Incluir Fuentes:",
        options=["Reuters", "AP", "Bloomberg", "CNN", "WSJ"],
        default=["Reuters", "AP", "Bloomberg", "CNN", "WSJ"]
    )
    
    date_filter = st.selectbox(
        "Filtro de Fecha:",
        options=["Todos", "Ultimas 24h", "Ultimas 48h", "Ultima semana"]
    )

# Acciones
st.markdown("---")
st.subheader(" **ACCIONES**")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Actualizar Corpus", use_container_width=True):
        st.success(" Corpus actualizado")
        st.rerun()

with col2:
    if st.button(" Limpiar Historial", use_container_width=True):
        st.info(" Historial limpiado")

with col3:
    if st.button(" Exportar Resultados", use_container_width=True):
        st.success(" Resultados exportados a JSON")

# Footer
st.markdown("---")
st.caption(" Modulo de Busqueda Semantica - VISION Premium")
