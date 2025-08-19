import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Visión", page_icon="🔮", layout="wide")
st.title("🔮 Sistema Predictivo Visión")

menu = st.sidebar.selectbox(
    "Selecciona un módulo:",
    ["Inicio", "Tabla T70", "Noticias (Filtro Emocional)"]
)

# ========= Inicio =========
if menu == "Inicio":
    st.write("Bienvenido. Usa el menú lateral para navegar por los módulos.")

# ========= T70 =========
elif menu == "Tabla T70":
    st.subheader("📊 Tabla T70 (referencia)")
    try:
        df_t70 = pd.read_csv("T70.csv", encoding="utf-8")
        st.dataframe(df_t70, hide_index=True, use_container_width=True)
    except Exception as e:
        st.error(f"No se pudo cargar T70.csv: {e}")
        st.info("Asegura que T70.csv exista en la raíz del repositorio.")

# ========= Noticias (Filtro Emocional) =========
elif menu == "Noticias (Filtro Emocional)":
    st.subheader("🗞️ Noticias — Filtro Emocional/Social")

    cols_esperadas = [
        "id_noticia","fecha","sorteo","pais","fuente","titular","resumen",
        "etiquetas","nivel_emocional_diccionario","nivel_emocional_modelo",
        "nivel_emocional_final","noticia_relevante","categorias_t70_ref"
    ]

    # Cargar CSV
    try:
        df = pd.read_csv("noticias.csv", encoding="utf-8")
    except FileNotFoundError:
        st.warning("Falta noticias.csv. Crea el archivo con la cabecera canónica de 13 columnas.")
        st.code(",".join(cols_esperadas), language="text")
        st.stop()
    except Exception as e:
        st.error(f"No se pudo leer noticias.csv: {e}")
        st.stop()

    # Completar columnas faltantes y ordenar
    for c in cols_esperadas:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[cols_esperadas].copy()

    # Normalizaciones
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    for c in ["nivel_emocional_diccionario","nivel_emocional_modelo","nivel_emocional_final"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # calcular final si falta
    mask_nan = df["nivel_emocional_final"].isna()
    df.loc[mask_nan, "nivel_emocional_final"] = (
        df.loc[mask_nan, "nivel_emocional_diccionario"].fillna(0) +
        df.loc[mask_nan, "nivel_emocional_modelo"].fillna(0)
    ) / 2
    # booleano
    df["noticia_relevante"] = (
        df["noticia_relevante"].astype(str).str.strip().str.lower()
        .isin(["true","1","sí","si","y","yes"])
    )

    # ----- Filtros -----
    c1, c2, c3 = st.columns([1,1,2], gap="large")
    with c1:
        sorteos = ["(Todos)"] + sorted([s for s in df["sorteo"].dropna().unique()])
        sel_sorteo = st.selectbox("Sorteo", sorteos)
    with c2:
        paises = ["(Todos)"] + sorted([p for p in df["pais"].dropna().unique()])
        sel_pais = st.selectbox("País", paises)
    with c3:
        texto = st.text_input("Buscar en titular / resumen / etiquetas", "")

    fechas = sorted([f for f in df["fecha"].dropna().unique()])
    usar_fecha = st.checkbox("Filtrar por fecha", value=False)
    if usar_fecha and fechas:
        f_desde = st.date_input("Desde", value=fechas[0], min_value=fechas[0], max_value=fechas[-1])
        f_hasta = st.date_input("Hasta", value=fechas[-1], min_value=fechas[0], max_value=fechas[-1])
    else:
        f_desde, f_hasta = None, None

    umbral = st.slider("Umbral emocional (0–100)", 0, 100, 60)
    solo_rel = st.checkbox("Mostrar solo relevantes", value=True)

    # ----- Aplicar filtros -----
    dfv = df.copy()
    if sel_sorteo != "(Todos)":
        dfv = dfv[dfv["sorteo"] == sel_sorteo]
    if sel_pais != "(Todos)":
        dfv = dfv[dfv["pais"] == sel_pais]
    if usar_fecha and f_desde and f_hasta:
        dfv = dfv[(dfv["fecha"] >= f_desde) & (dfv["fecha"] <= f_hasta)]
    if texto.strip():
        q = texto.strip().lower()
        dfv = dfv[
            dfv[["titular","resumen","etiquetas"]].astype(str).apply(
                lambda r: any(q in x.lower() for x in r), axis=1
            )
        ]
    if solo_rel:
        dfv = dfv[dfv["noticia_relevante"] & (dfv["nivel_emocional_final"] >= umbral)]
    else:
        dfv = dfv[dfv["nivel_emocional_final"] >= umbral]

    st.caption(f"Mostrando {len(dfv)} de {len(df)} noticias")
    st.dataframe(
        dfv.sort_values(["fecha","nivel_emocional_final"], ascending=[False, False]),
        hide_index=True, use_container_width=True
    )

    # Exportación
    st.download_button(
        "⬇️ Exportar filtrado (CSV)",
        dfv.to_csv(index=False),
        "noticias_filtradas.csv",
        "text/csv"
    )

    # Plantilla de nueva fila
    st.divider()
    st.markdown("### ➕ Plantilla para agregar fila a `noticias.csv`")
    hoy = date.today().isoformat()
    nuevo_id = f"N-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    linea = (
        f"{nuevo_id},{hoy},MegaMillions,US,FuenteEjemplo,Titular ejemplo,Resumen breve,"
        f"tema1;tema2,70,80,75,True,sociedad;economia"
    )
    st.code(",".join(cols_esperadas) + "\n" + linea, language="text")
    st.info("Copia la línea y pégala al final de `noticias.csv` en GitHub (Commit).")