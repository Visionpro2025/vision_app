# connectors/lotteryusa_backup.py
import requests, datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

ET = ZoneInfo("America/New_York")
MID_URL = "https://www.lotteryusa.com/florida/midday-pick-3/"
EVE_URL = "https://www.lotteryusa.com/florida/evening-pick-3/"
MID4_URL = "https://www.lotteryusa.com/florida/midday-pick-4/"
EVE4_URL = "https://www.lotteryusa.com/florida/evening-pick-4/"

def _fetch_block(url, block):
    r = requests.get(url, timeout=12)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # La tabla de "last 10 results" tiene fechas en formato "Sep 08, 2025"
    rows = soup.select("table tbody tr")[:3]  # tomamos 3 por seguridad
    out = []
    for tr in rows:
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(tds) < 2: continue
        date = datetime.datetime.strptime(tds[0], "%b %d, %Y").date().isoformat()
        nums = [int(x) for x in list(tds[1].replace(" ", "")) if x.isdigit()]
        out.append({"date": date, "block": block, "numbers": nums})
    return out

def fetch_pick3_pick4_backup():
    p3_mid = _fetch_block(MID_URL, "MID")
    p3_eve = _fetch_block(EVE_URL, "EVE")
    p4_mid = _fetch_block(MID4_URL, "MID")
    p4_eve = _fetch_block(EVE4_URL, "EVE")
    # junta por (date, block)
    idx = {}
    for x in p3_mid + p3_eve:
        idx[(x["date"], x["block"])] = {"date": x["date"], "block": x["block"], "pick3": x["numbers"]}
    for y in p4_mid + p4_eve:
        k = (y["date"], y["block"])
        if k in idx:
            idx[k]["pick4"] = y["numbers"]
        else:
            idx[k] = {"date": y["date"], "block": y["block"], "pick4": y["numbers"]}
    out = list(idx.values())
    for v in out:
        v["source"] = "lotteryusa.com"
        v["confidence"] = "secondary"
        v["fetched_at"] = datetime.datetime.now(ET).replace(microsecond=0).isoformat()
    return sorted(out, key=lambda x: (x["date"], x["block"]), reverse=True)


