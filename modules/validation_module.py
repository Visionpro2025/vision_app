# modules/validation_module.py
from typing import List
from modules.schemas import NewsItem, T70Result, GematriaResult, SubliminalResult, QuantumResult
from config.settings import THRESH

class PipelineValidationError(Exception):
    pass

def assert_news_minimum(news: List[NewsItem]):
    if len(news) < THRESH.min_news:
        raise PipelineValidationError(f"Se requieren {THRESH.min_news} noticias, hay {len(news)}.")

def assert_t70(t70: T70Result):
    if len([c for c in t70.categories if t70.categories[c] > 0]) < THRESH.min_categories:
        raise PipelineValidationError("T70: categorías insuficientes.")

def assert_gematria(g: GematriaResult):
    if len(g.archetypes) < THRESH.min_archetypes:
        raise PipelineValidationError("Gematría: arquetipos insuficientes.")

def assert_subliminal(s: SubliminalResult):
    if len(s.messages) < THRESH.min_subliminal_msgs:
        raise PipelineValidationError("Subliminal: no se detectaron mensajes mínimos.")

def assert_quantum(q: QuantumResult):
    if len(q.states) < THRESH.min_quantum_states:
        raise PipelineValidationError("Cuántico: sin estados mínimos.")








