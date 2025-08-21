# ================== PARTE 1/4 — Núcleo: router, backup, cola, papelera, pegado ==================

# ---- Router/Navegación fiable (para función 18 y menús) ----
NAV_KEY = "_nav"
NAV_LABELS = {
    "gematria": ["🔡 Gematría", "Gematría", "Gematria"],
    "subliminal": ["🌀 Análisis subliminal", "Análisis subliminal", "Subliminal"],
    "noticias_crudas": ["🗞️ Crudas", "Crudas"],
    "noticias_filtradas": ["🔥 Filtradas", "Filtradas"],
    "noticias_procesar": ["⚙️ Procesar", "Procesar"],
    "noticias_explorar": ["🔎 Explorador / Ingreso", "Explorador", "Ingreso"],
    "noticias_papelera": ["🗑️ Papelera", "Papelera"],
    "noticias_limpiar": ["🧹 Limpiar", "Limpiar"],
}

def _router_go(target_key: str):
    labels = NAV_LABELS.get(target_key, [target_key])
    target = labels[0]
    # Compatibilidad con múltiples llaves de sesión
    st.session_state[NAV_KEY] = target
    st.session_state["nav"] = target
    st.session_state["page"] = target
    st.rerun()

# ---- ID generator seguro (por si falta o quieres versión estable) ----
def _gen_id(prefix: str = "N") -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    base = f"{prefix}-{today}"
    try:
        df = _load_news(NEWS_CSV)
    except Exception:
        df = pd.DataFrame(columns=["id_noticia"])
    n = int(df["id_noticia"].astype(str).str.startswith(base).sum()) + 1
    return f"{base}-{n:03d}"

# ---- Backup explícito con sello ----
def _backup_now(df: pd.DataFrame) -> Path:
    RUNS_NEWS.mkdir(parents=True, exist_ok=True)
    bpath = RUNS_NEWS / f"backup_noticias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv"
    df.to_csv(bpath, index=False, encoding="utf-8")
    return bpath

# ---- Papelera (cesto) con restaurar/vaciar/exportar) ----
TRASH_CSV = RUNS_NEWS / ".trash.csv"

def _load_trash() -> pd.DataFrame:
    try:
        tdf = pd.read_csv(TRASH_CSV, dtype=str, encoding="utf-8").fillna("") if TRASH_CSV.exists() else pd.DataFrame()
    except Exception:
        tdf = pd.DataFrame()
    # Asegura columnas
    for c in REQUIRED_COLS:
        if c not in tdf.columns: tdf[c] = ""
    return tdf[REQUIRED_COLS]

