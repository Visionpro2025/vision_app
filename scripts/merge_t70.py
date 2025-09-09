#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de fusión para T70
Combina T70.csv validado con T70_enriched.json para crear T70_enriched_merged.json
"""

import csv
import json
import sys
import os
import argparse
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Optional

def load_csv_data(csv_file: str) -> Tuple[Dict[str, str], List[Dict]]:
    """Carga datos del CSV T70 validado"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Detectar encabezados (similar a validate_t70.py)
            header_mapping = {}
            for csv_header in reader.fieldnames:
                if csv_header in ['n', 'N', 'eq', 'EQ', 'titulo', 'lectura', 'categoria']:
                    # Mapear a campos estándar
                    if csv_header.lower() == 'n':
                        header_mapping['N'] = csv_header
                    elif csv_header.lower() == 'eq':
                        header_mapping['EQ'] = csv_header
                    else:
                        header_mapping[csv_header] = csv_header
            
            # Leer filas
            data_rows = []
            for row in reader:
                row_data = {}
                for standard_field, csv_header in header_mapping.items():
                    if csv_header in row:
                        value = row[csv_header].strip()
                        if standard_field in ['N', 'EQ'] and value:
                            try:
                                row_data[standard_field] = int(value)
                            except ValueError:
                                row_data[standard_field] = None
                        else:
                            row_data[standard_field] = value
                    else:
                        row_data[standard_field] = None
                
                data_rows.append(row_data)
            
            return header_mapping, data_rows
            
    except Exception as e:
        print(f"❌ Error cargando CSV: {str(e)}")
        return {}, []

def load_json_data(json_file: str) -> List[Dict]:
    """Carga datos del JSON enriquecido T70"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Aceptar diferentes estructuras de JSON
        if isinstance(data, dict):
            # Buscar listas en diferentes claves
            for key in ['items', 'data', 'records', 't70', 'list']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # Si no hay lista, asumir que el dict es la lista
            return [data]
        elif isinstance(data, list):
            return data
        else:
            print(f"❌ Formato JSON no reconocido: {type(data)}")
            return []
            
    except Exception as e:
        print(f"❌ Error cargando JSON: {str(e)}")
        return []

def find_matching_json_entry(csv_row: Dict, json_data: List[Dict]) -> Optional[Dict]:
    """Encuentra entrada JSON que coincida con fila CSV"""
    csv_n = csv_row.get('N')
    csv_eq = csv_row.get('EQ')
    
    # Buscar por N primero
    if csv_n is not None:
        for json_entry in json_data:
            if json_entry.get('N') == csv_n:
                return json_entry
    
    # Buscar por EQ como respaldo
    if csv_eq is not None:
        for json_entry in json_data:
            if json_entry.get('EQ') == csv_eq:
                return json_entry
    
    return None

def merge_t70_data(csv_data: List[Dict], json_data: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Fusiona datos CSV con JSON enriquecido"""
    merged_data = []
    stats = {
        'emparejados': 0,
        'solo_csv': 0,
        'solo_json': 0,
        'csv_processed': set(),
        'json_processed': set()
    }
    
    # Procesar cada fila CSV
    for csv_row in csv_data:
        csv_n = csv_row.get('N')
        if csv_n is None:
            continue
            
        json_entry = find_matching_json_entry(csv_row, json_data)
        
        if json_entry:
            # Fusión exitosa
            merged_row = {
                'N': csv_n,
                'EQ': csv_row.get('EQ'),
                'titulo': csv_row.get('titulo', ''),
                'lectura': csv_row.get('lectura', ''),
                'categoria': csv_row.get('categoria', ''),
                'campbell_stage': json_entry.get('campbell_stage'),
                'vonfranz_symbol': json_entry.get('vonfranz_symbol'),
                'freud': json_entry.get('freud')
            }
            
            # Asegurar que N y EQ sean numéricos
            if merged_row['EQ'] is not None:
                try:
                    merged_row['EQ'] = int(merged_row['EQ'])
                except (ValueError, TypeError):
                    merged_row['EQ'] = None
            
            merged_data.append(merged_row)
            stats['emparejados'] += 1
            stats['csv_processed'].add(csv_n)
            
            # Marcar entrada JSON como procesada
            json_n = json_entry.get('N')
            if json_n is not None:
                stats['json_processed'].add(json_n)
        else:
            # Solo CSV - crear entrada nueva con capas en None
            merged_row = {
                'N': csv_n,
                'EQ': csv_row.get('EQ'),
                'titulo': csv_row.get('titulo', ''),
                'lectura': csv_row.get('lectura', ''),
                'categoria': csv_row.get('categoria', ''),
                'campbell_stage': None,
                'vonfranz_symbol': None,
                'freud': None
            }
            
            merged_data.append(merged_row)
            stats['solo_csv'] += 1
            stats['csv_processed'].add(csv_n)
    
    # Identificar entradas JSON sin correspondencia en CSV
    for json_entry in json_data:
        json_n = json_entry.get('N')
        if json_n is not None and json_n not in stats['json_processed']:
            stats['solo_json'] += 1
    
    return merged_data, stats

