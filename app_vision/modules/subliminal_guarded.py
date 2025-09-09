from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import hashlib, random

ONTOLOGY: Dict[str, Dict] = {
    "digits": {
        0: {"hebrew":"-",      "families":["vacío"],     "words":["vacío","portal","origen"]},
        1: {"hebrew":"א Alef", "families":["comienzo"],  "words":["comienzo","aliento","unidad","toro"]},
        2: {"hebrew":"ב Bet",  "families":["casa"],      "words":["casa","contenedor","refugio"]},
        3: {"hebrew":"ג Guímel","families":["tránsito"], "words":["tránsito","provisión","camello","puente"]},
        4: {"hebrew":"ד Dálet","families":["apertura"],  "words":["puerta","umbral","acceso","portal"]},
        5: {"hebrew":"ה He",   "families":["revelación"],"words":["soplo","revelación","ventana"]},
        6: {"hebrew":"ו Vav",  "families":["unión"],     "words":["clavo","conexión","unión","lazo"]},
        7: {"hebrew":"ז Zayin","families":["corte"],     "words":["arma","corte","decisión","veredicto"]},
        8: {"hebrew":"ח Jet",  "families":["ciclo"],     "words":["valla","vida","ciclo"]},
        9: {"hebrew":"ט Tet",  "families":["oculto"],    "words":["serpiente","oculto","giro","veneno"]},
    },
    "topics": {
        "apertura":  ["apertura","inauguración","lanzamiento","umbral","portal"],
        "corte":     ["corte","arma","veredicto","decisión","cirugía"],
        "tránsito":  ["tránsito","frontera","puente","movilidad","caravana"],
        "oculto":    ["serpiente","veneno","reptil","antídoto"],
        "casa":      ["hogar","vivienda","propiedad","refugio"],
        "comienzo":  ["inicio","fundación","arranque","semilla"],
        "revelación":["anuncio","señal","declaración","comunicado"],
        "unión":     ["conexión","acuerdo","alianza","firma"],
        "ciclo":     ["lluvia","río","mareas","estación"],
        "vacío":     ["portal","umbral","origen","silencio"],
    },
    "templates": [
        "({label} · {date})",
        "{hebrews}",
        "Escucha la señal en el tránsito del día:",
        "{kw_line}.",
        "Donde el {family_a} toque al {family_b}, la cifra se revela.",
    ]
}

@dataclass
class SubliminalGuarded:
    game: str
    draw_label: str
    input_draw: Tuple[int, int, int]
    hebrew_labels: List[str]
    families_used: List[str]
    keywords_used: List[str]
    poem: str
    topics: List[str]
    trace: List[str] = field(default_factory=list)

def _seed_from(prev_draw: Tuple[int,int,int], label: str, date_str: str)->int:
    s = f"{prev_draw}-{label}-{date_str}"
    return int(hashlib.sha256(s.encode()).hexdigest(), 16) % (2**31-1)

def _choose_words(words: List[str], k: int, rng: random.Random)->List[str]:
    pool = list(dict.fromkeys(words))
    rng.shuffle(pool)
    return pool[:k] if len(pool)>=k else pool

def subliminal_guarded_from_pick3(prev_draw: Tuple[int,int,int],
                                  draw_label: str,
                                  date_str: Optional[str]=None,
                                  max_keywords: int = 6) -> SubliminalGuarded:
    date_str = date_str or datetime.now().strftime("%Y-%m-%d")
    d1,d2,d3 = prev_draw
    assert all(0<=d<=9 for d in prev_draw), "Pick3: dígitos deben estar en 0..9"

    rng = random.Random(_seed_from(prev_draw, draw_label, date_str))

    hebs, families, words = [], [], []
    trace = []
    for d in (d1,d2,d3):
        entry = ONTOLOGY["digits"][d]
        hebs.append(entry["hebrew"])
        families.extend(entry["families"])
        words.extend(entry["words"])
        trace.append(f"digit={d} → {entry['hebrew']} → families={entry['families']} → words={entry['words']}")

    fam_unique = list(dict.fromkeys(families))
    if len(fam_unique) < 2 and len(fam_unique) < len(families):
        if 0 in prev_draw and "vacío" not in fam_unique:
            fam_unique.append("vacío")
        elif 5 in prev_draw and "revelación" not in fam_unique:
            fam_unique.append("revelación")

    kw = _choose_words(words, k=max_keywords, rng=rng)
    kw_line = ", ".join(kw) if kw else "señal"
    heb_line = " · ".join([h for h in hebs if h != "-"]) or "—"

    if len(fam_unique) == 1:
        fam_a, fam_b = fam_unique[0], fam_unique[0]
    else:
        rng.shuffle(fam_unique)
        fam_a, fam_b = fam_unique[0], fam_unique[1]

    tpls = ONTOLOGY["templates"]
    poem_lines = []
    for tpl in tpls:
        line = tpl.format(
            label=draw_label,
            date=date_str,
            hebrews=heb_line,
            kw_line=kw_line,
            family_a=fam_a,
            family_b=fam_b
        )
        poem_lines.append(line)
    poem = "\n".join(poem_lines)

    topics_set = []
    for fam in dict.fromkeys([fam_a, fam_b]):
        topics_set.extend(ONTOLOGY["topics"].get(fam, []))
    rng.shuffle(topics_set)
    topics = list(dict.fromkeys(topics_set))[:6]

    return SubliminalGuarded(
        game="Pick3_FL",
        draw_label=draw_label,
        input_draw=prev_draw,
        hebrew_labels=hebs,
        families_used=[fam_a, fam_b],
        keywords_used=kw,
        poem=poem,
        topics=topics,
        trace=trace + [f"families_used={fam_a},{fam_b}", f"topics={topics}"]
    )