def _move_to_trash(df: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    if not ids: return df
    sel = df[df["id_noticia"].isin(ids)].copy()
    if sel.empty: return df
    trash = _load_trash()
    new_trash = pd.concat([trash, sel], ignore_index=True)
    new_trash = new_trash.drop_duplicates(subset=["id_noticia"], keep="last").reset_index(drop=True)
    new_trash.to_csv(TRASH_CSV, index=False, encoding="utf-8")
    cleaned = df[~df["id_noticia"].isin(ids)].reset_index(drop=True)
    _save_news(cleaned)
    return cleaned

def _restore_from_trash(ids: list[str]) -> None:
    if not ids: return
    trash = _load_trash()
    sel = trash[trash["id_noticia"].isin(ids)].copy()
    if sel.empty: return
    base = _load_news(NEWS_CSV)
    merged = pd.concat([base, sel], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url", "id_noticia"], keep="first").reset_index(drop=True)
    _save_news(merged)
    remain = trash[~trash["id_noticia"].isin(ids)].reset_index(drop=True)
    remain.to_csv(TRASH_CSV, index=False, encoding="utf-8")

def _purge_trash() -> None:
    pd.DataFrame(columns=REQUIRED_COLS).to_csv(TRASH_CSV, index=False, encoding="utf-8")

def _ui_papelera():
    st.subheader("🗑️ Papelera de noticias")
    tdf = _load_trash()
    if tdf.empty:
        st.info("La papelera está vacía.")
        return
    view = tdf.sort_values(["fecha", "fuente", "titular"], ascending=[False, True, True]).reset_index(drop=True)
    st.caption(f"En papelera: **{len(view)}**")
    ids = st.multiselect("Selecciona id_noticia para actuar", options=view["id_noticia"].tolist())
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("♻️ Restaurar seleccionadas", use_container_width=True, disabled=not ids):
            _restore_from_trash(ids); st.success(f"Restauradas {len(ids)}."); st.rerun()
    with c2:
        if st.button("🧹 Vaciar papelera", use_container_width=True):
            _purge_trash(); st.success("Papelera vaciada."); st.rerun()
    with c3:
        st.download_button(
            "⬇️ Exportar papelera (CSV)",
            view.to_csv(index=False).encode("utf-8"),
            file_name=f"papelera_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv",
            use_container_width=True,
        )

# ---- Cola de procesamiento (Gematría/Subliminal) ----
QUEUE_CSV = RUNS_NEWS / "queue_to_process.csv"

def _queue_list() -> pd.DataFrame:
    try:
        if QUEUE_CSV.exists():
            qdf = pd.read_csv(QUEUE_CSV, dtype=str, encoding="utf-8").fillna("")
        else:
            qdf = pd.DataFrame(columns=REQUIRED_COLS)
    except Exception:
        qdf = pd.DataFrame(columns=REQUIRED_COLS)
    for c in REQUIRED_COLS:
        if c not in qdf.columns: qdf[c] = ""
    return qdf[REQUIRED_COLS]

def _queue_add(rows: pd.DataFrame | list[dict]) -> None:
    base = _queue_list()
    if isinstance(rows, list):
        add = pd.DataFrame(rows)
    else:
        add = rows.copy()
    for c in REQUIRED_COLS:
        if c not in add.columns: add[c] = ""
    merged = pd.concat([base, add[REQUIRED_COLS]], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url", "id_noticia"], keep="first")
    merged.to_csv(QUEUE_CSV, index=False, encoding="utf-8")

def _queue_clear() -> None:
    pd.DataFrame(columns=REQUIRED_COLS).to_csv(QUEUE_CSV, index=False, encoding="utf-8")

def _ui_queue():
    st.subheader("📥 Cola de procesamiento (Gematría / Subliminal)")
    qdf = _queue_list()
    st.caption(f"En cola: **{len(qdf)}**")
    if qdf.empty:
        st.info("No hay elementos en la cola.")
        return
    # Vista compacta
    show = qdf[["id_noticia", "fecha", "fuente", "titular", "url"]].reset_index(drop=True)
    st.dataframe(show, use_container_width=True, hide_index=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔤 Ir a Gematría", use_container_width=True):
            _router_go("gematria")
    with c2:
        if st.button("🌀 Ir a Subliminal", use_container_width=True):
            _router_go("subliminal")
    with c3:
        if st.button("🗑️ Vaciar cola", use_container_width=True):
            _queue_clear(); st.success("Cola vaciada."); st.rerun()

# ---- Enumerador para vistas numeradas ----
def _enumerate_df(df: pd.DataFrame) -> pd.DataFrame:
    dff = df.reset_index(drop=True).copy()
    dff.insert(0, "#", range(1, len(dff) + 1))
    return dff

# ---- Pegado manual: parseo y alta ----
def _manual_paste_parse(raw_text: str) -> pd.DataFrame:
    """
    Soporta formatos por línea:
    - titulo | resumen | fuente | url
    - titulo — resumen (url opcional)
    - solo url (intenta titular desde URL más adelante si procede)
    """
    rows = []
    for line in (raw_text or "").splitlines():
        line = line.strip()
        if not line: continue
        tit, res, fue, url = "", "", "", ""
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 1: tit = parts[0]
            if len(parts) >= 2: res = parts[1]
            if len(parts) >= 3: fue = parts[2]
            if len(parts) >= 4: url = parts[3]
        elif " — " in line:
            parts = [p.strip() for p in line.split(" — ", 1)]
            tit = parts[0]; res = parts[1] if len(parts) > 1 else ""
        else:
            # Podría ser URL sola
            if line.startswith("http"):
                url = line
                tit = "Noticia (manual)"
        rows.append({
            "id_noticia": _gen_id("N"),
            "fecha": datetime.utcnow().strftime("%Y-%m-%d"),
            "sorteo": "", "pais": "US", "fuente": fue or "manual",
            "titular": tit, "resumen": res, "etiquetas": "manual;ingreso",
            "nivel_emocional_diccionario": "", "nivel_emocional_modelo": "",
            "nivel_emocional_final": "", "noticia_relevante": "",
            "categorias_t70_ref": "", "url": url,
        })
    return pd.DataFrame(rows).fillna("")

def _ingest_manual(rows: pd.DataFrame, destino: str = "crudas"):
    """destino: 'crudas' => noticias.csv, 'cola' => queue_to_process.csv"""
    if rows is None or rows.empty: 
        st.warning("No hay entradas válidas para ingresar.")
        return
    for c in REQUIRED_COLS:
        if c not in rows.columns: rows[c] = ""
    if destino == "cola":
        _queue_add(rows[REQUIRED_COLS])
        st.success(f"Agregadas {len(rows)} a la cola.")
    else:
        base = _load_news(NEWS_CSV)
        merged = pd.concat([base, rows[REQUIRED_COLS]], ignore_index=True)
        if "url" in merged.columns:
            merged = merged.drop_duplicates(subset=["url"], keep="first").reset_index(drop=True)
        _save_news(merged)
        st.success(f"Agregadas {len(merged) - len(base)} noticias al acopio.")

       # ================== PARTE 2/4 — Toolbar global y navegación de Procesar ==================

def _fetch_emergent_now(window_days: int = 1, limit_each: int = 60) -> int:
    """
    Recolección inmediata (RSS + NewsAPI si hay clave), acumulativa y deduplicada.
    Devuelve el número de nuevas filas agregadas.
    """
    frames = []
    # RSS para todas las consultas
    for q in _default_queries():
        dfr = _fetch_news_rss_google(q, max_items=limit_each, days=window_days)
        if not dfr.empty: frames.append(dfr)
    # NewsAPI (si disponible)
    if _newsapi_key():
        for q in _default_queries():
            dfa = _fetch_news_newsapi(q, page_size=min(limit_each, 100), pages=2)
            if not dfa.empty: frames.append(dfa)

    if not frames:
        return 0
    extra = pd.concat(frames, ignore_index=True)
    if "url" in extra.columns:
        extra = extra.drop_duplicates(subset=["url"]).reset_index(drop=True)
    base = _load_news(NEWS_CSV)
    merged = pd.concat([base, extra], ignore_index=True)
    if "url" in merged.columns:
        merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
    _save_news(merged)
    return len(merged) - len(base)

def _target_progress(today_df: pd.DataFrame, target: int = 200) -> tuple[int, int]:
    """Retorna (n_actual, objetivo)."""
    return len(today_df), target

def _ui_toolbar_global(df_today: pd.DataFrame):
    """
    Barra superior con acopio continuo y utilidades globales.
    """
    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
    with c1:
        if st.button("🔄 Buscar emergentes ahora", use_container_width=True):
            added = _fetch_emergent_now(window_days=1, limit_each=60)
            st.success(f"Nuevas agregadas: {added}"); st.rerun()
    with c2:
        if st.button("🛰 Variedad (multi-consulta)", use_container_width=True):
            added = _fetch_emergent_now(window_days=3, limit_each=100)
            st.success(f"Variedad agregada: {added}"); st.rerun()
    with c3:
        # Backup explícito
        if st.button("📦 Backup ahora", use_container_width=True):
            path = _backup_now(_load_news(NEWS_CSV))
            st.toast(f"Backup guardado: {path.name}", icon="📦")
    with c4:
        if st.button("📥 Ver cola", use_container_width=True):
            st.session_state[NAV_KEY] = NAV_LABELS["noticias_procesar"][0]  # permanecer en noticias
            st.session_state["_show_queue"] = True
            st.rerun()
    with c5:
        if st.button("🗑️ Papelera", use_container_width=True):
            _router_go("noticias_papelera")

    # Progreso hacia el objetivo diario
    n, goal = _target_progress(df_today, target=200)
    st.caption(f"🎯 Progreso del día: **{n}/{goal}** crudas")

# ---- Reemplazo seguro de _ui_procesar (Función 18) ----
def _ui_procesar():
    st.subheader("⚙️ Procesar / Analizar noticias (in-app)")
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("🔤 Abrir Gematría", use_container_width=True):
            _router_go("gematria")
    with c2:
        if st.button("🌀 Abrir Subliminal", use_container_width=True):
            _router_go("subliminal")
    with c3:
        if st.button("📥 Ver cola (pendientes)", use_container_width=True):
            st.session_state["_show_queue"] = True
            st.rerun()
    st.caption("Sugerencia: pasa a análisis solo las noticias filtradas (alto impacto).")

    if st.session_state.get("_show_queue"):
        _ui_queue()

# ================== PARTE 3/4 — Vistas numeradas + acciones + explorador + pegar ==================

def _ui_crudas_v2(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("🗞️ Noticias crudas (primarias)")
    if df.empty:
        st.info("No hay noticias crudas para mostrar.")
        return df
    dff = df.sort_values(["fecha", "fuente", "titular"], ascending=[False, True, True]).reset_index(drop=True)
    dff = _enumerate_df(dff)
    st.caption(f"Total crudas visibles: **{len(dff)}**")
    st.dataframe(dff[["#", "fecha","fuente","titular","url","etiquetas"]], use_container_width=True, hide_index=True)

    # Acciones por lote
    ids = st.multiselect("Selecciona id_noticia para acciones", options=df["id_noticia"].tolist())
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📤 Enviar a Cola (Gematría/Subliminal)", use_container_width=True, disabled=not ids):
            _queue_add(df[df["id_noticia"].isin(ids)])
            st.success(f"Enviadas {len(ids)} a la cola."); st.rerun()
    with c2:
        if st.button("🗑️ Mover a Papelera", use_container_width=True, disabled=not ids):
            cleaned = _move_to_trash(df, ids)
            st.success(f"Movidas {len(ids)} a papelera."); st.rerun()
    with c3:
        st.download_button(
            "⬇️ Descargar crudas (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_crudas_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv", use_container_width=True,
        )
    return df

def _ui_filtradas_v2(df: pd.DataFrame) -> pd.DataFrame:
    st.subheader("🔥 Noticias filtradas (alto impacto)")
    colU, colW = st.columns(2)
    with colU:
        umbral = st.slider("Umbral emoción final", 0, 100, 60)
    with colW:
        alto = st.multiselect("Palabras de alto impacto", PALABRAS_ALTO_IMPACTO_DEFAULT, default=PALABRAS_ALTO_IMPACTO_DEFAULT[:10])

    if df.empty:
        st.info("No hay noticias para filtrar.")
        return pd.DataFrame()

    enriched = []
    for _, r in df.iterrows():
        text = f"{r.get('titular','')} {r.get('resumen','')}"
        emo_lex, score_lex = _lexicon_score(text)
        nlp = _nlp_backend(text)
        score_model = nlp["modelo"] if nlp else None
        final = _final_score(score_lex, score_model)
        cats = _categorize(text)
        hit = _high_impact_hit(text, alto)
        motivo = (
            f"Incluida: emoción={final}≥{umbral} + alto impacto" if (final >= umbral and hit) else
            f"Incluida: emoción={final}≥{umbral}" if (final >= umbral) else
            f"Incluida: alto impacto (emocion={final}<{umbral})" if hit else
            f"Excluida: emoción={final}<{umbral} sin alto impacto"
        )
        enriched.append({
            **r.to_dict(),
            "emocion_dominante": (nlp["emocion"] if (nlp and nlp.get("emocion")) else emo_lex),
            "nivel_emocional_lexicon": score_lex,
            "nivel_emocional_modelo": (score_model if score_model is not None else ""),
            "nivel_emocional_final": final,
            "categorias_emocionales": ";".join(sorted(set(cats))) if cats else "",
            "motivo_filtrado": motivo,
            "es_alto_impacto": motivo.startswith("Incluida"),
        })

    dff = pd.DataFrame(enriched)
    ok = dff[dff["es_alto_impacto"] == True].copy()  # noqa: E712
    ok = ok.sort_values(["fecha","fuente","titular"], ascending=[False, True, True]).reset_index(drop=True)
    ok = _enumerate_df(ok)
    st.caption(f"Seleccionadas: **{len(ok)}** / {len(dff)}")
    st.dataframe(
        ok[["#", "fecha","fuente","titular","nivel_emocional_final","categorias_emocionales","motivo_filtrado","url"]],
        use_container_width=True, hide_index=True
    )

    ids = st.multiselect("Selecciona id_noticia (filtradas) para acciones", options=ok["id_noticia"].tolist())
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📤 Enviar a Cola", use_container_width=True, disabled=not ids):
            _queue_add(ok[ok["id_noticia"].isin(ids)])
            st.success(f"Enviadas {len(ids)} a la cola."); st.rerun()
    with c2:
        if st.button("🔤 Ir a Gematría", use_container_width=True, disabled=not ids):
            _queue_add(ok[ok["id_noticia"].isin(ids)]); _router_go("gematria")
    with c3:
        if st.button("🌀 Ir a Subliminal", use_container_width=True, disabled=not ids):
            _queue_add(ok[ok["id_noticia"].isin(ids)]); _router_go("subliminal")
    with c4:
        if st.button("🗑️ Mover a Papelera", use_container_width=True, disabled=not ids):
            base = _load_news(NEWS_CSV)
            cleaned = _move_to_trash(base, ids)
            st.success(f"Movidas {len(ids)} a papelera."); st.rerun()
    return ok

def _ui_explorador_v2(df: pd.DataFrame):
    st.subheader("🔎 Explorador / Ingreso")
    st.caption("Trae más noticias desde varias fuentes o agrega manualmente. Todo se queda en la app.")
    fuente = st.selectbox("Fuente", ["Google News (RSS)", "NewsAPI"], index=0)
    q = st.text_input("Consulta (amplia)", _default_query())
    n = st.slider("Cantidad a traer por consulta", 20, 100, 60, step=10)
    window = st.selectbox("Ventana temporal", ["24h","48h","72h"], index=0)
    days = {"24h":1, "48h":2, "72h":3}[window]

    c1, c2 = st.columns(2)
    with c1:
        if st.button("📥 Traer noticias", use_container_width=True):
            extra = _fetch_news_rss_google(q, max_items=int(n), days=days) if fuente == "Google News (RSS)" else _fetch_news_newsapi(q, page_size=int(n), pages=2)
            if extra is None or extra.empty:
                st.warning("No se trajo nada (prueba otra consulta/fuente).")
            else:
                merged = pd.concat([df, extra], ignore_index=True)
                if "url" in merged.columns: merged = merged.drop_duplicates(subset=["url"]).reset_index(drop=True)
                _save_news(merged); st.success(f"+{len(merged)-len(df)} noticias nuevas."); st.rerun()
    with c2:
        if st.button("🛰 Traer variedad (multi-consulta)", use_container_width=True):
            added = _fetch_emergent_now(window_days=days, limit_each=100)
            st.success(f"Variedad agregada: {added}"); st.rerun()

    st.markdown("---")
    st.markdown("### ✍️ Pegar noticias manuales (una por línea)")
    raw = st.text_area("Pega aquí (formato: título | resumen | fuente | url, o 'título — resumen')", height=160)
    colp1, colp2, colp3 = st.columns([1,1,1])
    with colp1:
        if st.button("➕ Ingresar a Crudas", use_container_width=True, disabled=not raw.strip()):
            rows = _manual_paste_parse(raw); _ingest_manual(rows, destino="crudas"); st.rerun()
    with colp2:
        if st.button("📤 Ingresar a Cola (procesar)", use_container_width=True, disabled=not raw.strip()):
            rows = _manual_paste_parse(raw); _ingest_manual(rows, destino="cola"); st.rerun()
    with colp3:
        st.download_button(
            "⬇️ Descargar noticias actuales (CSV)",
            df.to_csv(index=False).encode("utf-8"),
            file_name=f"noticias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv",
            mime="text/csv", use_container_width=True,
        )
# ================== PARTE 4/4 — Render principal + main ==================

def render_noticias():
    st.header("📰 Noticias — Filtro emocional PRO")

    # Acopio continuo: no bloquea la UI; lo manual está en toolbar
    # Carga base y filtro “del día” para progreso
    df_all = _load_news(NEWS_CSV)
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    df_today = df_all[df_all["fecha"].astype(str) == today_str]

    # Toolbar global (emergentes, variedad, backup, cola, papelera) + progreso 200
    _ui_toolbar_global(df_today)

    # Mini-menú estable (radio)
    vista = st.radio(
        "Vista",
        [NAV_LABELS["noticias_crudas"][0],
         NAV_LABELS["noticias_filtradas"][0],
         NAV_LABELS["noticias_procesar"][0],
         NAV_LABELS["noticias_explorar"][0],
         NAV_LABELS["noticias_papelera"][0],
         NAV_LABELS["noticias_limpiar"][0]],
        horizontal=True
    )

    # Filtros rápidos (fecha / sorteo / búsqueda)
    colf1, colf2, colf3 = st.columns([1, 1, 2])
    fechas = ["(todas)"] + sorted([f for f in df_all.get("fecha", pd.Series(dtype=str)).unique() if str(f).strip()])
    sorteos = ["(todos)"] + sorted([s for s in df_all.get("sorteo", pd.Series(dtype=str)).unique() if str(s).strip()])
    fsel = colf1.selectbox("Fecha", options=fechas, index=0)
    ssel = colf2.selectbox("Sorteo (opcional)", options=sorteos, index=0)
    q = colf3.text_input("Buscar (titular / resumen / etiquetas)")

    base = df_all.copy()
    if fsel != "(todas)": base = base[base["fecha"].astype(str) == fsel]
    if ssel != "(todos)": base = base[base["sorteo"].astype(str) == ssel]
    if q.strip():
        qn = q.lower().strip()
        base = base[
            base["titular"].astype(str).str.lower().str.contains(qn, na=False) |
            base["resumen"].astype(str).str.lower().str.contains(qn, na=False) |
            base["etiquetas"].astype(str).str.lower().str.contains(qn, na=False)
        ]

    # Métricas
    colM1, colM2 = st.columns(2)
    with colM1: st.metric("📰 Crudas (vista actual)", len(base))
    with colM2: st.metric("⏱️ Última acción", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))

    # Rutas de navegación de la vista
    if vista in NAV_LABELS["noticias_crudas"]:
        _ui_crudas_v2(base)

    elif vista in NAV_LABELS["noticias_filtradas"]:
        _ui_filtradas_v2(base)

    elif vista in NAV_LABELS["noticias_procesar"]:
        _ui_procesar()
        if st.session_state.get("_show_queue"):  # mostrar cola si se pidió desde toolbar o procesar
            _ui_queue()

    elif vista in NAV_LABELS["noticias_explorar"]:
        _ui_explorador_v2(df_all)

    elif vista in NAV_LABELS["noticias_papelera"]:
        _ui_papelera()

    elif vista in NAV_LABELS["noticias_limpiar"]:
        # Reusa tu _ui_limpiar existente (si ya estaba definido)
        try:
            _ui_limpiar(df_all)
        except Exception:
            st.info("Vista de limpieza no disponible en esta versión.")

# Shims de conveniencia
def render():
    """Mantiene compatibilidad si app.py llama a render() en lugar de render_noticias()."""
    render_noticias()

def main():
    render_noticias()

if __name__ == "__main__":
    main()
