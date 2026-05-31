import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Dashboard ATLAS",
    layout="wide"
)

st.title("📊 Dashboard de mantenimiento ATLAS")

# =====================================================
# RUTA DE DATOS
# =====================================================

RUTA_CSV = os.path.join("data", "reportes.csv")

if not os.path.exists(RUTA_CSV):
    st.warning("No hay datos aún.")
    st.stop()

# =====================================================
# CARGA DE DATOS
# =====================================================

df = pd.read_csv(RUTA_CSV)

# LIMPIEZA CRÍTICA (EVITA TU ERROR)
df.columns = df.columns.str.strip()

# =====================================================
# VALIDACIÓN DE COLUMNAS
# =====================================================

columnas_necesarias = [
    "Edificio", "Area", "Activo",
    "Categoria", "Impacto", "Estado"
]

for col in columnas_necesarias:
    if col not in df.columns:
        st.error(f"Falta la columna en el CSV: {col}")
        st.stop()

# =====================================================
# LIMPIEZA DE NULOS
# =====================================================

df["Edificio"] = df["Edificio"].fillna("Sin dato")
df["Area"] = df["Area"].fillna("Sin dato")
df["Activo"] = df["Activo"].fillna("Sin dato")
df["Categoria"] = df["Categoria"].fillna("Sin dato")
df["Impacto"] = df["Impacto"].fillna("Sin dato")
df["Estado"] = df["Estado"].fillna("Sin dato")

# =====================================================
# MÉTRICAS GENERALES
# =====================================================

st.subheader("📌 Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de reportes", len(df))

col2.metric(
    "Pendientes",
    len(df[df["Estado"] == "Pendiente"])
)

col3.metric(
    "Críticos",
    len(df[df["Impacto"] == "Impide realizar actividades"])
)

col4.metric(
    "Activos únicos afectados",
    df["Activo"].nunique()
)

st.divider()

# =====================================================
# FILTROS
# =====================================================

st.subheader("🔎 Filtros")

col_f1, col_f2 = st.columns(2)

with col_f1:
    edificio_sel = st.selectbox(
        "Filtrar por edificio",
        ["Todos"] + list(df["Edificio"].unique())
    )

with col_f2:
    estado_sel = st.selectbox(
        "Filtrar por estado",
        ["Todos"] + list(df["Estado"].unique())
    )

# Aplicar filtros
df_filtrado = df.copy()

if edificio_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Edificio"] == edificio_sel]

if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_sel]

st.divider()

# =====================================================
# GRÁFICO 1: POR ACTIVO
# =====================================================

st.subheader("🔧 Reportes por activo")

activos = df_filtrado["Activo"].value_counts().reset_index()
activos.columns = ["Activo", "Reportes"]

fig1 = px.bar(
    activos,
    x="Activo",
    y="Reportes",
    text="Reportes"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================================
# GRÁFICO 2: POR EDIFICIO
# =====================================================

st.subheader("🏢 Reportes por edificio")

edificios = df_filtrado["Edificio"].value_counts().reset_index()
edificios.columns = ["Edificio", "Reportes"]

fig2 = px.bar(
    edificios,
    x="Edificio",
    y="Reportes",
    text="Reportes"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# GRÁFICO 3: POR CATEGORÍA
# =====================================================

st.subheader("⚙️ Reportes por categoría")

categoria = df_filtrado["Categoria"].value_counts().reset_index()
categoria.columns = ["Categoria", "Reportes"]

fig3 = px.pie(
    categoria,
    names="Categoria",
    values="Reportes"
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# GRÁFICO 4: IMPACTO
# =====================================================

st.subheader("🚨 Impacto de los reportes")

impacto = df_filtrado["Impacto"].value_counts().reset_index()
impacto.columns = ["Impacto", "Reportes"]

fig4 = px.bar(
    impacto,
    x="Impacto",
    y="Reportes",
    text="Reportes"
)

st.plotly_chart(fig4, use_container_width=True)

# =====================================================
# TABLA FINAL
# =====================================================

st.subheader("📋 Últimos reportes")

st.dataframe(
    df_filtrado.sort_values("Fecha", ascending=False).head(20),
    use_container_width=True
)
