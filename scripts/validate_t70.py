#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de validación para T70.csv
Valida estructura, unicidad y contenido del archivo T70
"""

import csv
import sys
import os
import unicodedata
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Configuración de alias de encabezados (tolerante a acentos/alias)
HEADER_ALIASES = {
    'N': ['n', 'num', 'numero', 'número', 'id', 'idx'],
    'EQ': ['eq', 'equivalente', 'equiv', 'valor', 'valor_eq'],
    'titulo': ['titulo', 'título', 'title', 'nombre'],
    'lectura': ['lectura', 'reading', 'descripcion', 'descripción', 'desc'],
    'categoria': ['categoria', 'categoría', 'category', 'grupo', 'caracteristicas']
}

def normalize_text(text: str) -> str:
    """Normaliza texto: quita acentos y convierte a minúsculas"""
    if not text:
        return ""
    # Quitar acentos
    normalized = unicodedata.normalize('NFD', text)
    normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
    # Convertir a minúsculas
    return normalized.lower().strip()

def detect_headers(csv_file: str) -> Tuple[Dict[str, str], List[str]]:
    """Detecta encabezados del CSV y los mapea a campos estándar"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
        header_mapping = {}
        detected_headers = []
        
        for i, header in enumerate(headers):
            normalized_header = normalize_text(header)
            detected_headers.append(f"'{header}' (columna {i+1})")
            
            # Buscar coincidencia en alias
            for standard_field, aliases in HEADER_ALIASES.items():
                if normalized_header in [normalize_text(alias) for alias in aliases]:
                    header_mapping[standard_field] = header
                    break
        
        return header_mapping, detected_headers
        
    except Exception as e:
        print(f"❌ Error leyendo CSV: {str(e)}")
        return {}, []

def validate_t70_data(csv_file: str, header_mapping: Dict[str, str]) -> Tuple[bool, List[str], List[str], List[Dict]]:
    """Valida los datos del CSV T70"""
    errors = []
    warnings = []
    data_rows = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Verificar que existan los campos obligatorios
            required_fields = ['N', 'titulo', 'lectura', 'categoria']
            missing_fields = [field for field in required_fields if field not in header_mapping]
            
            if missing_fields:
                errors.append(f"❌ Campos obligatorios faltantes: {', '.join(missing_fields)}")
                return False, errors, warnings, data_rows
            
            # Leer y validar cada fila
            seen_numbers = set()
            row_number = 1
            
            for row in reader:
                row_number += 1
                row_data = {}
                
                # Mapear campos usando los encabezados detectados
                for standard_field, csv_header in header_mapping.items():
                    if csv_header in row:
                        row_data[standard_field] = row[csv_header]
                    else:
                        row_data[standard_field] = None
                
                # Validaciones obligatorias
                n_value = row_data.get('N')
                if not n_value:
                    errors.append(f"❌ Fila {row_number}: Campo N está vacío")
                    continue
                
                try:
                    n_int = int(n_value)
                    if n_int < 1 or n_int > 100:
                        errors.append(f"❌ Fila {row_number}: N={n_int} está fuera del rango [1..100]")
                        continue
                except ValueError:
                    errors.append(f"❌ Fila {row_number}: N='{n_value}' no es un entero válido")
                    continue
                
                # Verificar unicidad de N
                if n_int in seen_numbers:
                    errors.append(f"❌ Fila {row_number}: N={n_int} está duplicado")
                    continue
                seen_numbers.add(n_int)
                
                # Validar campos obligatorios no vacíos
                titulo = row_data.get('titulo', '').strip()
                if not titulo:
                    errors.append(f"❌ Fila {row_number}: Campo titulo está vacío")
                    continue
                
                lectura = row_data.get('lectura', '').strip()
                if not lectura:
                    errors.append(f"❌ Fila {row_number}: Campo lectura está vacío")
                    continue
                
                categoria = row_data.get('categoria', '').strip()
                if not categoria:
                    errors.append(f"❌ Fila {row_number}: Campo categoria está vacío")
                    continue
                
                # Validar campo EQ si existe
                eq_value = row_data.get('EQ')
                if eq_value:
                    try:
                        eq_int = int(eq_value)
                        row_data['EQ'] = eq_int
                    except ValueError:
                        warnings.append(f"⚠️ Fila {row_number}: EQ='{eq_value}' no es un entero válido")
                        row_data['EQ'] = None
                else:
                    row_data['EQ'] = None
                
                # Añadir fila validada
                row_data['N'] = n_int
                data_rows.append(row_data)
            
            # Verificar números faltantes
            expected_numbers = set(range(1, 101))
            missing_numbers = expected_numbers - seen_numbers
            if missing_numbers:
                warnings.append(f"⚠️ Números faltantes en el rango [1..100]: {sorted(missing_numbers)}")
            
            # Verificar duplicados en EQ
            eq_values = [row['EQ'] for row in data_rows if row['EQ'] is not None]
            eq_duplicates = set([x for x in eq_values if eq_values.count(x) > 1])
            if eq_duplicates:
                warnings.append(f"⚠️ Valores EQ duplicados: {sorted(eq_duplicates)}")
            
            return len(errors) == 0, errors, warnings, data_rows
            
    except Exception as e:
        errors.append(f"❌ Error procesando CSV: {str(e)}")
        return False, errors, warnings, []

