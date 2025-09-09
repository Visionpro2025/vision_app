# modules/pattern_blocker.py — Gestor de Patrones Vetados
from __future__ import annotations
from pathlib import Path
import re
import json
from typing import List, Dict, Tuple, Optional
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
BLACKLIST_PATH = ROOT / "__CONFIG" / "blacklist_patterns.txt"
CONFIG_PATH = ROOT / "__CONFIG" / "quantum_config.json"

class PatternBlocker:
    def __init__(self):
        self.patterns = self._load_patterns()
        self.config = self._load_config()
        
    def _load_patterns(self) -> List[Tuple[str, str]]:
        """Carga patrones vetados desde archivo."""
        patterns = []
        try:
            if BLACKLIST_PATH.exists():
                for line in BLACKLIST_PATH.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "|" in line:
                            pattern, description = line.split("|", 1)
                            patterns.append((pattern.strip(), description.strip()))
                        else:
                            patterns.append((line, "patrón_generico"))
        except Exception:
            pass
        return patterns
    
    def _load_config(self) -> dict:
        """Carga configuración de bloqueo."""
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {"assembler": {"pattern_blocking": {"enabled": True, "strict_mode": True}}}
    
    def _save_patterns(self):
        """Guarda patrones vetados."""
        try:
            BLACKLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
            content = "# Patrones vetados - Secuencias obvias y repetidos absurdos\n"
            content += "# Formato: regex_pattern|descripción\n\n"
            
            for pattern, description in self.patterns:
                content += f"{pattern}|{description}\n"
            
            BLACKLIST_PATH.write_text(content, encoding="utf-8")
        except Exception:
            pass
    
    def is_blocked(self, numbers: List[int], strict_mode: bool = None) -> Tuple[bool, str]:
        """Verifica si una secuencia está bloqueada."""
        if strict_mode is None:
            strict_mode = self.config["assembler"]["pattern_blocking"]["strict_mode"]
        
        if not numbers:
            return False, ""
        
        # Convertir a string para regex
        number_str = " ".join(map(str, sorted(numbers)))
        
        for pattern, description in self.patterns:
            try:
                if re.search(pattern, number_str):
                    return True, description
            except re.error:
                # Si el regex es inválido, saltar
                continue
        
        # Verificaciones adicionales en modo estricto
        if strict_mode:
            # Secuencias consecutivas
            sorted_nums = sorted(numbers)
            consecutive_count = 1
            for i in range(1, len(sorted_nums)):
                if sorted_nums[i] == sorted_nums[i-1] + 1:
                    consecutive_count += 1
                else:
                    consecutive_count = 1
                if consecutive_count >= 4:
                    return True, "secuencia_consecutiva_larga"
            
            # Números repetidos
            if len(set(numbers)) < len(numbers) * 0.8:
                return True, "demasiados_repetidos"
        
        return False, ""
    
    def add_pattern(self, pattern: str, description: str = ""):
        """Añade un nuevo patrón vetado."""
        if pattern and pattern not in [p[0] for p in self.patterns]:
            self.patterns.append((pattern, description or "patrón_personalizado"))
            self._save_patterns()
    
    def remove_pattern(self, pattern: str):
        """Elimina un patrón vetado."""
        self.patterns = [(p, d) for p, d in self.patterns if p != pattern]
        self._save_patterns()
    
    def get_patterns(self) -> List[Tuple[str, str]]:
        """Obtiene lista de patrones vetados."""
        return self.patterns.copy()
    
    def test_pattern(self, pattern: str, test_numbers: List[int]) -> bool:
        """Prueba un patrón contra números de prueba."""
        try:
            number_str = " ".join(map(str, sorted(test_numbers)))
            return bool(re.search(pattern, number_str))
        except re.error:
            return False

def render_pattern_blocker_ui():
    """Renderiza UI para gestión de patrones vetados."""
    st.subheader("🚫 Gestor de Patrones Vetados")
    
    blocker = PatternBlocker()
    
    # Configuración
    col1, col2 = st.columns(2)
    with col1:
        enabled = st.toggle("Bloqueo Activo", value=blocker.config["assembler"]["pattern_blocking"]["enabled"])
    with col2:
        strict_mode = st.toggle("Modo Estricto", value=blocker.config["assembler"]["pattern_blocking"]["strict_mode"])
    
    # Guardar configuración
    if st.button("💾 Guardar Configuración", use_container_width=True):
        blocker.config["assembler"]["pattern_blocking"].update({
            "enabled": enabled,
            "strict_mode": strict_mode
        })
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(blocker.config, indent=2, ensure_ascii=False), encoding="utf-8")
            st.success("✅ Configuración guardada")
        except Exception as e:
            st.error(f"❌ Error al guardar: {e}")
    
    # Añadir nuevo patrón
    st.markdown("#### Añadir Patrón")
    col1, col2 = st.columns([2, 1])
    with col1:
        new_pattern = st.text_input("Patrón Regex", placeholder="\\d+\\s+\\d+\\s+\\d+")
    with col2:
        new_description = st.text_input("Descripción", placeholder="patrón_descripción")
    
    if st.button("➕ Añadir Patrón", use_container_width=True):
        if new_pattern:
            blocker.add_pattern(new_pattern, new_description)
            st.success("✅ Patrón añadido")
            st.rerun()
    
    # Lista de patrones existentes
    st.markdown("#### Patrones Actuales")
    patterns = blocker.get_patterns()
    
    if not patterns:
        st.info("No hay patrones configurados.")
    else:
        for i, (pattern, description) in enumerate(patterns):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.code(pattern, language="regex")
            with col2:
                st.write(description)
            with col3:
                if st.button("🗑️", key=f"del_{i}"):
                    blocker.remove_pattern(pattern)
                    st.success("✅ Patrón eliminado")
                    st.rerun()
    
    # Probador de patrones
    st.markdown("#### Probador de Patrones")
    test_numbers = st.text_input("Números de prueba (separados por espacios)", placeholder="1 2 3 4 5")
    
    if test_numbers:
        try:
            numbers = [int(x) for x in test_numbers.split()]
            is_blocked, reason = blocker.is_blocked(numbers, strict_mode)
            
            if is_blocked:
                st.error(f"❌ BLOQUEADO: {reason}")
            else:
                st.success("✅ PERMITIDO")
        except ValueError:
            st.warning("⚠️ Formato inválido. Usa números separados por espacios.")
    
    return blocker
