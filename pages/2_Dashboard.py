import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

st.title("📊 Dashboard de Mantenimiento")

st.write(
    "Panel general para monitorear el estado de las incidencias."
)

# =====================================================
# RUTA CSV
# =====================================================

RUTA_CSV = os.path.join("data", "reportes.csv")

# =====================================================
# VALIDAR EXISTENCIA
# =====================================================

if not os.path.exists(RUTA_CSV):

    st.warning("No existe la base de datos de reportes.")
    st.stop()

# =====================================================
# LEER CSV
# =====================================================

df = pd.read_csv(RUTA_CSV)

if df.empty:

    st.info("No existen reportes registrados.")
    st.stop()

# =====================================================
# ASEGURAR COLUMNAS
# =====================================================

if "Estado" not in df.columns:
    df["Estado"] = "Pendiente"

# =====================================================
# INDICADORES
# =====================================================

total_reportes = len(df)

pendientes = len(
    df[df["Estado"] == "Pendiente"]
)

en_proceso = len(
    df[df["Estado"] == "En proceso"]
)

resueltos = len(
    df[df["Estado"] == "Resuelto"]
)

# =====================================================
# MÉTRICAS
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Reportes",
        total_reportes
    )

with col2:
    st.metric(
        "Pendientes",
        pendientes
    )

with col3:
    st.metric(
        "En Proceso",
        en_proceso
    )

with col4:
    st.metric(
        "Resueltos",
        resueltos
    )

st.divider()

# =====================================================
# DISTRIBUCIÓN POR ESTADO
# =====================================================

st.subheader("Reportes por estado")

conteo_estados = (
    df["Estado"]
    .value_counts()
    .reset_index()
)

conteo_estados.columns = [
    "Estado",
    "Cantidad"
]

st.bar_chart(
    conteo_estados.set_index("Estado")
)

st.divider()

# =====================================================
# ÚLTIMOS REPORTES
# =====================================================

st.subheader("Últimos reportes registrados")

columnas_mostrar = []

for columna in [
    "ID",
    "Fecha",
    "Area",
    "Problema",
    "Estado"
]:
    if columna in df.columns:
        columnas_mostrar.append(columna)

st.dataframe(
    df[columnas_mostrar].tail(10),
    width="stretch",
    hide_index=True
)
