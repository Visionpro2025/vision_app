# connectors/__init__.py
"""
Conectores para fuentes externas de lotería
"""

from .florida_official import fetch_pick3_latest_html, fetch_pick4_latest_html, merge_p3_p4
from .lotteryusa_backup import fetch_pick3_pick4_backup
from .bolita_cuba import fetch_directorio_cubano, fetch_labolitacubana

__all__ = [
    'fetch_pick3_latest_html',
    'fetch_pick4_latest_html', 
    'merge_p3_p4',
    'fetch_pick3_pick4_backup',
    'fetch_directorio_cubano',
    'fetch_labolitacubana'
]


