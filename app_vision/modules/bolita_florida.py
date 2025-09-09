# ============================================
# 📌 MÓDULO BOLITA FLORIDA - LÓGICA DEL CANDADO
# Implementación quirúrgica para Florida Quiniela (objetivo: candado)
# ============================================

from typing import Dict, Any, List, Tuple, Set

def _empuje(fijo: str) -> str:
    """Calcula el empuje: (suma de dígitos del fijo) mod 10 * 2"""
    return str((int(fijo[0]) + int(fijo[1])) % 10) * 2

def _senales(p3: str, fijo: str) -> Dict[str, int | str]:
    """Calcula señales energéticas: suma total, raíz mod10, empuje, reversa"""
    s_total = sum(map(int, p3))
    return {
        "suma_total": s_total, 
        "raiz": s_total % 10, 
        "empuje": _empuje(fijo), 
        "reversa": fijo[::-1]
    }

def _equivalencia_cero_100(conjunto_2d: List[str], noticias: Set[int] | None, enabled: bool) -> Dict[str, Any]:
    """Regla 00↔100: activa solo si hay '00' en 2D y 100 en noticias"""
    if not enabled:
        return {"presente_00": False, "hay_100_noticias": False, "equivalencia_activa": False}
    
    noticias = noticias or set()
    presente = "00" in conjunto_2d
    hay_100 = 100 in noticias
    return {
        "presente_00": presente, 
        "hay_100_noticias": hay_100, 
        "equivalencia_activa": (presente and hay_100)
    }

def _parles(triada: List[str], ordenados: bool) -> List[Tuple[str, str]]:
    """Genera parlés: 3 sin orden o 6 ordenados según configuración"""
    if ordenados:
        return [(triada[i], triada[j]) for i in range(len(triada)) for j in range(len(triada)) if i != j]
    return [(triada[i], triada[j]) for i in range(len(triada)) for j in range(i+1, len(triada))]

def _formar_triada(fijo: str, corr_bloque: str | None, corr_dia: str,
                   usar_p4: bool, activar_empuje: bool, activar_reversa: bool) -> List[str]:
    """Forma la tríada del candado: {fijo, corrido-bloque, corrido-día} + derivados si falta"""
    base = [fijo]
    if usar_p4 and corr_bloque:
        base.append(corr_bloque)
    base.append(corr_dia)
    
    triada: List[str] = []
    for n in base:
        if n and n not in triada: 
            triada.append(n)
    
    # Completar tríada con empuje si falta
    if len(triada) < 3 and activar_empuje:
        e = _empuje(fijo)
        if e not in triada: 
            triada.append(e)
    
    # Completar tríada con reversa si falta
    if len(triada) < 3 and activar_reversa:
        r = fijo[::-1]
        if r not in triada: 
            triada.append(r)
    
    return triada[:3]

def _bloque(p3: str, p4: str | None, p3_otro: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Procesa un bloque (MID o EVE) completo"""
    fijo = p3[-2:]
    corr_bloque = (p4[-2:] if p4 else None)
    corr_dia = p3_otro[-2:]
    
    triada = _formar_triada(fijo, corr_bloque, corr_dia,
                            cfg.get("usar_p4_como_corrido_bloque", True),
                            cfg.get("activar_empuje", True),
                            cfg.get("activar_reversa", True))
    
    meta = _senales(p3, fijo)
    conjunto = list({*triada, meta["empuje"], meta["reversa"]})
    
    eq = _equivalencia_cero_100(conjunto, set(cfg.get("noticias_equivalentes", []) or []),
                                cfg.get("equivalencia_cero_100", True))
    
    return {
        "candado": triada,
        "parles": _parles(triada, cfg.get("parles_ordenados", False)),
        "conjunto_2D": conjunto,
        "metadatos": meta,
        "equivalencia_00_100": eq,
        "explicacion_breve": f"Fijo={fijo}, CorrBloque={corr_bloque}, CorrDia={corr_dia} → Candado={triada}"
    }

def candado_florida_quini(p3_mid: str, p4_mid: str, p3_eve: str, p4_eve: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función principal: genera candados para MID y EVE
    
    Parámetros:
        p3_mid: Pick 3 Midday (3 dígitos)
        p4_mid: Pick 4 Midday (4 dígitos)
        p3_eve: Pick 3 Evening (3 dígitos)
        p4_eve: Pick 4 Evening (4 dígitos)
        cfg: Configuración del módulo
    
    Retorna:
        Dict con candados, parlés, metadatos y equivalencias
    """
    mid = _bloque(p3_mid, p4_mid, p3_eve, cfg)
    eve = _bloque(p3_eve, p4_eve, p3_mid, cfg)
    
    return {
        "candado_mid": mid["candado"], 
        "parles_mid": mid["parles"], 
        "conjunto_2D_mid": mid["conjunto_2D"],
        "candado_eve": eve["candado"], 
        "parles_eve": eve["parles"], 
        "conjunto_2D_eve": eve["conjunto_2D"],
        "metadatos": {"mid": mid["metadatos"], "eve": eve["metadatos"]},
        "equivalencia": {"mid": mid["equivalencia_00_100"], "eve": eve["equivalencia_00_100"]},
        "explicacion_mid": mid["explicacion_breve"], 
        "explicacion_eve": eve["explicacion_breve"]
    }




