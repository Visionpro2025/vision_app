# ============================================
# 📌 FILTRO DE CONTENIDO ALINEADO CON MENSAJE
# Sin lotería, solo social/emocional guiado por mensaje del sorteo anterior
# ============================================

from __future__ import annotations
import os, re, json, urllib.parse
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

UA = "App.Vision-ContentFilter/1.0"
TIMEOUT = 15

@dataclass
class Article:
    url: str
    final_url: str
    title: str
    text: str
    score_social: float
    score_geo: float
    score_guidance: float
    banned_hit: bool

def _fetch_text(url: str) -> Tuple[str, str, str]:
    """Extrae título y texto de una URL"""
    with requests.Session() as s:
        s.headers.update({"User-Agent": UA})
        r = s.get(url, timeout=TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        final_url = r.url
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.get_text(strip=True) if soup.title else ""
        # Contenido simple: párrafos
        text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))
        return final_url, title, re.sub(r"\s+", " ", text).strip()

def _any_hit(text: str, terms: List[str]) -> bool:
    """Verifica si algún término prohibido está presente"""
    t = text.lower()
    return any((" "+w+" " in " "+t+" ") for w in terms)

def _score_hits(text: str, terms: List[str]) -> int:
    """Cuenta ocurrencias de términos en texto"""
    t = text.lower()
    return sum(t.count(w) for w in terms)

def _load_rules(path: str) -> Dict[str, Any]:
    """Carga reglas de contenido desde YAML"""
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def classify_articles(urls: List[str], rules_path: str, guidance: Dict[str, List[str]], top_k: int = 24) -> Dict[str, Any]:
    """
    Clasifica artículos por contenido social/emocional alineado con mensaje.
    
    Args:
        urls: Lista de URLs ya validadas (fechas, dominios, duplicados)
        rules_path: Ruta al archivo de reglas YAML
        guidance: Guía del mensaje del sorteo anterior
        top_k: Número máximo de artículos a retornar
    
    Returns:
        Dict con artículos seleccionados, métricas y guía usada
    """
    rules = _load_rules(rules_path)
    banned = [x.lower() for x in rules.get("banned_terms", [])]
    social = [x.lower() for x in rules.get("social_emotion_terms", [])]
    geos = [x.lower() for x in rules.get("geo_prefer", [])]

    # Guía del mensaje del sorteo anterior (SubliminalGuarded)
    guide_terms = []
    for k in ("topics", "keywords_used", "families_used"):
        guide_terms.extend([x.lower() for x in guidance.get(k, []) if isinstance(x, str)])

    arts: List[Article] = []
    
    for u in urls:
        try:
            final_url, title, text = _fetch_text(u)
            full = (title + " " + text).lower()

            # Verificar términos prohibidos (lotería, etc.)
            banned_hit = _any_hit(full, banned)
            if banned_hit:
                # Descartado por lotería/quiniela/etc.
                continue

            # Calcular scores
            sc_social = _score_hits(full, social)
            sc_geo = _score_hits(full, geos)
            sc_guide = _score_hits(full, guide_terms)

            # Exigir que sea realmente "social/emocional"
            if sc_social <= 0 and sc_geo <= 0:
                # Si no hay ni social ni geo, solo pasa si guidance lo apunta fuerte
                if sc_guide < 2:
                    continue

            arts.append(Article(
                url=u, final_url=final_url, title=title, text=text,
                score_social=float(sc_social), score_geo=float(sc_geo),
                score_guidance=float(sc_guide), banned_hit=False
            ))
        except Exception:
            continue

    # Ranking: social fuerte + geocontexto + alineación con el mensaje
    arts.sort(key=lambda a: (a.score_social*2.0 + a.score_geo*1.0 + a.score_guidance*1.5), reverse=True)
    top = arts[:top_k]

    # Diversidad por tema simple (heurística por palabras)
    buckets = {
        "familia": [], "comunidad": [], "vivienda": [], "empleo": [], 
        "salud": [], "educacion": [], "seguridad": [], "otros": []
    }
    
    def _bucket(a: Article) -> str:
        """Asigna artículo a bucket temático"""
        t = (a.title + " " + a.text).lower()
        if any(k in t for k in ["familia","family","hogar","parent","child"]): 
            return "familia"
        if any(k in t for k in ["comunidad","community","barrio","neighborhood","vecino"]): 
            return "comunidad"
        if any(k in t for k in ["vivienda","alquiler","eviction","homeless","alojamiento","renta","housing"]): 
            return "vivienda"
        if any(k in t for k in ["empleo","trabajo","salario","strike","union","desempleo","job","worker"]): 
            return "empleo"
        if any(k in t for k in ["salud mental","salud","hospital","depresión","terapia","health","mental"]): 
            return "salud"
        if any(k in t for k in ["escuela","educación","colegio","students","teachers","school","education"]): 
            return "educacion"
        if any(k in t for k in ["crimen","violencia","tiroteo","delito","seguridad","crime","violence","security"]): 
            return "seguridad"
        return "otros"

    out = []
    for a in top:
        out.append({
            "url": a.url,
            "final_url": a.final_url,
            "title": a.title,
            "score": a.score_social*2.0 + a.score_geo + a.score_guidance*1.5,
            "scores": {
                "social": a.score_social, 
                "geo": a.score_geo, 
                "guidance": a.score_guidance
            },
            "bucket": _bucket(a)
        })

    # Métricas finales
    metrics = {
        "input_urls": len(urls),
        "kept": len(out),
        "buckets": {b: sum(1 for x in out if x["bucket"] == b) for b in buckets.keys()},
        "avg_social_score": sum(a.score_social for a in top) / len(top) if top else 0,
        "avg_guidance_score": sum(a.score_guidance for a in top) / len(top) if top else 0
    }
    
    return {
        "selected": out, 
        "metrics": metrics, 
        "guidance_used": {"guide_terms": guide_terms}
    }



