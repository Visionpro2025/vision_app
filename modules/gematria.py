import streamlit as st

def show_gematria():
    st.title("🔡 Capa Gematría")
    st.info("Módulo de Gematría en construcción 🚧")
# ==============================
# Lote gematría desde noticias
# ==============================
from pathlib import Path
from datetime import datetime
import pandas as pd

def _g_repo_root() -> Path:
    try:
        return Path(__file__).resolve().parent.parent
    except Exception:
        return Path.cwd()

def _g_load_csv_safe(path: Path):
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8")
    except Exception:
        return None

def _g_load_translit_table(corpus_dir: Path) -> dict[str, int]:
    """
    Intenta cargar __CORPUS/GEMATRIA/translit_table.csv con columnas:
    'char','value'. Si no existe, usa un fallback a=1, b=2,..., z=26.
    """
    table = {}
    tpath = corpus_dir / "translit_table.csv"
    if tpath.exists():
        try:
            df = pd.read_csv(tpath, dtype=str, encoding="utf-8")
            for _, r in df.iterrows():
                ch = str(r.get("char", "")).lower().strip()
                try:
                    val = int(str(r.get("value", "0")).strip())
                except Exception:
                    val = 0
                if ch:
                    table[ch] = val
            if table:
                return table
        except Exception:
            pass

    # Fallback latino simple
    abc = "abcdefghijklmnopqrstuvwxyz"
    for i, ch in enumerate(abc, start=1):
        table[ch] = i
    return table

def _g_reduce_number(n: int) -> int:
    """Reducción tipo 'digital root' (1..9), con 0 si n=0."""
    if n == 0:
        return 0
    r = n % 9
    return 9 if r == 0 else r

def _g_phrase_value(text: str, char_map: dict[str, int]) -> tuple[int, int]:
    """
    Suma valores por caracter (a-z y dígitos con valor = dígito),
    devuelve (total, reducido).
    """
    total = 0
    for ch in (text or "").lower():
        if ch.isalpha():
            total += char_map.get(ch, 0)
        elif ch.isdigit():
            total += int(ch)
    return total, _g_reduce_number(total)

def run_gematria_batch() -> str:
    """
    Lee noticias.csv y produce:
      - __RUNS/GEMATRIA/gematria_tokens_YYYYMMDD.csv
      - __RUNS/GEMATRIA/gematria_news_YYYYMMDD.csv
    Usa 'titular + resumen + etiquetas' como frase base.
    """
    root = _g_repo_root()
    runs = root / "__RUNS" / "GEMATRIA"
    corpus = root / "__CORPUS" / "GEMATRIA"
    runs.mkdir(parents=True, exist_ok=True)

    news_path = root / "noticias.csv"
    df_news = _g_load_csv_safe(news_path)
    if df_news is None or df_news.empty:
        raise RuntimeError("noticias.csv no existe o está vacío.")

    char_map = _g_load_translit_table(corpus)

    tokens_rows = []
    news_rows = []

    for _, r in df_news.iterrows():
        nid = str(r.get("id_noticia", ""))
        base_text = " ".join([
            str(r.get("titular", "")),
            str(r.get("resumen", "")),
            str(r.get("etiquetas", "")),
        ]).strip()

        total, reducido = _g_phrase_value(base_text, char_map)
        news_rows.append({
            "id_noticia": nid,
            "frase_base": base_text,
            "valor_total": total,
            "valor_reducido": reducido,
        })

        # Tokens (muy simple: palabras alfanuméricas >2)
        for tok in pd.Series(base_text.split()):
            t = "".join(ch for ch in str(tok).lower() if ch.isalnum())
            if len(t) < 3:
                continue
            v, vr = _g_phrase_value(t, char_map)
            tokens_rows.append({
                "id_noticia": nid,
                "token": t,
                "valor_total": v,
                "valor_reducido": vr,
            })

    df_tokens = pd.DataFrame(tokens_rows)
    df_out = pd.DataFrame(news_rows)

    stamp = datetime.utcnow().strftime("%Y%m%d")
    f_tokens = runs / f"gematria_tokens_{stamp}.csv"
    f_news   = runs / f"gematria_news_{stamp}.csv"

    if not df_tokens.empty:
        df_tokens.to_csv(f_tokens, index=False, encoding="utf-8")
    df_out.to_csv(f_news, index=False, encoding="utf-8")

    return f"Exportado: {f_news.name} (+ {len(df_tokens)} tokens)"
