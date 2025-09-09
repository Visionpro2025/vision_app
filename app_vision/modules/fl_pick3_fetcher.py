# app_vision/modules/fl_pick3_fetcher.py
from __future__ import annotations
from typing import List, Dict, Any, Tuple
import re, requests
from bs4 import BeautifulSoup
from datetime import datetime

UA = "App.Vision/1.0 (+real-data; FloridaPick3)"
TIMEOUT = 15

URLS_HTML = [
    "https://www.flalottery.com/pick3",
    "https://floridalottery.com/games/draw-games/pick-3",
    "https://www.flalottery.com/winningNumbers"
]
URL_PDF = "https://www.flalottery.com/exptkt/p3.pdf"  # Winning Numbers History (oficial)

DATE_PATTERNS = [
    # Ejemplos que aparecen en el sitio: "Fri, Sep 5, 2025" o "Wed, Sep 03, 2025"
    (r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+([A-Za-z]{3})\s+(\d{1,2}),\s+(20\d{2})", "%b %d %Y"),
    # fallback numérico si hiciera falta: "09/05/25"
    (r"\b(\d{2})/(\d{2})/(\d{2})\b", None),
]

def _parse_date(text: str) -> datetime | None:
    t = text.strip()
    for pat, fmt in DATE_PATTERNS:
        m = re.search(pat, t)
        if m:
            if fmt:
                mon, day, year = m.group(2), m.group(3), m.group(4)
                return datetime.strptime(f"{mon} {day} {year}", fmt)
            else:
                mm, dd, yy = m.group(1), m.group(2), m.group(3)
                return datetime.strptime(f"{mm}/{dd}/{yy}", "%m/%d/%y")
    return None

def _num_list_from_text(chunk: str) -> Tuple[List[int], int | None]:
    # Extrae 3 dígitos y Fireball (si está) de un bloque cercano.
    digits = [int(x) for x in re.findall(r"\b([0-9])\b", chunk)[:3]]
    fb = re.search(r"Fireball\s*([0-9])", chunk, flags=re.I)
    return (digits if len(digits)==3 else [], int(fb.group(1)) if fb else None)

def _fetch_html_results() -> List[Dict[str, Any]]:
    s = requests.Session(); s.headers.update({"User-Agent": UA})
    rows: List[Dict[str, Any]] = []
    for url in URLS_HTML:
        try:
            r = s.get(url, timeout=TIMEOUT)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            # Buscamos tarjetas/filas que contengan bloques de fecha y Midday/Evening
            text = soup.get_text(" ", strip=True)
            # Cortes por fecha → luego buscamos bloques "Midday / Evening" cercanos
            for seg in re.split(r"(?=(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+[A-Za-z]{3}\s+\d{1,2},\s+20\d{2})", text):
                dt = _parse_date(seg)
                if not dt: 
                    continue
                # Midday
                m_mid = re.search(r"\b(Midday)\b(.{0,80})", seg, flags=re.I)
                if m_mid:
                    nums, fb = _num_list_from_text(m_mid.group(0))
                    if nums:
                        rows.append({"date": dt.strftime("%Y-%m-%d"), "block": "MID", "numbers": nums, "fireball": fb, "source": url})
                # Evening
                m_eve = re.search(r"\b(Evening)\b(.{0,80})", seg, flags=re.I)
                if m_eve:
                    nums, fb = _num_list_from_text(m_eve.group(0))
                    if nums:
                        rows.append({"date": dt.strftime("%Y-%m-%d"), "block": "EVE", "numbers": nums, "fireball": fb, "source": url})
        except Exception:
            continue
    return rows

def _fetch_pdf_results(max_pages: int = 2) -> List[Dict[str, Any]]:
    """
    Plan B: PDF oficial (histórico). Para evitar dependencias pesadas,
    usamos una lectura simple del binario como texto; muchos PDF de lotería
    son text-based y permiten extracción básica.
    """
    s = requests.Session(); s.headers.update({"User-Agent": UA})
    try:
        r = s.get(URL_PDF, timeout=TIMEOUT)
        r.raise_for_status()
        text = r.content.decode("latin-1", errors="ignore")  # suele bastar para PDF con texto plano
    except Exception:
        return []

    rows: List[Dict[str, Any]] = []
    # El PDF lista líneas con fechas repetidas y etiquetas E/M (Evening/Midday)
    # Buscamos patrones tipo "09/06/25" y en el entorno de esa línea intentamos extraer 3 dígitos y E/M.
    for m in re.finditer(r"(\d{2}/\d{2}/\d{2})", text):
        dt = m.group(1)
        # ventana de contexto
        start = max(0, m.start()-120)
        end   = m.end()+120
        blob = text[start:end]
        # etiqueta E/M
        block = "EVE" if re.search(r"\bE\b", blob) else ("MID" if re.search(r"\bM\b", blob) else None)
        nums = [int(x) for x in re.findall(r"\b([0-9])\b", blob)[:3]]
        if len(nums)==3 and block:
            # normaliza fecha a YYYY-MM-DD
            try:
                dtn = datetime.strptime(dt, "%m/%d/%y").strftime("%Y-%m-%d")
                rows.append({"date": dtn, "block": block, "numbers": nums, "fireball": None, "source": URL_PDF})
            except Exception:
                continue
    return rows

def fetch_last_n(n: int = 5) -> List[Dict[str, Any]]:
    """
    Devuelve N sorteos REALES más recientes combinando HTML y PDF oficial.
    Sin datos → lista vacía (el step llamante debe ABORTAR).
    """
    rows = _fetch_html_results()
    if len(rows) < n:
        rows += _fetch_pdf_results()
    # ordenar por fecha + bloque (EVE después de MID para misma fecha)
    def key(x): 
        return (x["date"], 1 if x["block"]=="MID" else 2)
    rows = sorted(rows, key=key, reverse=True)

    # dedup por (date, block)
    seen = set(); out = []
    for r in rows:
        k = (r["date"], r["block"])
        if k in seen: 
            continue
        seen.add(k); out.append(r)
        if len(out) >= n:
            break
    return out




