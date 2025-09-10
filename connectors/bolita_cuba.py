# connectors/bolita_cuba.py
import requests, re, datetime
from bs4 import BeautifulSoup
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
DC_URL = "https://www.directoriocubano.info/bolita/"
LBC_URL = "https://www.labolitacubana.com/"

def _clean2d(s: str) -> str:
    s = re.sub(r"\D", "", s)
    return s[-2:] if len(s)>=2 else s

def fetch_directorio_cubano(timeout=12):
    r = requests.get(DC_URL, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    txt = soup.get_text(" ", strip=True)

    # Heurística: buscar "mediodía/noche" y pares 2D cercanos (fijo/corridos).
    # Ajusta si cambian formatos.
    blocks = []
    for block_lbl in ("Mediodía","Tarde","Noche"):
        if block_lbl in txt:
            segment = txt.split(block_lbl,1)[1][:300]  # ventana corta
            nums = re.findall(r"\b\d{2}\b", segment)
            if nums:
                blocks.append({"slot": block_lbl, "pairs": list(dict.fromkeys(nums))[:5]})
    return {
        "source": DC_URL,
        "fetched_at": datetime.datetime.now(ET).replace(microsecond=0).isoformat(),
        "blocks": blocks
    }

def fetch_labolitacubana(timeout=12):
    r = requests.get(LBC_URL, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    txt = soup.get_text(" ", strip=True)

    # Buscamos menciones directas a "fijo", "corridos", "parlés", "candado"
    # y extraemos NN cercanos (2 dígitos) por bloque (mediodía/noche).
    items = []
    for blk in ("mediodía","noche","Mediodía","Noche"):
        if blk in txt:
            seg = txt.split(blk,1)[1][:400]
            pairs = re.findall(r"\b\d{2}\b", seg)
            items.append({"slot": blk.capitalize(), "pairs": list(dict.fromkeys(pairs))[:8]})
    return {
        "source": LBC_URL,
        "fetched_at": datetime.datetime.now(ET).replace(microsecond=0).isoformat(),
        "blocks": items
    }




