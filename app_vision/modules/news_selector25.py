from __future__ import annotations
from typing import List, Dict, Any, Tuple
import re, unicodedata, math
from collections import defaultdict

SP_STOP = set("a al algo algun algunos ante antes aquel aquella aquellas aquello aquellos aqui arriba abajo bien cada casi como con contra cosa cual cuales cuando cuanto de del desde donde dos el ella ellas ellos en entre era eran es esa esas ese eso esos esta estas este esto estos fue fueron ha haber habia habido hasta la las le les lo los mas más me mi mia mias mientras muy ni no nos nuestra nuestras nuestro nuestros o os otra otro para pero poca poco por porque pues que quien quienes se sea segun según ser si sí sin sobre solo sólo son su sus te tener tuve tuya tuyas tuyos un una uno unos y ya".split())
EN_STOP = set("a an and are as at be by for from has have if in into is it its of on or that the their there they this to was were will with your you we our us not no yes".split())

# Sinónimos mínimos (extensibles) para mapear guía → términos de noticias
SYN = {
    "veredicto": {"verdict","ruling","decision","sentencing","judgment","fallo"},
    "decisión": {"decision","ruling","verdict","order"},
    "corte": {"court","supreme court","appeals","judge","tribunal"},
    "casa": {"home","housing","household","residential","hogar","vivienda"},
    "refugio": {"shelter","homeless","housing assistance","albergue"},
    "propiedad": {"property","homeownership","eviction","foreclosure","title"},
    "umbral": {"threshold","gate","portal","entry","ingreso","acceso"},
    "portal": {"portal","gateway","entry"},
    "contenedor": {"container","shelter","housing unit"},
    # categorías sociales seguras
    "vivienda": {"housing","rent","rental","eviction","homeless","shelter"},
    "empleo": {"employment","jobs","wage","salary","strike","union"},
    "educacion": {"school","education","students","teachers","college"},
    "salud": {"health","mental health","hospital","clinic"},
    "seguridad": {"crime","violence","shooting","safety","police"},
    "inmigracion": {"immigration","migrant","asylum"},
    "comunidad": {"community","neighborhood","barrio","local"},
}

FALLBACK_BUCKETS = {
    "vivienda": SYN["vivienda"],
    "seguridad": SYN["seguridad"],
    "salud": SYN["salud"],
    "educacion": SYN["educacion"],
    "empleo": SYN["empleo"],
    "inmigracion": SYN["inmigracion"],
    "comunidad": SYN["comunidad"],
}

def _strip_acc(s:str)->str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c)!='Mn')

def _tok(s:str)->List[str]:
    t = _strip_acc((s or "").lower())
    t = re.sub(r"[^a-z0-9áéíóúñü\s-]", " ", t)
    toks = [w for w in t.split() if w and len(w)>2 and w not in SP_STOP and w not in EN_STOP]
    return toks

def _expand_guidance(g:Dict[str,List[str]])->List[str]:
    base = []
    for k in ("topics","keywords","families","guide_terms"):
        base += [x for x in (g or {}).get(k,[]) if isinstance(x,str)]
    # añadir sinónimos
    extra = []
    for term in list(base):
        key = _strip_acc(term.lower())
        if key in SYN:
            extra += list(SYN[key])
    return list(dict.fromkeys(base + extra))

def _score(doc:str, guide_terms:List[str])->Tuple[float,List[str]]:
    toks = set(_tok(doc))
    guide = set(_tok(" ".join(guide_terms)))
    inter = toks & guide
    if not toks: 
        return 0.0, []
    # score: coincidencias ajustadas por longitud (TF-lite) + bonus por términos "fuertes"
    strong = {"verdict","ruling","eviction","shelter","housing","homeless","court","decision","refugio","vivienda"}
    base = len(inter) / (1.0 + math.log(1+len(toks)))
    bonus = 0.25 * len([w for w in inter if w in strong])
    return base + bonus, sorted(list(inter))[:8]

def _matches_bucket(doc:str, vocab:set[str])->bool:
    t = " ".join(_tok(doc))
    return any(v in t for v in vocab)

def select_min25(news:List[Dict[str,Any]], guidance:Dict[str,List[str]], 
                 start_thr:float=0.6, min_keep:int=25, min_body:bool=False)->Dict[str,Any]:
    """
    news: Items reales con al menos {title, url|final_url, (summary|text opcional)}
    guidance: del Paso 3
    Ajusta el umbral hacia abajo hasta conseguir >= min_keep. Si falta, rellena por buckets sociales.
    """
    guide = _expand_guidance(guidance)
    # 1) Scoring principal
    scored = []
    for a in news or []:
        title = a.get("title") or ""
        text  = a.get("text") or a.get("summary") or ""
        if min_body and not text:
            continue
        doc = (title + " " + text).strip()
        if not doc:
            continue
        s, hits = _score(doc, guide)
        scored.append({
            "url": a.get("final_url") or a.get("url"),
            "title": title or "(sin título)",
            "score": round(s,4),
            "hits": hits,
            "bucket": a.get("bucket") or None
        })
    # Orden inicial
    scored.sort(key=lambda x: x["score"], reverse=True)

    # 2) Umbral dinámico (0.6 → 0.5 → 0.45 → 0.4 → 0.35)
    thresholds = [start_thr, 0.5, 0.45, 0.4, 0.35]
    kept = []
    used_urls = set()
    chosen_thr = None
    for thr in thresholds:
        kept = [x for x in scored if x["score"] >= thr and x["url"] and x["url"] not in used_urls]
        # dedup urls manteniendo orden
        used_urls = set([x["url"] for x in kept])
        chosen_thr = thr
        if len(kept) >= min_keep:
            kept = kept[:max(min_keep, 25)]  # al menos 25; puede devolver más
            break

    # 3) Fallback por buckets sociales si aún falta
    reasons = []
    if len(kept) < min_keep:
        need = min_keep - len(kept)
        # Construye candidatos no elegidos aún
        remaining = [x for x in scored if x["url"] not in used_urls]
        # bucketizar por vocab
        added = []
        for bname, vocab in FALLBACK_BUCKETS.items():
            if need <= 0: break
            for x in remaining:
                if x["url"] in used_urls: 
                    continue
                doc = (x["title"] + " " + " ".join(x.get("hits",[]))).lower()
                # también probar contra vocab del bucket
                if _matches_bucket(doc, set(v.lower() for v in vocab)):
                    added.append({**x, "reason":"fallback:"+bname})
                    used_urls.add(x["url"])
                    need -= 1
                if need <= 0: break
        kept += added
        reasons.append(f"fallback_used={len(added)}")

    # 4) Si aún no llegamos, devolver lo que hay (sin inventar)
    kept = kept[:max(len(kept), min_keep)] if len(kept)>=min_keep else kept

    audit = {
        "input_total": len(news or []),
        "scored_total": len(scored),
        "selected": len(kept),
        "threshold_chosen": chosen_thr,
        "fallback_applied": any("reason" in k for k in kept),
        "reasons": reasons,
        "guide_terms_used": guide[:50]
    }
    return {"selected": kept, "audit": audit}



