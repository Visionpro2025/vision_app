#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step6Artifacts - Paso para guardar artefactos del análisis sefirotico
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app_vision.engine.contracts import Step, StepContext, StepError, StepResult
from app_vision.engine.fsm import register_step
import json

@register_step("step6_artifacts")
class Step6Artifacts(Step):
    name = "step6_artifacts"
    description = "Guarda artefactos del análisis sefirotico (poema y temas)"
    version = "1.0"
    
    def validate_inputs(self, data):
        """Valida que existan poem y topics en los datos de entrada."""
        poem = data.get("poem")
        topics = data.get("topics")
        
        if not poem:
            return False
        if not topics:
            return False
        
        return True
    
    def run(self, ctx: StepContext, data) -> StepResult:
        """Guarda el poema y los temas en archivos de artefactos."""
        
        # Leer payload del paso anterior desde el state store no está expuesto aquí.
        # En este bootstrap, el Engine no pasa payloads entre pasos automáticamente.
        # Alternativa simple: repetir la generación o inyectar desde 'inputs'.
        poem = data.get("poem")
        topics = data.get("topics")
        
        if not poem or not topics:
            raise StepError("InputError", "Faltan 'poem' y 'topics' para guardar.")

        # Crear directorio de artefactos
        art_dir = os.path.join(ctx.state_dir, "artifacts", ctx.run_id)
        os.makedirs(art_dir, exist_ok=True)
        
        # Guardar poema
        poem_file = os.path.join(art_dir, "poem.txt")
        with open(poem_file, "w", encoding="utf-8") as f:
            f.write(poem)
        
        # Guardar temas
        topics_file = os.path.join(art_dir, "topics.json")
        with open(topics_file, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        
        return StepResult(
            success=True,
            data={
                "saved_to": art_dir,
                "poem_file": poem_file,
                "topics_file": topics_file,
                "artifacts_created": 2
            },
            metadata={
                "step_name": self.name,
                "version": self.version,
                "artifacts_dir": art_dir
            }
        )
