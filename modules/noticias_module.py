def render_noticias():
    st.subheader("📰 Acopio de noticias (Emoción social — EE. UU.)")
    st.caption(f"Última recarga: {_now_utc_str()}")

    # ---------- Acciones diferidas (previas al render) ----------
    if _consume_flag("__force_reacopio__"):
        st.cache_data.clear()
        # seguimos; el layout aún no existe en este ciclo

    if _consume_flag("__show_trash__"):
        st.session_state["__show_trash_mode__"] = True
    if _consume_flag("__hide_trash__"):
        st.session_state["__show_trash_mode__"] = False

    # ---------- Sidebar (estructura fija) ----------
    with st.sidebar:
        st.markdown("#### Noticias · Acciones")
        if st.button("↻ Reacopiar ahora", use_container_width=True, key="btn_reacopiar_now"):
            _flag("__force_reacopio__")
            st.stop()  # corta el render y evita mezclar creación/elim de nodos

        # --- Descargas SIEMPRE visibles (habilitar/deshabilitar) ---
        st.markdown("#### Descargas")
        cdl, cdr = st.columns(2)

        raw_exists = RAW_LAST.exists()
        sel_exists = SEL_LAST.exists()
        raw_bytes = RAW_LAST.read_bytes() if raw_exists else b""
        sel_bytes = SEL_LAST.read_bytes() if sel_exists else b""

        with cdl:
            st.download_button(
                "Acopio bruto",
                data=raw_bytes,
                file_name="acopio_bruto_ultimo.csv",
                use_container_width=True,
                key="dl_raw_last",
                disabled=not raw_exists
            )
        with cdr:
            st.download_button(
                "Selección ES",
                data=sel_bytes,
                file_name="seleccion_es_ultima.csv",
                use_container_width=True,
                key="dl_sel_last",
                disabled=not sel_exists
            )

        # --- Envíos a buffers ---
        st.markdown("#### Enviar selección a")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔡 GEM", use_container_width=True, key="send_gem_btn"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "GEM")
                    st.toast(f"GEMATRÍA: {p.name if p else 'sin datos'}", icon="✅")
        with c2:
            if st.button("🌀 SUB", use_container_width=True, key="send_sub_btn"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    p = _export_buffer(sel, "SUB")
                    st.toast(f"SUBLIMINAL: {p.name if p else 'sin datos'}", icon="✅")
        with c3:
            if st.button("📊 T70", use_container_width=True, key="send_t70_btn"):
                sel = st.session_state.get("news_selected_df", pd.DataFrame())
                if not sel.empty:
                    sel2 = sel.copy()
                    if "categorias_t70_ref" in sel2.columns:
                        sel2["T70_map"] = sel2["categorias_t70_ref"].map(_map_news_to_t70)
                    p = _export_buffer(sel2, "T70")
                    st.toast(f"T70: {p.name if p else 'sin datos'}", icon="✅")

        # --- Bitácora por sorteo ---
        st.markdown("#### Bitácora por sorteo")
        current_lottery = st.session_state.get("current_lottery", "GENERAL")
        if st.button("Guardar selección en bitácora", use_container_width=True, key="save_ledger_btn"):
            sel = st.session_state.get("news_selected_df", pd.DataFrame())
            if not sel.empty:
                sel2 = sel.copy()
                sel2["sorteo_aplicado"] = current_lottery
                p = _save_ledger(sel2, current_lottery)
                _save_csv(sel2, SEL_LAST)  # snapshot
                st.toast(f"Bitácora guardada: {p.name}", icon="🗂️")

        # --- Papelera: controles de visibilidad (no crean/borrran nodos) ---
        st.markdown("#### Papelera")
        cpa, cpb = st.columns(2)
        with cpa:
            if st.button("Ver", use_container_width=True, key="show_trash_btn"):
                _flag("__show_trash__"); st.stop()
        with cpb:
            if st.button("Ocultar", use_container_width=True, key="hide_trash_btn"):
                _flag("__hide_trash__"); st.stop()

    # ---------- Acopio (cacheado) ----------
    @st.cache_data(show_spinner=True)
    def _run_acopio() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
        df_raw, logs = _fetch_all_sources()
        if df_raw.empty:
            return df_raw, df_raw, logs

        df = _score_emocion_social(df_raw)
        if CFG["SEMANTIC_ON"]:
            df = _semantic_dedup(df, CFG["SEMANTIC_THR"])
        if CFG["SOFT_DEDUP_NORM"]:
            df = _soft_dedup(df)
        df = _limit_per_source(df, CFG["MAX_PER_SOURCE"])
        df = df.sort_values(by=["_score_es", "fecha_dt"], ascending=[False, False]).reset_index(drop=True)

        _save_csv(df_raw, RAW_LAST)
        _save_csv(df, SEL_LAST)
        return df_raw, df, logs

    df_raw, df_sel, logs = _run_acopio()
    st.session_state["news_selected_df"] = df_sel.copy()

    # ---------- Encabezado de estado (estructura fija) ----------
    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Fuentes", f"{len(logs.get('sources', []))}")
    s2.metric("Candidatas (bruto)", f"{len(df_raw)}")
    s3.metric("Seleccionadas", f"{len(df_sel)}")
    s4.metric("Ventana (h)", f"{CFG['RECENCY_HOURS']}")
    s5.metric("Tiempo (s)", f"{logs.get('elapsed_sec', 0)}")

    # ---------- Mini-menú de selección múltiple (estable) ----------
    st.markdown("##### Acciones sobre selección")
    sel_ids = st.multiselect(
        "Selecciona ID(s) de noticia:",
        options=df_sel["id_noticia"].tolist(),
        key="news_sel_ids",
        label_visibility="collapsed"
    )

    b1, b2, b3, b4, b5 = st.columns(5)
    with b1:
        if st.button("📋 Copiar seleccionadas", key="copy_sel_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)][["titular","url","resumen"]]
            payload = "\n\n".join([f"• {r.titular}\n{r.url}\n{r.resumen}" for r in subset.itertuples()])
            st.code(payload)

    with b2:
        if st.button("🗑️ Cortar a Papelera", key="to_trash_btn"):
            to_trash = df_sel[df_sel["id_noticia"].isin(sel_ids)]
            if not to_trash.empty:
                _append_trash(to_trash, reason="manual_batch")
                st.toast(f"Enviadas a papelera: {len(to_trash)}", icon="🗑️")

    with b3:
        if st.button("🔡 → GEMATRÍA", key="to_gem_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)]
            p = _export_buffer(subset, "GEM") if not subset.empty else None
            st.toast(f"Batch a GEMATRÍA: {p.name if p else 'sin datos'}", icon="✅")

    with b4:
        if st.button("🌀 → SUBLIMINAL", key="to_sub_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)]
            p = _export_buffer(subset, "SUB") if not subset.empty else None
            st.toast(f"Batch a SUBLIMINAL: {p.name if p else 'sin datos'}", icon="✅")

    with b5:
        if st.button("📊 → T70", key="to_t70_btn"):
            subset = df_sel[df_sel["id_noticia"].isin(sel_ids)].copy()
            if not subset.empty and "categorias_t70_ref" in subset.columns:
                subset["T70_map"] = subset["categorias_t70_ref"].map(_map_news_to_t70)
            p = _export_buffer(subset, "T70") if not subset.empty else None
            st.toast(f"Batch a T70: {p.name if p else 'sin datos'}", icon="✅")

    # ---------- Tablas (estructura estable) ----------
    st.markdown("###### Selección actual (ordenada por score y fecha)")
    st.dataframe(
        df_sel[[
            c for c in ["id_noticia","fecha_dt","fuente","titular","_score_es"]
            if c in df_sel.columns
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("###### Log de fuentes")
    log_df = pd.DataFrame(logs.get("sources", []))
    if not log_df.empty:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
    else:
        st.caption("Sin logs de fuentes.")

    # ---------- Papelera (vista opcional con slot fijo) ----------
    with st.session_state["__trash_slot"].container():
        if st.session_state.get("__show_trash_mode__", False):
            st.markdown("#### Papelera")
            trash_df = _load_trash()
            if trash_df.empty:
                st.info("Papelera vacía por ahora.")
            else:
                st.dataframe(trash_df, use_container_width=True, hide_index=True)
        else:
            st.caption("Papelera oculta.")   