def generate_merge_report(csv_file: str, json_file: str, output_file: str,
                         stats: Dict, csv_data: List[Dict], json_data: List[Dict]) -> str:
    """Genera reporte de fusión"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"data/T70_merge_report_{timestamp}.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("REPORTE DE FUSIÓN T70\n")
            f.write("=" * 80 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivo CSV: {csv_file}\n")
            f.write(f"Archivo JSON: {json_file}\n")
            f.write(f"Archivo de salida: {output_file}\n\n")
            
            f.write("ESTADÍSTICAS DE FUSIÓN\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total de filas CSV: {len(csv_data)}\n")
            f.write(f"Total de entradas JSON: {len(json_data)}\n")
            f.write(f"Total de filas fusionadas: {stats['emparejados'] + stats['solo_csv']}\n\n")
            
            f.write("RESULTADOS DE EMPAREJAMIENTO\n")
            f.write("-" * 40 + "\n")
            f.write(f"✅ Emparejados (CSV + JSON): {stats['emparejados']}\n")
            f.write(f"➕ Solo CSV (añadidos): {stats['solo_csv']}\n")
            f.write(f"📄 Solo JSON (sin CSV): {stats['solo_json']}\n\n")
            
            if stats['emparejados'] > 0:
                f.write("ENTRADAS EMPAREJADAS:\n")
                f.write("-" * 25 + "\n")
                csv_processed = sorted(stats['csv_processed'])
                for n in csv_processed[:20]:  # Mostrar solo las primeras 20
                    f.write(f"  N={n}\n")
                if len(csv_processed) > 20:
                    f.write(f"  ... y {len(csv_processed) - 20} más\n")
                f.write("\n")
            
            if stats['solo_csv'] > 0:
                f.write("ENTRADAS SOLO CSV (NUEVAS):\n")
                f.write("-" * 30 + "\n")
                solo_csv_ns = [row['N'] for row in csv_data if row['N'] not in stats['json_processed']]
                for n in sorted(solo_csv_ns):
                    f.write(f"  N={n}\n")
                f.write("\n")
            
            if stats['solo_json'] > 0:
                f.write("ENTRADAS SOLO JSON (SIN CSV):\n")
                f.write("-" * 35 + "\n")
                solo_json_ns = [entry['N'] for entry in json_data 
                               if entry.get('N') is not None and entry['N'] not in stats['csv_processed']]
                for n in sorted(solo_json_ns):
                    f.write(f"  N={n}\n")
                f.write("\n")
            
            f.write("ESTRUCTURA FINAL\n")
            f.write("-" * 20 + "\n")
            f.write("Cada entrada fusionada contiene:\n")
            f.write("  - N, EQ, titulo, lectura, categoria (del CSV)\n")
            f.write("  - campbell_stage, vonfranz_symbol, freud (del JSON)\n")
            f.write("  - Las entradas solo CSV tienen capas en None\n")
        
        return report_file
        
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        return ""

def backup_existing_file(output_file: str) -> str:
    """Crea backup del archivo de salida si existe"""
    if os.path.exists(output_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{output_file}.bak_{timestamp}"
        try:
            shutil.copy2(output_file, backup_file)
            print(f"✅ Backup creado: {backup_file}")
            return backup_file
        except Exception as e:
            print(f"⚠️ No se pudo crear backup: {str(e)}")
    return ""

def main():
    """Función principal del script de fusión"""
    parser = argparse.ArgumentParser(description='Fusiona T70.csv con T70_enriched.json')
    parser.add_argument('--csv', required=True, help='Archivo CSV de entrada')
    parser.add_argument('--json', required=True, help='Archivo JSON enriquecido')
    parser.add_argument('--out', required=True, help='Archivo JSON de salida')
    parser.add_argument('--dry-run', action='store_true', help='Solo mostrar reporte, no escribir archivo')
    
    args = parser.parse_args()
    
    # Verificar archivos de entrada
    if not os.path.exists(args.csv):
        print(f"❌ Archivo CSV no encontrado: {args.csv}")
        sys.exit(1)
    
    if not os.path.exists(args.json):
        print(f"❌ Archivo JSON no encontrado: {args.json}")
        sys.exit(1)
    
    print("🔄 INICIANDO FUSIÓN T70...")
    print(f"📁 CSV: {args.csv}")
    print(f"📁 JSON: {args.json}")
    print(f"📁 Salida: {args.out}")
    print()
    
    # 1. Cargar datos CSV
    print("1️⃣ CARGANDO DATOS CSV...")
    header_mapping, csv_data = load_csv_data(args.csv)
    
    if not csv_data:
        print("❌ No se pudieron cargar datos CSV")
        sys.exit(1)
    
    print(f"✅ CSV cargado: {len(csv_data)} filas")
    print()
    
    # 2. Cargar datos JSON
    print("2️⃣ CARGANDO DATOS JSON...")
    json_data = load_json_data(args.json)
    
    if not json_data:
        print("❌ No se pudieron cargar datos JSON")
        sys.exit(1)
    
    print(f"✅ JSON cargado: {len(json_data)} entradas")
    print()
    
    # 3. Fusionar datos
    print("3️⃣ FUSIONANDO DATOS...")
    merged_data, stats = merge_t70_data(csv_data, json_data)
    
    print(f"✅ Fusión completada:")
    print(f"  📊 Emparejados: {stats['emparejados']}")
    print(f"  ➕ Solo CSV: {stats['solo_csv']}")
    print(f"  📄 Solo JSON: {stats['solo_json']}")
    print()
    
    # 4. Generar reporte
    print("4️⃣ GENERANDO REPORTE...")
    report_file = generate_merge_report(args.csv, args.json, args.out, 
                                      stats, csv_data, json_data)
    
    if report_file:
        print(f"✅ Reporte generado: {report_file}")
    
    # 5. Escribir archivo de salida (si no es dry-run)
    if not args.dry_run:
        print("5️⃣ ESCRIBIENDO ARCHIVO DE SALIDA...")
        
        # Crear backup si existe
        backup_file = backup_existing_file(args.out)
        
        try:
            with open(args.out, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Archivo de salida escrito: {args.out}")
            
        except Exception as e:
            print(f"❌ Error escribiendo archivo: {str(e)}")
            sys.exit(1)
    else:
        print("5️⃣ DRY-RUN: No se escribió archivo de salida")
    
    # 6. Mostrar resumen final
    print("\n" + "=" * 60)
    print("FUSIÓN T70 COMPLETADA")
    print("=" * 60)
    print(f"📊 Total de entradas fusionadas: {len(merged_data)}")
    print(f"✅ Emparejados: {stats['emparejados']}")
    print(f"➕ Solo CSV: {stats['solo_csv']}")
    print(f"📄 Solo JSON: {stats['solo_json']}")
    
    if not args.dry_run:
        print(f"\n📁 Archivo de salida: {os.path.abspath(args.out)}")
        if backup_file:
            print(f"📁 Backup: {os.path.abspath(backup_file)}")
    
    print(f"📄 Reporte: {os.path.abspath(report_file)}")
    print("\n🎉 ¡Fusión completada exitosamente!")

if __name__ == "__main__":
    main()
