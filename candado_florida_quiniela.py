# ============================================
# 📌 Módulo: Candado Florida Quiniela (Bolita)
# Este bloque se integra al PROTOCOLO UNIVERSAL
# y SOLO se aplica cuando se analice "Florida Quiniela"
# ============================================

from typing import Dict, Any

def candado_florida(p3_mid: str, p4_mid: str, p3_eve: str, p4_eve: str) -> Dict[str, Any]:
    """
    Construye el candado cubano a partir de los sorteos oficiales
    de la Lotería de la Florida (Pick 3 / Pick 4, Midday & Evening).
    
    Parámetros:
        p3_mid (str) -> Ej: "698"  (Pick 3 Midday)
        p4_mid (str) -> Ej: "5184" (Pick 4 Midday)
        p3_eve (str) -> Ej: "607"  (Pick 3 Evening)
        p4_eve (str) -> Ej: "1670" (Pick 4 Evening)

    Retorna:
        dict con:
          - conjunto_2D (lista): todos los 2D generados
          - candado_mid (lista): candado del bloque MID
          - candado_eve (lista): candado del bloque EVE
          - parles_mid / parles_eve (listas de parlés)
          - metadatos (suma total y raíz mod10 de cada Pick 3)
    """
    
    def procesar_bloque(p3: str, p4: str, p3_otro: str) -> Dict[str, Any]:
        fijo = p3[-2:]
        corrido_bloque = p4[-2:]
        corrido_dia = p3_otro[-2:]
        
        # derivados
        suma_total = sum(int(d) for d in p3)
        raiz_mod10 = suma_total % 10
        empuje = str((int(fijo[0]) + int(fijo[1])) % 10) * 2
        reversa = fijo[::-1]
        
        # conjunto de trabajo
        conjunto = list({fijo, corrido_bloque, corrido_dia, empuje, reversa})
        
        # candado y parlés
        candado = list({fijo, corrido_bloque, corrido_dia})
        parles = [(candado[i], candado[j]) for i in range(len(candado)) for j in range(i+1, len(candado))]
        
        return {
            "fijo": fijo,
            "corrido_bloque": corrido_bloque,
            "corrido_dia": corrido_dia,
            "conjunto_2D": conjunto,
            "candado": candado,
            "parles": parles,
            "suma_total": suma_total,
            "raiz_mod10": raiz_mod10,
            "empuje": empuje,
            "reversa": reversa
        }
    
    mid = procesar_bloque(p3_mid, p4_mid, p3_eve)
    eve = procesar_bloque(p3_eve, p4_eve, p3_mid)
    
    return {
        "candado_mid": mid["candado"],
        "candado_eve": eve["candado"],
        "parles_mid": mid["parles"],
        "parles_eve": eve["parles"],
        "conjunto_2D_mid": mid["conjunto_2D"],
        "conjunto_2D_eve": eve["conjunto_2D"],
        "metadatos": {
            "suma_total_mid": mid["suma_total"], "raiz_mid": mid["raiz_mod10"],
            "suma_total_eve": eve["suma_total"], "raiz_eve": eve["raiz_mod10"]
        }
    }

# ===========================
# 📌 Ejemplo de uso real
# Resultados 7 sep 2025 (ejemplo histórico):
if __name__ == "__main__":
    ejemplo = candado_florida(p3_mid="698", p4_mid="5184", p3_eve="607", p4_eve="1670")

    print("== Candado MID ==", ejemplo["candado_mid"])
    print("Parlés MID:", ejemplo["parles_mid"])
    print("== Candado EVE ==", ejemplo["candado_eve"])
    print("Parlés EVE:", ejemplo["parles_eve"])
    print("Conjunto 2D EVE:", ejemplo["conjunto_2D_eve"])
    print("Metadatos suma/raíz:", ejemplo["metadatos"])




