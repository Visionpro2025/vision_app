#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Página de Administración T70
Permite validar y fusionar archivos T70 desde la interfaz de Streamlit
"""

import streamlit as st
import subprocess
import os
import json
from datetime import datetime
from pathlib import Path

# Configuración de la página
st.set_page_config(
    page_title="Admin T70 - VISIÓN Premium",
    page_icon="🔧",
    layout="wide"
)

def run_command_with_output(command: list) -> tuple:
    """Ejecuta comando y retorna (exit_code, output, error)"""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=Path(__file__).parent.parent
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def validate_t70_csv():
    """Ejecuta validación del CSV T70"""
    st.info("🔍 Iniciando validación del archivo T70.csv...")
    
    # Verificar que existe el archivo
    csv_file = "data/T70.csv"
    if not os.path.exists(csv_file):
        st.error(f"❌ Archivo no encontrado: {csv_file}")
        return
    
    # Ejecutar validación
    command = ["python", "scripts/validate_t70.py", csv_file]
    
    with st.spinner("Ejecutando validación..."):
        exit_code, stdout, stderr = run_command_with_output(command)
    
    # Mostrar resultados
    if exit_code == 0:
        st.success("✅ Validación exitosa - No hay errores bloqueantes")
    else:
        st.error("❌ Validación falló - Hay errores bloqueantes")
    
    # Mostrar salida del comando
    if stdout:
        st.subheader("📋 Salida de Validación:")
        st.code(stdout, language="text")
    
    if stderr:
        st.subheader("⚠️ Errores:")
        st.code(stderr, language="text")
    
    # Buscar reporte de validación
    if exit_code == 0:
        st.info("📄 Buscando reporte de validación...")
        data_dir = Path("data")
        validation_reports = list(data_dir.glob("T70_validation_*.txt"))
        
        if validation_reports:
            latest_report = max(validation_reports, key=os.path.getctime)
            st.success(f"📄 Reporte generado: {latest_report.name}")
            
            # Mostrar contenido del reporte
            try:
                with open(latest_report, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                st.subheader("📋 Contenido del Reporte:")
                st.text_area("Reporte de Validación", report_content, height=400)
            except Exception as e:
                st.error(f"Error leyendo reporte: {str(e)}")

def merge_t70_files():
    """Ejecuta fusión de T70.csv con T70_enriched.json"""
    st.info("🔄 Iniciando fusión de archivos T70...")
    
    # Verificar archivos de entrada
    csv_file = "data/T70.csv"
    json_file = "data/T70_enriched.json"
    output_file = "data/T70_enriched_merged.json"
    
    missing_files = []
    if not os.path.exists(csv_file):
        missing_files.append(csv_file)
    if not os.path.exists(json_file):
        missing_files.append(json_file)
    
    if missing_files:
        st.error(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return
    
    # Ejecutar fusión
    command = ["python", "scripts/merge_t70.py", 
               "--csv", csv_file, 
               "--json", json_file, 
               "--out", output_file]
    
    with st.spinner("Ejecutando fusión..."):
        exit_code, stdout, stderr = run_command_with_output(command)
    
    # Mostrar resultados
    if exit_code == 0:
        st.success("✅ Fusión completada exitosamente")
    else:
        st.error("❌ Fusión falló")
    
    # Mostrar salida del comando
    if stdout:
        st.subheader("📋 Salida de Fusión:")
        st.code(stdout, language="text")
    
    if stderr:
        st.subheader("⚠️ Errores:")
        st.code(stderr, language="text")
    
    # Verificar archivo de salida
    if exit_code == 0 and os.path.exists(output_file):
        st.success(f"📁 Archivo de salida creado: {output_file}")
        
        # Mostrar estadísticas del archivo fusionado
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                merged_data = json.load(f)
            
            st.subheader("📊 Estadísticas del Archivo Fusionado:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total de Entradas", len(merged_data))
            
            with col2:
                campbell_stages = [entry.get('campbell_stage') for entry in merged_data if entry.get('campbell_stage')]
                st.metric("Con Etapa Campbell", len(campbell_stages))
            
            with col3:
                freud_entries = [entry for entry in merged_data if entry.get('freud')]
                st.metric("Con Análisis Freud", len(freud_entries))
            
            # Mostrar ejemplo de entrada fusionada
            if merged_data:
                st.subheader("📝 Ejemplo de Entrada Fusionada:")
                example = merged_data[0]
                st.json(example)
        
        except Exception as e:
            st.error(f"Error leyendo archivo fusionado: {str(e)}")
    
    # Buscar reporte de fusión
    st.info("📄 Buscando reporte de fusión...")
    data_dir = Path("data")
    merge_reports = list(data_dir.glob("T70_merge_report_*.txt"))
    
    if merge_reports:
        latest_report = max(merge_reports, key=os.path.getctime)
        st.success(f"📄 Reporte generado: {latest_report.name}")
        
        # Mostrar contenido del reporte
        try:
            with open(latest_report, 'r', encoding='utf-8') as f:
                report_content = f.read()
            st.subheader("📋 Contenido del Reporte de Fusión:")
            st.text_area("Reporte de Fusión", report_content, height=400)
        except Exception as e:
            st.error(f"Error leyendo reporte: {str(e)}")

def show_file_status():
    """Muestra estado de los archivos T70"""
    st.subheader("📁 Estado de Archivos T70/T100")
    
    files_info = [
        ("data/T70.csv", "Archivo CSV original T70"),
        ("data/T100.csv", "Archivo CSV extendido T100"),
        ("data/T100_enriched.json", "JSON con capas narrativas T100"),
        ("data/T100_enriched_merged.json", "Archivo fusionado final T100")
    ]
    
    col1, col2, col3, col4 = st.columns(4)
    
    for i, (file_path, description) in enumerate(files_info):
        col = col1 if i == 0 else col2 if i == 1 else col3 if i == 2 else col4
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            col.success(f"✅ {description}")
            col.metric("Tamaño", f"{file_size:,} bytes")
            col.caption(f"Modificado: {file_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            col.error(f"❌ {description}")
            col.metric("Estado", "No existe")

def main():
    """Función principal de la página"""
    st.title("🔧 Administración T70/T100")
    st.markdown("---")
    
    # Información general
    st.info("""
    **Esta página permite administrar las tablas T70 y T100:**
    - **Validar** archivos CSV (T70 y T100)
    - **Fusionar** CSV con JSON enriquecido
    - **Monitorear** el estado de los archivos
    - **Actualizar** de T70 a T100 automáticamente
    """)
    
    # Estado de archivos
    show_file_status()
    
    st.markdown("---")
    
    # Botones de acción
    st.subheader("🚀 Acciones Disponibles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Validar T70.csv", use_container_width=True, type="primary"):
            validate_t70_csv()
    
    with col2:
        if st.button("🔄 Fusionar T70", use_container_width=True, type="secondary"):
            merge_t70_files()
    
    st.markdown("---")
    
    # Información adicional
    st.subheader("📚 Información Técnica")
    
    with st.expander("🔧 Comandos de Línea de Comandos"):
        st.code("""
