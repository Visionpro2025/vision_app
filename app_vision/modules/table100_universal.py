from __future__ import annotations
from typing import Dict, List, Any
import re

def _kw(s: str)->List[str]:
    return [w.strip().lower() for w in re.split(r"[,\|/;]", s) if w.strip()]

def build_table100()->Dict[int, Dict[str, Any]]:
    """
    Tabla 1..100 minimal pero extensible: label, significado, keywords ES/EN.
    Puedes enriquecer en caliente sin romper el API.
    """
    base: Dict[int, Dict[str, Any]] = {
        1:  {"label":"inicio", "meaning":"comienzo, impulso, identidad", "kw":_kw("inicio,comienzo,arranque,uno,unidad,begin,start,seed,identity")},
        2:  {"label":"cooperación","meaning":"pareja, acuerdos, balance","kw":_kw("pareja,acuerdo,alianza,dos,balance,union,cooperate,deal,agreement")},
        3:  {"label":"expresión","meaning":"comunicación, creatividad","kw":_kw("voz,habla,expresión,poesía,arte,creative,expression,voice")},
        4:  {"label":"estabilidad","meaning":"estructura, hogar, base","kw":_kw("casa,techo,hogar,estructura,base,estabilidad,home,house,structure")},
        5:  {"label":"cambio","meaning":"movimiento, viaje, riesgo","kw":_kw("viaje,carretera,movilidad,riesgo,change,travel,move")},
        6:  {"label":"responsabilidad","meaning":"familia, servicio, cuidado","kw":_kw("familia,cuidado,salud,servicio,care,family,service")},
        7:  {"label":"búsqueda","meaning":"sabiduría, espiritualidad","kw":_kw("espiritual,templo,oración,estudio,sabiduría,wisdom,spiritual")},
        8:  {"label":"poder","meaning":"economía, autoridad, éxito","kw":_kw("salario,empleo,negocio,autoridad,éxito,business,power,income")},
        9:  {"label":"humanidad","meaning":"solidaridad, cierre, ayuda","kw":_kw("ayuda,solidaridad,duelo,crisis,voluntariado,help,aid,crisis,relief")},
        10: {"label":"portal","meaning":"umbral, anuncio","kw":_kw("anuncio,apertura,lanzamiento,announcement,launch,opening")},
        # ... (puedes completar 11..99 según tu catálogo)
        100:{"label":"pescado","meaning":"cierre de ciclo x10, renuevo","kw":_kw("cero,00,cierre,pescado,renovación,renew,zero,end,reset")}
    }
    # Relleno ligero para 11..99: heredan de la decena (heurística sencilla)
    dec_map = {
        10: base[10], 20: base[2], 30: base[3], 40: base[4], 50: base[5],
        60: base[6], 70: base[7], 80: base[8], 90: base[9]
    }
    for d in range(11, 100):
        if d in base: continue
        dec = (d//10)*10
        unit = d % 10
        if dec in dec_map and unit in base:
            lbl = f"{dec_map[dec]['label']}-{base[unit]['label']}"
            mean = f"{dec_map[dec]['meaning']} + {base[unit]['meaning']}"
            kw = list(dict.fromkeys(dec_map[dec]["kw"] + base[unit]["kw"]))
            base[d] = {"label": lbl, "meaning": mean, "kw": kw}
        else:
            base[d] = {"label": f"n{d}", "meaning":"—", "kw":[]}
    return base



