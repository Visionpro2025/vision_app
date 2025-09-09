# connectors/florida_official.py
import requests, re, datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

PICK3_URL = "https://floridalottery.com/games/draw-games/pick-3"
PICK4_URL = "https://flalottery.com/pick4"  # redirección válida a la sección Pick 4
P3_PDF_URL = "https://www.flalottery.com/exptkt/p3.pdf"

ET = ZoneInfo("America/New_York")

def _et_now():
    return datetime.datetime.now(ET).replace(microsecond=0).isoformat()

def _norm_date(s: str) -> str:
    # Espera "Mon, Sep 8, 2025" → YYYY-MM-DD
    dt = datetime.datetime.strptime(s.strip(), "%a, %b %d, %Y")
    return dt.date().isoformat()

def fetch_pick3_latest_html(timeout=12):
    r = requests.get(PICK3_URL, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # La página muestra "Pick 3 - Mon, Sep 8, 2025" seguido por "Midday/Evening" y los 3 dígitos + Fireball
    cards = []
    for sec in soup.select("section, div"):
        txt = sec.get_text(" ", strip=True)
        if "Pick 3 - " in txt and any(x in txt for x in ("Midday","Evening")):
            # Fecha
            mdate = re.search(r"Pick 3 - ([A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4})", txt)
            if not mdate: continue
            date = _norm_date(mdate.group(1))
            # Bloque y dígitos (e.g., "Midday 8 8 1 Fireball3")
            block = "MID" if "Midday" in txt else ("EVE" if "Evening" in txt else None)
            nums = re.findall(r"\b\d\b", txt)  # captura dígitos sueltos
            # Heurística: 3 primeros tras el bloque son Pick3
            if block and len(nums) >= 3:
                pick3 = list(map(int, nums[:3]))
                # Fireball (opcional)
                mfb = re.search(r"Fireball\s*([0-9])", txt, re.I)
                fb = int(mfb.group(1)) if mfb else None
                cards.append({"date": date, "block": block, "pick3": pick3, "fireball": fb})
    return sorted(cards, key=lambda x: (x["date"], x["block"]), reverse=True)

def fetch_pick4_latest_html(timeout=12):
    r = requests.get(PICK4_URL, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for sec in soup.select("section, div"):
        txt = sec.get_text(" ", strip=True)
        if "Pick 4" in txt and any(x in txt for x in ("Midday","Evening")) and re.search(r"\b\d\b.\b\d\b.\b\d\b.*\b\d\b", txt):
            mdate = re.search(r"([A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{4})", txt)
            if not mdate: continue
            # Ojo: algunas vistas no repiten "Pick 4 - "; por eso tomamos la 1ra fecha del bloque
            date = _norm_date(mdate.group(1))
            block = "MID" if "Midday" in txt else ("EVE" if "Evening" in txt else None)
            nums = list(map(int, re.findall(r"\b\d\b", txt)))
            if block and len(nums) >= 4:
                pick4 = nums[:4]
                out.append({"date": date, "block": block, "pick4": pick4})
    return sorted(out, key=lambda x: (x["date"], x["block"]), reverse=True)

def merge_p3_p4(p3_list, p4_list, source="flalottery.com"):
    # junta por (date, block)
    idx = {(x["date"], x["block"]): x for x in p3_list}
    for y in p4_list:
        k = (y["date"], y["block"])
        if k in idx:
            idx[k]["pick4"] = y["pick4"]
        else:
            idx[k] = {"date": y["date"], "block": y["block"], "pick4": y["pick4"]}
    out = []
    for v in idx.values():
        v["source"] = source
        v["fetched_at"] = _et_now()
        out.append(v)
    # normaliza bloques: 'MID'|'EVE'
    for v in out:
        v["block"] = "MID" if v["block"].upper().startswith("MID") else "EVE"
    return sorted(out, key=lambda x: (x["date"], x["block"]), reverse=True)



