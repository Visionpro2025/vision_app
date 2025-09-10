# ============================================
# 🚀 MÓDULO: INGESTA PROFESIONAL DE NOTICIAS
# Ingesta determinista por RSS con deduplicación y normalización
# Corrige los métodos faltantes en ProfessionalNewsIngestion
# ============================================

from __future__ import annotations
import time, hashlib, re
from typing import List, Dict, Any, Optional, Tuple
import feedparser

# Utilidades simples y deterministas

def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

def _norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def _clean_url(u: str) -> str:
    return (u or "").split("#")[0].strip()

def _dedup_urls(urls: List[str]) -> List[str]:
    seen = set(); out = []
    for u in urls:
        cu = _clean_url(u)
        if not cu or cu in seen: 
            continue
        seen.add(cu); out.append(cu)
    return out

def _extract_entries_from_feed(feed_url: str, max_items: int) -> List[Dict[str, Any]]:
    d = feedparser.parse(feed_url)
    entries = []
    for e in d.entries[:max_items]:
        entries.append({
            "title": _norm_space(getattr(e, "title", "")),
            "url": _clean_url(getattr(e, "link", "")),
            "published": _norm_space(getattr(e, "published", "")),
            "summary": _norm_space(getattr(e, "summary", "")),
            "feed": feed_url
        })
    return entries

class ProfessionalNewsIngestion:
    """
    Ingesta determinista por RSS y retorno de URLs normalizadas.
    - collect_news(): trae 'principales' según feeds configurados.
    - search_emotional_news(): restringe por términos sociales/emocionales.
    NOTA: No inventa nada. Si no hay feeds, devuelve lista vacía con motivo.
    """

    def __init__(self, feeds: Optional[List[str]] = None, max_per_feed: int = 20):
        self.feeds = feeds or []
        self.max_per_feed = max(1, int(max_per_feed))

    # === Requerido por tu pipeline ===
    def collect_news(self) -> Dict[str, Any]:
        """
        Devuelve:
        {
          'urls': [...],
          'count': int,
          'sources': [{'feed':..., 'items':int}, ...],
          'log': [...]
        }
        """
        log: List[str] = []
        if not self.feeds:
            return {"urls": [], "count": 0, "sources": [], "log": ["No feeds configured."]}

        urls: List[str] = []
        sources_meta: List[Dict[str, Any]] = []
        for f in self.feeds:
            try:
                entries = _extract_entries_from_feed(f, self.max_per_feed)
                k = 0
                for ent in entries:
                    if ent["url"]:
                        urls.append(ent["url"]); k += 1
                sources_meta.append({"feed": f, "items": k})
            except Exception as e:
                log.append(f"Error leyendo feed {f}: {e.__class__.__name__}")

        urls = _dedup_urls(urls)
        return {"urls": urls, "count": len(urls), "sources": sources_meta, "log": log}

    # === Requerido por tu pipeline ===
    def search_emotional_news(self, guidance_terms: List[str]) -> Dict[str, Any]:
        """
        Filtrado básico por términos sociales/emocionales + guía.
        Como esta clase solo usa RSS (título/summary), el filtrado es heurístico.
        Devuelve misma estructura que collect_news() pero ya filtrada.
        """
        base = self.collect_news()
        if base["count"] == 0:
            base["log"].append("Sin base para filtrar (0 URLs).")
            return {"urls": [], "count": 0, "sources": base["sources"], "log": base["log"]}

        guide = set([t.strip().lower() for t in guidance_terms if isinstance(t, str)]) or set()
        # Términos sociales default (puedes ampliarlos)
        social_terms = guide | {
            "community","comunidad","familia","family","neighborhood","barrio","empleo",
            "salud","mental","escuela","educación","vivienda","alquiler","homeless",
            "protesta","manifestación","migración","ayuda","solidaridad","crimen","violencia",
            "inflación","costo de vida","eviction","duelo","tragedia","celebración","voluntariado"
        }

        # Releer metadatos mínimos (título/summary) de cada feed y filtrar
        urls_keep: List[str] = []
        for s in self.feeds:
            try:
                entries = _extract_entries_from_feed(s, self.max_per_feed)
                for ent in entries:
                    blob = f"{ent['title']} {ent['summary']}".lower()
                    if any(t in blob for t in social_terms):
                        if ent["url"]:
                            urls_keep.append(ent["url"])
            except Exception:
                continue

        urls_keep = _dedup_urls(urls_keep)
        return {"urls": urls_keep, "count": len(urls_keep), "sources": base["sources"], "log": base["log"]}





