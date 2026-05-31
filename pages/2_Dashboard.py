import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(page_title="ATLAS Admin Dashboard", layout="wide")

st.title("📊 ATLAS - Panel Administrativo")

# =====================================================
# RUTA DATOS
# =====================================================

RUTA_CSV = "data/reportes.csv"

# =====================================================
# VALIDACIÓN DE ARCHIVO
# =====================================================

if not os.path.exists(RUTA_CSV):
    st.error("No existe el archivo de reportes")
    st.stop()

df = pd.read_csv(RUTA_CSV)
df.columns = df.columns.str.strip()

# =====================================================
# 🔥 BLINDAJE DE COLUMNAS (CRÍTICO)
# =====================================================

columnas_base = [
    "ID","Folio","FechaCreacion","TipoUsuario","Nombre","Correo",
    "Edificio","Area","UbicacionDetalle","Activo","Categoria",
    "Prioridad","Descripcion","Impacto","Estado",
    "Responsable","FechaActualizacion","Imagen"
]

for col in columnas_base:
    if col not in df.columns:
        df[col] = "Sin dato"

# =====================================================
# SIDEBAR - FILTROS
# =====================================================

st.sidebar.header("🔎 Filtros")

estado_filtro = st.sidebar.multiselect(
    "Estado",
    df["Estado"].unique(),
    default=df["Estado"].unique()
)

prioridad_filtro = st.sidebar.multiselect(
    "Prioridad",
    df["Prioridad"].unique(),
    default=df["Prioridad"].unique()
)

edificio_filtro = st.sidebar.multiselect(
    "Edificio",
    df["Edificio"].unique(),
    default=df["Edificio"].unique()
)

df = df[
    (df["Estado"].isin(estado_filtro)) &
    (df["Prioridad"].isin(prioridad_filtro)) &
    (df["Edificio"].isin(edificio_filtro))
]

# =====================================================
# KPIs PRINCIPALES
# =====================================================

st.subheader("📌 Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total tickets", len(df))
col2.metric("Pendientes", len(df[df["Estado"] == "Pendiente"]))
col3.metric("En proceso", len(df[df["Estado"] == "En proceso"]))
col4.metric("Completados", len(df[df["Estado"] == "Completado"]))

st.divider()

# =====================================================
# GRÁFICOS
# =====================================================

colA, colB = st.columns(2)

with colA:

    st.subheader("📊 Tickets por estado")

    estado_counts = (
        df.groupby("Estado")
        .size()
        .reset_index(name="Cantidad")
    )

    fig1 = px.bar(
        estado_counts,
        x="Estado",
        y="Cantidad",
        text="Cantidad",
        title="Tickets por estado"
    )

    st.plotly_chart(fig1, use_container_width=True)

with colB:

    st.subheader("📊 Tickets por prioridad")

    fig2 = px.pie(
        df,
        names="Prioridad"
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# =====================================================
# TABLA GENERAL
# =====================================================

st.subheader("📋 Todos los tickets")

st.dataframe(
    df.sort_values(by="FechaCreacion", ascending=False),
    use_container_width=True
)
