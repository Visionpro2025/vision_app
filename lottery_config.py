# modules/lottery_config.py
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "logos"

LOTTERIES = {
    "megamillions": {
        "name": "Mega Millions",
        "logo": ASSETS / "megamillions.png",
        "days": ["Tuesday", "Friday"],
        "draw_time_local": "23:00",
        "tz": "America/New_York",
        "site": "https://www.megamillions.com/",
        "notes": "Formato 5/70 + 1/25",
    },
    "powerball": {
        "name": "Powerball",
        "logo": ASSETS / "powerball.png",
        "days": ["Monday", "Wednesday", "Saturday"],
        "draw_time_local": "22:59",
        "tz": "America/New_York",
        "site": "https://www.powerball.com/",
        "notes": "Formato 5/69 + 1/26",
    },
    "lotto_america": {
        "name": "Lotto America",
        "logo": ASSETS / "lotto_america.png",
        "days": ["Monday", "Wednesday", "Saturday"],
        "draw_time_local": "23:15",
        "tz": "America/New_York",
        "site": "https://www.lottoamerica.com/",
        "notes": "Formato 5/52 + 1/10",
    },
    "cash4life": {
        "name": "Cash4Life",
        "logo": ASSETS / "cash4life.png",
        "days": ["Daily"],
        "draw_time_local": "21:00",
        "tz": "America/New_York",
        "site": "https://www.valottery.com/datafile/datafilecash4life",
        "notes": "Formato 5/60 + 1/4",
    },
    "florida_lotto": {
        "name": "Florida Lotto",
        "logo": ASSETS / "florida_lotto.png",
        "days": ["Wednesday", "Saturday"],
        "draw_time_local": "23:15",
        "tz": "America/New_York",
        "site": "https://www.flalottery.com/",
        "notes": "Formato 6/53",
    },
    "ny_lotto": {
        "name": "New York LOTTO",
        "logo": ASSETS / "ny_lotto.png",
        "days": ["Wednesday", "Saturday"],
        "draw_time_local": "23:21",
        "tz": "America/New_York",
        "site": "https://nylottery.ny.gov/",
        "notes": "Formato 6/59",
    },
    "california_superlotto": {
        "name": "CA SuperLotto Plus",
        "logo": ASSETS / "ca_superlotto.png",
        "days": ["Wednesday", "Saturday"],
        "draw_time_local": "19:57",
        "tz": "America/Los_Angeles",
        "site": "https://www.calottery.com/",
        "notes": "Formato 5/47 + 1/27",
    },
    "texas_lotto": {
        "name": "Texas LOTTO",
        "logo": ASSETS / "texas_lotto.png",
        "days": ["Monday", "Wednesday", "Saturday"],
        "draw_time_local": "22:12",
        "tz": "America/Chicago",
        "site": "https://www.txlottery.org/",
        "notes": "Formato 6/54",
    },
    "mass_cash": {
        "name": "Mass Cash",
        "logo": ASSETS / "mass_cash.png",
        "days": ["Daily"],
        "draw_time_local": "22:00",
        "tz": "America/New_York",
        "site": "https://www.masslottery.com/",
        "notes": "Formato 5/35",
    },
    "oregon_megabucks": {
        "name": "Oregon Megabucks",
        "logo": ASSETS / "oregon_megabucks.png",
        "days": ["Monday", "Wednesday", "Saturday"],
        "draw_time_local": "19:29",
        "tz": "America/Los_Angeles",
        "site": "https://www.oregonlottery.org/",
        "notes": "Formato 6/48",
    },
}

DEFAULT_LOTTERY = "megamillions"
