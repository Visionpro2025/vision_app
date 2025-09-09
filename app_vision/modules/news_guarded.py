# ============================================
# 📌 MÓDULO DE VALIDACIÓN Y AUDITORÍA DE NOTICIAS
# Protocolo de Confianza: fechas reales, dominios permitidos, deduplicación
# ============================================

from __future__ import annotations
import re, os, json, hashlib, time, urllib.parse, datetime as dt
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

UA = "App.Vision-NewsBot/1.0 (+https://local.app.vision)"
TIMEOUT = 15

@dataclass
class Evidence:
    url: str
    final_url: str
    domain: str
    status: int
    fetched_at: str
    content_sha256: str
    content_len: int
    date_iso: Optional[str]
    date_confidence: str
    title: Optional[str]
    drop_reason: Optional[str] = None

def _domain(u: str) -> str:
    """Extrae dominio limpio de URL"""
    return urllib.parse.urlparse(u).netloc.lower().replace("www.","")

def _load_policy(path: str) -> Dict[str, Any]:
    """Carga política de dominios desde YAML"""
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _http_get(url: str) -> Tuple[requests.Response, str]:
    """Fetch HTTP con redirecciones y User-Agent"""
    with requests.Session() as s:
        s.headers.update({"User-Agent": UA})
        r = s.get(url, timeout=TIMEOUT, allow_redirects=True)
        return r, r.url

def _sha256(b: bytes) -> str:
    """Hash SHA256 de contenido"""
    return hashlib.sha256(b).hexdigest()

# Selectores de fecha en metadatos HTML
_DATE_META_KEYS = [
    ("meta", {"property":"article:published_time"}),
    ("meta", {"name":"pubdate"}),
    ("meta", {"name":"publish-date"}),
    ("meta", {"name":"date"}),
    ("meta", {"itemprop":"datePublished"}),
    ("meta", {"name":"DC.date.issued"}),
    ("meta", {"name":"dcterms.created"}),
]

# Regex para fechas en JSON-LD
JSONLD_DATE_RE = re.compile(r'"datePublished"\s*:\s*"([^"]+)"', re.IGNORECASE)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE|re.DOTALL)

def _extract_date_and_title(html: str, url: str) -> Tuple[Optional[str], str]:
    """Extrae fecha y título del HTML con múltiples estrategias"""
    soup = BeautifulSoup(html, "html.parser")
    
    # Título
    title = None
    t = soup.find("title")
    title = t.get_text(strip=True) if t else None
    if not title:
        m = TITLE_RE.search(html)
        if m: 
            title = re.sub(r"\s+"," ", m.group(1)).strip()
    
    # Metadatos de fecha
    for kind, attrs in _DATE_META_KEYS:
        tag = soup.find(kind, attrs=attrs)
        if tag and (tag.get("content") or tag.get("datetime")):
            d = tag.get("content") or tag.get("datetime")
            return d, title
    
    # JSON-LD fallback
    m = JSONLD_DATE_RE.search(html)
    if m:
        return m.group(1), title
    
    # URL hint (yyyy/mm/dd o yyyy-mm-dd)
    url_hint = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", url)
    if url_hint:
        return f"{url_hint.group(1)}-{int(url_hint.group(2)):02d}-{int(url_hint.group(3)):02d}", title
    
    return None, title

def _to_iso(date_str: Optional[str]) -> Tuple[Optional[str], str]:
    """Convierte fecha a ISO y asigna confianza"""
    if not date_str: 
        return None, "baja"
    
    try:
        # Normalizar formato
        ds = date_str.strip().replace("Z","").replace("/", "-")
        
        # Si trae hora, quedarse solo con fecha
        if len(ds) >= 19:
            d = dt.datetime.fromisoformat(ds[:19])
        else:
            d = dt.datetime.fromisoformat(ds)
        
        return d.date().isoformat(), "alta"
    except Exception:
        # Heurística día/mes/año y mes/día/año
        m = re.search(r"(\d{4})[-](\d{1,2})[-](\d{1,2})", date_str)
        if m:
            yyyy, mm, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                return dt.date(yyyy, mm, dd).isoformat(), "media"
            except Exception:
                return None, "baja"
        return None, "baja"

def _days_ago(iso: str) -> int:
    """Días transcurridos desde fecha ISO"""
    d = dt.date.fromisoformat(iso)
    return (dt.date.today() - d).days

