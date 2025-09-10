#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado del Protocol Engine PRO
"""

import sqlite3
import json
import os

def verificar_estado():
    """Verifica el estado de la base de datos SQLite."""
    
    db_path = ".state/state.sqlite"
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🎯 ESTADO DEL PROTOCOL ENGINE PRO")
    print("="*50)
    
    # Verificar runs
    print("\n📊 RUNS REGISTRADOS:")
    cursor.execute("SELECT run_id, plan_path, cfg_hash, created_at FROM runs")
    runs = cursor.fetchall()
    for run_id, plan_path, cfg_hash, created_at in runs:
        print(f"   • {run_id}")
        print(f"     Plan: {plan_path}")
        print(f"     Hash: {cfg_hash[:16]}...")
        print(f"     Creado: {created_at}")
    
    # Verificar steps
    print(f"\n🔄 PASOS EJECUTADOS:")
    cursor.execute("SELECT run_id, step_name, status, error_kind, error_detail FROM steps ORDER BY run_id, step_name")
    steps = cursor.fetchall()
    
    current_run = None
    for run_id, step_name, status, error_kind, error_detail in steps:
        if run_id != current_run:
            print(f"\n   📋 Run: {run_id}")
            current_run = run_id
        
        if status == "OK":
            print(f"      ✅ {step_name}: EXITOSO")
        else:
            print(f"      ❌ {step_name}: ERROR - {error_kind}: {error_detail}")
    
    # Verificar artefactos
    print(f"\n📁 ARTEFACTOS GENERADOS:")
    artifacts_dir = ".state/artifacts"
    if os.path.exists(artifacts_dir):
        for run_dir in os.listdir(artifacts_dir):
            run_path = os.path.join(artifacts_dir, run_dir)
            if os.path.isdir(run_path):
                print(f"   📂 {run_dir}/")
                for file in os.listdir(run_path):
                    file_path = os.path.join(run_path, file)
                    if os.path.isfile(file_path):
                        size = os.path.getsize(file_path)
                        print(f"      📄 {file} ({size} bytes)")
    
    conn.close()

if __name__ == "__main__":
    verificar_estado()






