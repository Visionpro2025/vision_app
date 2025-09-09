from typing import List, Dict

def explain_series_choice(series: List[int], signals: Dict[str,float]) -> str:
    # Señales: {"gematria":0.7, "t70":0.5, "subliminal":0.3, "quantum":0.2}
    orden = sorted(signals.items(), key=lambda kv: kv[1], reverse=True)
    top = ", ".join([f"{k}:{v:.2f}" for k,v in orden])
    return f"Serie {series} respaldada por señales → {top}"







