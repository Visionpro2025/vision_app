#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step2LotteryConfig - Configuración de lotería
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

@register_step("step2_lottery_config")
class Step2LotteryConfig(Step):
    name = "step2_lottery_config"
    description = "Configuración de parámetros de lotería"
    version = "1.0"
    
    def validate_inputs(self, data):
        """Valida que existan los parámetros de lotería."""
        lottery_type = data.get("lottery_type")
        number_range = data.get("number_range")
        
        if not lottery_type:
            return False
        if not number_range:
            return False
        
        return True
    
    def run(self, ctx: StepContext, data) -> StepResult:
        """Configura los parámetros de la lotería."""
        
        lottery_type = data.get("lottery_type", "Florida Pick 3")
        number_range = data.get("number_range", "00-99")
        frequency = data.get("frequency", "twice_daily")
        
        # Configuración de lotería
        lottery_config = {
            "type": lottery_type,
            "range": number_range,
            "frequency": frequency,
            "min_number": int(number_range.split("-")[0]),
            "max_number": int(number_range.split("-")[1]),
            "total_numbers": int(number_range.split("-")[1]) - int(number_range.split("-")[0]) + 1
        }
        
        # Guardar configuración
        config_file = os.path.join(ctx.state_dir, f"lottery_config_{ctx.run_id}.json")
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(lottery_config, f, indent=2, ensure_ascii=False)
        
        return StepResult(
            success=True,
            data=lottery_config,
            metadata={
                "step_name": self.name,
                "version": self.version,
                "config_file": config_file
            }
        )
