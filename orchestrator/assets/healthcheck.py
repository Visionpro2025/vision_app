# orchestrator/assets/healthcheck.py
"""
Health check asset for Dagster Cloud monitoring
"""

from dagster import asset
import sys
import dagster
from datetime import datetime
import time
from typing import Dict, Any


@asset(
    name="healthcheck",
    description="Health check asset that provides system information without external dependencies"
)
def healthcheck() -> Dict[str, Any]:
    """
    Performs a health check and returns system information.
    
    Returns:
        Dict containing system information and health status
    """
    try:
        # Get Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        # Get Dagster version
        dagster_version = dagster.__version__
        
        # Get current timezone (default system timezone)
        current_time = datetime.now()
        timezone_info = str(current_time.astimezone().tzinfo)
        
        # Get current timestamp
        timestamp = current_time.isoformat()
        
        health_data = {
            "status": "healthy",
            "timestamp": timestamp,
            "python_version": python_version,
            "dagster_version": dagster_version,
            "timezone": timezone_info,
            "system_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "health_check_passed": True
        }
        
        return health_data
        
    except Exception as e:
        # Return error information if health check fails
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "health_check_passed": False
        }