# 1) Validación (falla si hay errores)
python scripts/validate_t70.py data/T70.csv

# 2) Fusión (solo si la validación anterior pasó)
python scripts/merge_t70.py --csv data/T70.csv --json data/T70_enriched.json --out data/T70_enriched_merged.json

# 3) Fusión en modo dry-run (solo reporte)
python scripts/merge_t70.py --csv data/T70.csv --json data/T70_enriched.json --out data/T70_enriched_merged.json --dry-run
        """, language="bash")
    
    with st.expander("📋 Estructura de Archivos"):
        st.code("""
data/
  T70.csv                    # CSV original con datos base
  T70_enriched.json          # JSON con capas narrativas
  T70_enriched_merged.json   # Archivo fusionado final
  T70_validation_*.txt       # Reportes de validación
  T70_merge_report_*.txt     # Reportes de fusión

scripts/
  validate_t70.py            # Script de validación
  merge_t70.py               # Script de fusión
        """, language="text")
    
    with st.expander("🎯 Criterios de Aceptación"):
        st.markdown("""
        - ✅ **Validación**: Si hay errores bloqueantes, la fusión no se ejecuta
        - ✅ **Tolerancia**: Funciona con encabezados con/sin acentos
        - ✅ **Backup**: Crea backup automático del archivo de salida
        - ✅ **Reportes**: Genera reportes detallados de cada operación
        - ✅ **Idempotencia**: Se puede ejecutar múltiples veces sin problemas
        """)

if __name__ == "__main__":
    main()
