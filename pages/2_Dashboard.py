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
# RUTA
# =====================================================

RUTA_CSV = os.path.join("data", "reportes.csv")

if not os.path.exists(RUTA_CSV):
    st.warning("No hay datos aún.")
    st.stop()

# =====================================================
# CARGA DE DATOS
# =====================================================

df = pd.read_csv(RUTA_CSV)

# =====================================================
# LIMPIEZA ROBUSTA (CLAVE PARA TU ERROR)
# =====================================================

# quitar espacios invisibles
df.columns = df.columns.str.strip()

# normalizar nombres alternativos
df.rename(columns={
    "edificio": "Edificio",
    "EDIFICIO": "Edificio",
    "area": "Area",
    "Área": "Area",
    "activo": "Activo",
    "ACTIVO": "Activo",
    "categoria": "Categoria",
    "CATEGORIA": "Categoria",
    "impacto": "Impacto",
    "IMPACTO": "Impacto",
    "estado": "Estado",
    "ESTADO": "Estado"
}, inplace=True)

# =====================================================
# VALIDACIÓN FLEXIBLE
# =====================================================

columnas_necesarias = ["Edificio", "Area", "Activo", "Categoria", "Impacto", "Estado"]

faltantes = [col for col in columnas_necesarias if col not in df.columns]

if len(faltantes) > 0:
    st.error(f"Faltan columnas en el CSV: {faltantes}")
    st.stop()

# =====================================================
# LIMPIEZA DE NULOS
# =====================================================

for col in columnas_necesarias:
    df[col] = df[col].fillna("Sin dato")

# =====================================================
# MÉTRICAS
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
    "Activos únicos",
    df["Activo"].nunique()
)

st.divider()

# =====================================================
# FILTROS
# =====================================================

st.subheader("🔎 Filtros")

col1, col2 = st.columns(2)

with col1:
    edificio_sel = st.selectbox(
        "Edificio",
        ["Todos"] + list(df["Edificio"].unique())
    )

with col2:
    estado_sel = st.selectbox(
        "Estado",
        ["Todos"] + list(df["Estado"].unique())
    )

df_f = df.copy()

if edificio_sel != "Todos":
    df_f = df_f[df_f["Edificio"] == edificio_sel]

if estado_sel != "Todos":
    df_f = df_f[df_f["Estado"] == estado_sel]

st.divider()

# =====================================================
# GRÁFICO 1: ACTIVO
# =====================================================

st.subheader("🔧 Reportes por activo")

activos = df_f["Activo"].value_counts().reset_index()
activos.columns = ["Activo", "Reportes"]

fig1 = px.bar(
    activos,
    x="Activo",
    y="Reportes",
    text="Reportes"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================================
# GRÁFICO 2: EDIFICIO
# =====================================================

st.subheader("🏢 Reportes por edificio")

edificios = df_f["Edificio"].value_counts().reset_index()
edificios.columns = ["Edificio", "Reportes"]

fig2 = px.bar(
    edificios,
    x="Edificio",
    y="Reportes",
    text="Reportes"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# GRÁFICO 3: CATEGORÍA
# =====================================================

st.subheader("⚙️ Reportes por categoría")

cat = df_f["Categoria"].value_counts().reset_index()
cat.columns = ["Categoria", "Reportes"]

fig3 = px.pie(
    cat,
    names="Categoria",
    values="Reportes"
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# GRÁFICO 4: IMPACTO
# =====================================================

st.subheader("🚨 Impacto")

impacto = df_f["Impacto"].value_counts().reset_index()
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
    df_f.sort_values("Fecha", ascending=False).head(20),
    use_container_width=True
)