def generate_validation_report(csv_file: str, header_mapping: Dict[str, str], 
                             detected_headers: List[str], errors: List[str], 
                             warnings: List[str], data_rows: List[Dict]) -> str:
    """Genera reporte de validación"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"data/T70_validation_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE VALIDACIÓN T70\n")
            f.write("=" * 80 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivo CSV: {csv_file}\n\n")
            
            f.write("DETECCIÓN DE ENCABEZADOS\n")
            f.write("-" * 40 + "\n")
            f.write("Encabezados detectados en CSV:\n")
            for header in detected_headers:
                f.write(f"  {header}\n")
            f.write("\n")
            
            f.write("Mapeo de encabezados:\n")
            for standard_field, csv_header in header_mapping.items():
                f.write(f"  {standard_field} -> '{csv_header}'\n")
            f.write("\n")
            
            f.write("RESULTADOS DE VALIDACIÓN\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total de filas validadas: {len(data_rows)}\n")
            f.write(f"Errores encontrados: {len(errors)}\n")
            f.write(f"Advertencias: {len(warnings)}\n\n")
            
            if errors:
                f.write("ERRORES (BLOQUEANTES):\n")
                f.write("-" * 20 + "\n")
                for error in errors:
                    f.write(f"{error}\n")
                f.write("\n")
            
            if warnings:
                f.write("ADVERTENCIAS:\n")
                f.write("-" * 15 + "\n")
                for warning in warnings:
                    f.write(f"{warning}\n")
                f.write("\n")
            
            if data_rows:
                f.write("ESTADÍSTICAS:\n")
                f.write("-" * 15 + "\n")
                f.write(f"Rango de números N: {min(row['N'] for row in data_rows)} - {max(row['N'] for row in data_rows)}\n")
                
                eq_count = len([row for row in data_rows if row['EQ'] is not None])
                f.write(f"Filas con EQ válido: {eq_count}\n")
                f.write(f"Filas sin EQ: {len(data_rows) - eq_count}\n")
                
                categorias = set(row['categoria'] for row in data_rows)
                f.write(f"Categorías encontradas: {len(categorias)}\n")
                for cat in sorted(categorias):
                    count = len([row for row in data_rows if row['categoria'] == cat])
                    f.write(f"  {cat}: {count} entradas\n")
        
        return report_file
        
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        return ""

def main():
    """Función principal del script de validación"""
    if len(sys.argv) != 2:
        print("❌ Uso: python validate_t70.py <archivo_csv>")
        print("Ejemplo: python validate_t70.py data/T70.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ Archivo no encontrado: {csv_file}")
        sys.exit(1)
    
    print("🔍 INICIANDO VALIDACIÓN T70...")
    print(f"📁 Archivo CSV: {csv_file}")
    print()
    
    # 1. Detectar encabezados
    print("1️⃣ DETECTANDO ENCABEZADOS...")
    header_mapping, detected_headers = detect_headers(csv_file)
    
    if not header_mapping:
        print("❌ No se pudieron detectar encabezados válidos")
        sys.exit(1)
    
    print("✅ Encabezados detectados:")
    for standard_field, csv_header in header_mapping.items():
        print(f"  {standard_field} -> '{csv_header}'")
    print()
    
    # 2. Validar datos
    print("2️⃣ VALIDANDO DATOS...")
    is_valid, errors, warnings, data_rows = validate_t70_data(csv_file, header_mapping)
    
    # 3. Generar reporte
    print("3️⃣ GENERANDO REPORTE...")
    report_file = generate_validation_report(csv_file, header_mapping, detected_headers, 
                                          errors, warnings, data_rows)
    
    if report_file:
        print(f"✅ Reporte generado: {report_file}")
    
    # 4. Mostrar resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    print(f"📊 Total de filas validadas: {len(data_rows)}")
    print(f"❌ Errores encontrados: {len(errors)}")
    print(f"⚠️ Advertencias: {len(warnings)}")
    
    if errors:
        print("\n❌ VALIDACIÓN FALLÓ - Hay errores bloqueantes:")
        for error in errors[:5]:  # Mostrar solo los primeros 5 errores
            print(f"  {error}")
        if len(errors) > 5:
            print(f"  ... y {len(errors) - 5} errores más")
        print(f"\n📄 Ver reporte completo: {report_file}")
        sys.exit(1)
    else:
        print("\n✅ VALIDACIÓN EXITOSA - No hay errores bloqueantes")
        if warnings:
            print("⚠️ Hay advertencias (no bloquean la fusión)")
        print(f"📄 Reporte detallado: {report_file}")
        sys.exit(0)

if __name__ == "__main__":
    main()