def _normalize_title(t: Optional[str]) -> str:
    """Normaliza título para deduplicación"""
    if not t: 
        return ""
    t = t.casefold()
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _similar(a: str, b: str) -> float:
    """Similitud Jaccard sobre shingles (determinista)"""
    A, B = set(a.split()), set(b.split())
    if not A or not B: 
        return 0.0
    return len(A & B) / float(len(A | B))

def validate_news(raw_urls: List[str], policy_path: str, evidence_dir: str) -> Dict[str, Any]:
    """
    Valida noticias con Protocolo de Confianza:
    - Dominios permitidos (whitelist)
    - Fechas reales y recientes
    - Deduplicación por similitud de título
    - Evidencia exportable
    """
    os.makedirs(evidence_dir, exist_ok=True)
    pol = _load_policy(policy_path)
    allowed = set(pol.get("allowed_domains", []))
    max_age = int(pol.get("max_age_days", 7))
    min_valid = int(pol.get("min_valid_items", 15))

    evidences: List[Evidence] = []
    seen_titles: List[str] = []

    for u in raw_urls:
        dom = _domain(u)
        
        # Verificar dominio permitido
        if dom not in allowed:
            evidences.append(Evidence(
                u, u, dom, 0, dt.datetime.utcnow().isoformat(), 
                "", 0, None, "baja", None, "domain_not_allowed"
            ))
            continue
        
        try:
            # Fetch HTTP
            r, final_url = _http_get(u)
            html = r.text or ""
            sha = _sha256(html.encode("utf-8", errors="ignore"))
            
            # Extraer fecha y título
            date_raw, title = _extract_date_and_title(html, final_url)
            date_iso, conf = _to_iso(date_raw)
            
            # Validaciones
            reason = None
            status = r.status_code
            
            if status != 200:
                reason = f"http_status_{status}"
            elif date_iso is None:
                reason = "no_date_found"
            elif _days_ago(date_iso) > max_age:
                reason = "too_old"
            else:
                # Deduplicación por título
                nt = _normalize_title(title)
                dup = any(_similar(nt, t) >= 0.85 for t in seen_titles)
                if dup:
                    reason = "duplicate_title"
                else:
                    seen_titles.append(nt)
            
            ev = Evidence(
                url=u, final_url=final_url, domain=dom, status=status,
                fetched_at=dt.datetime.utcnow().isoformat(),
                content_sha256=sha, content_len=len(html),
                date_iso=date_iso, date_confidence=conf, title=title,
                drop_reason=reason
            )
            
            # Guardar snapshot HTML (solo válidos)
            if reason is None:
                snap_path = os.path.join(evidence_dir, f"{sha}.html")
                with open(snap_path, "w", encoding="utf-8") as f:
                    f.write(html)
            
            evidences.append(ev)
            
        except Exception as e:
            evidences.append(Evidence(
                u, u, dom, 0, dt.datetime.utcnow().isoformat(), 
                "", 0, None, "baja", None, f"exception:{e.__class__.__name__}"
            ))

    # Separar válidos y rechazados
    valid = [e for e in evidences if e.drop_reason is None]
    rejected = [e for e in evidences if e.drop_reason is not None]

    # Generar reporte
    report = {
        "policy": {
            "max_age_days": max_age, 
            "min_valid_items": min_valid, 
            "allowed_domains": sorted(list(allowed))
        },
        "metrics": {
            "total_input": len(raw_urls),
            "valid_count": len(valid),
            "rejected_count": len(rejected),
            "rejected_by_reason": {}
        },
        "valid": [e.__dict__ for e in valid],
        "rejected": [e.__dict__ for e in rejected],
    }
    
    # Conteo de razones de rechazo
    for e in rejected:
        report["metrics"]["rejected_by_reason"].setdefault(e.drop_reason, 0)
        report["metrics"]["rejected_by_reason"][e.drop_reason] += 1

    # Condición de evidencia suficiente
    if len(valid) < min_valid:
        report["status"] = "ERROR"
        report["error_kind"] = "InsufficientEvidence"
        report["error_detail"] = f"Solo {len(valid)} válidas de {len(raw_urls)} (mínimo requerido {min_valid})."
    else:
        report["status"] = "OK"

    return report

def save_report(report: Dict[str, Any], path_json: str):
    """Guarda reporte de evidencia en JSON"""
    os.makedirs(os.path.dirname(path_json), exist_ok=True)
    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)




