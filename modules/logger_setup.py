# modules/logger_setup.py
from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime

_LOGGER_CREATED = False

def get_logger(name: str = "vision") -> logging.Logger:
    """
    Configura un logger de aplicación que escribe en __RUNS/logs/app.log
    y retorna un logger con el nombre indicado.
    """
    global _LOGGER_CREATED
    logger = logging.getLogger(name)

    if _LOGGER_CREATED:
        return logger

    root = Path(__file__).resolve().parent.parent
    logs_dir = root / "__RUNS" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "app.log"

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(fmt)

    sh = logging.StreamHandler()
    sh.setLevel(logging.WARNING)
    sh.setFormatter(fmt)

    base = logging.getLogger()
    base.setLevel(logging.INFO)
    base.addHandler(fh)
    base.addHandler(sh)

    _LOGGER_CREATED = True
    logger.info("Logger inicializado")
    return logger
