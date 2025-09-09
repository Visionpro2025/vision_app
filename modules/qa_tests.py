from __future__ import annotations

class QAError(Exception):
    pass

def assert_min_news(n: int, min_required: int = 50):
    if n < min_required:
        raise QAError(f"Min noticias {min_required}, hay {n}")

def assert_caps(arquetipos: int, mensajes: int, estados: int):
    if arquetipos < 2: raise QAError("Arquetipos insuficientes")
    if mensajes < 1: raise QAError("Mensajes subliminales insuficientes")
    if estados < 1: raise QAError("Estados cuánticos insuficientes")
