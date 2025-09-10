from __future__ import annotations
from typing import Dict, Any, List, Tuple
import re, unicodedata, math
from collections import defaultdict
from .table100_universal import build_table100

_SP_STOP = set("""
a al algo algún algunos ante antes aquel aquella aquellas aquello aquellos aqui
arriba abajo bien cada casi como con contra cosa cual cuales cuando cuanto de del
desde donde dos el ella ellas ellos en entre era eran es esa esas ese eso esos esta
estas este esto estos fue fueron ha haber habia habido hasta la las le les lo los
mas más me mi mia mias mientras muy ni no nos nuestra nuestras nuestro nuestros
o os otra otro para pero poca poco por porque pues que quien quienes se sea segun según
ser si sí sin sobre solo sólo son su sus te tener tuve tuya tuyas tuyos un una uno unos
y ya
""".split())

_EN_STOP = set("""
a an and are as at be by for from has have if in into is it its of on or that the their
there they this to was were will with your you we our us not no yes
""".split())

def _strip_accents(s: str)->str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c)!='Mn')

def _tokenize(text: str)->List[str]:
    t = _strip_accents(text.lower())
    t = re.sub(r"[^a-z0-9áéíóúñü\s]", " ", t)
    toks = [w for w in t.split() if w and w not in _SP_STOP and w not in _EN_STOP and len(w)>2]
    return toks

def _score_article(text: str, table: Dict[int, Dict[str, Any]], guide_terms: List[str])->Tuple[Dict[int,float], Dict[int, List[str]]]:
    toks = _tokenize(text)
    if not toks:
        return {}, {}
    tokset = set(toks)
    guide = set(_tokenize(" ".join(guide_terms or [])))
    scores: Dict[int, float] = defaultdict(float)
    hits: Dict[int, List[str]] = defaultdict(list)
    # índice rápido por keyword
    for num, meta in table.items():
        kws = set(meta.get("kw", []))
        if not kws: continue
        # coincidencias exactas por token
        inter = tokset & kws
        if inter:
            base = len(inter)
            # ponderación: coincidencias + guía (si la hay) + longitud del texto (suavizado)
            boost_guide = 1.0 + 0.5*len(guide & kws)
            scores[num] += base * boost_guide / (1.0 + math.log(1+len(toks)))
            hits[num].extend(sorted(list(inter))[:6])
    # regla 00↔100 si aparece "00" literal en el texto
    if "00" in text:
        scores[100] += 0.75
        hits[100].append("00")
    return scores, hits

def attribute_news_to_table100(selected_news: List[Dict[str, Any]],
                               guidance: Dict[str, List[str]]|None=None,
                               min_attr: int = 3,
                               threshold: float = 0.6)->Dict[str, Any]:
    table = build_table100()
    guide_terms = []
    for k in ("topics","keywords","families","guide_terms"):
        guide_terms += [x for x in (guidance or {}).get(k, []) if isinstance(x, str)]

    per_article = []
    totals: Dict[int, float] = defaultdict(float)
    reasons = []

    for a in selected_news or []:
        title = (a.get("title") or "").strip()
        text  = (a.get("text")  or "")  # nuestro pipeline suele tener solo title; está bien.
        blob = (title + " " + text).strip()
        if not blob:
            reasons.append({"url": a.get("final_url") or a.get("url"), "reason":"empty_blob"})
            continue
        sc, hits = _score_article(blob, table, guide_terms)
        # filtra contribuciones débiles
        sc = {k:v for k,v in sc.items() if v>=0.2}
        rank = sorted(sc.items(), key=lambda kv: kv[1], reverse=True)[:5]
        for n, s in rank:
            totals[n] += s
        per_article.append({
            "url": a.get("final_url") or a.get("url"),
            "title": title or "(sin título)",
            "top": [{"number": n, "score": round(s,3), "label": table[n]["label"], "hits": hits.get(n,[])[:6]} for n,s in rank]
        })

    # ranking global de la jornada
    global_rank = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    global_rank = [{"number": n, "score": round(s,3), "label": table[n]["label"], "meaning": table[n]["meaning"]} for n,s in global_rank]

    # auditoría mínima
    ok = len([x for x in global_rank if x["score"]>=threshold]) >= min_attr
    auditor = {
        "ok": ok,
        "threshold": threshold,
        "min_attr": min_attr,
        "kept_above_threshold": len([x for x in global_rank if x["score"]>=threshold]),
        "total_articles": len(per_article),
        "reasons": reasons
    }

    return {
        "table_version": "1.0",
        "per_article": per_article,
        "global_rank": global_rank,
        "auditor": auditor
    }





