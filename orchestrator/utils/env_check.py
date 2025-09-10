# orchestrator/utils/env_check.py
"""
Environment variable validation utility for Dagster Cloud
"""

import os
from typing import Dict, List


def require_env(names: List[str]) -> Dict[str, str]:
    """
    Validates that required environment variables are present.
    
    Args:
        names: List of environment variable names to check
        
    Returns:
        Dict containing only the present environment variables
        
    Raises:
        ValueError: If any required environment variable is missing
        
    Example:
        >>> secrets = require_env(["NEWS_API_KEY", "GNEWS_API_KEY"])
        >>> # Returns {"NEWS_API_KEY": "actual_key", "GNEWS_API_KEY": "actual_key"}
        
        >>> require_env(["MISSING_KEY"])
        # Raises ValueError: Falta variable MISSING_KEY. Defínela en Dagster Cloud → Settings → Secrets.
    """
    present_vars = {}
    missing_vars = []
    
    for name in names:
        value = os.getenv(name)
        if value is not None and value.strip():
            present_vars[name] = value
        else:
            missing_vars.append(name)
    
    if missing_vars:
        missing_str = ", ".join(missing_vars)
        raise ValueError(
            f"Falta variable {missing_str}. "
            f"Defínela en Dagster Cloud → Settings → Secrets."
        )
    
    return present_vars
