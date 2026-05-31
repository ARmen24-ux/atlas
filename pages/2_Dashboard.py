import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(page_title="ATLAS Dashboard", layout="wide")
st.title("📊 Dashboard ATLAS")

# =====================================================
# CARGA DE DATOS
# =====================================================

ruta = "data/reportes.csv"

if not os.path.exists(ruta):
    st.warning("No hay datos registrados aún.")
    st.stop()

df = pd.read_csv(ruta)

# LIMPIEZA DE COLUMNAS (OBLIGATORIO)
df.columns = df.columns.str.strip()

# =====================================================
# NORMALIZACIÓN DEFENSIVA
# =====================================================

for c in ["Edificio", "Activo", "Categoria", "Impacto", "Estado"]:
    if c not in df.columns:
        df[c] = "Sin dato"

# =====================================================
# MÉTRICA GENERAL
# =====================================================

st.metric("Total de reportes", len(df))

# =====================================================
# FILTRO
# =====================================================

edificio = st.selectbox(
    "Filtrar por edificio",
    ["Todos"] + list(df["Edificio"].unique())
)

if edificio != "Todos":
    df = df[df["Edificio"] == edificio]

st.divider()

# =====================================================
# 🔥 GRÁFICO 1: ACTIVOS (CORREGIDO)
# =====================================================

st.subheader("🔧 Reportes por activo")

activos = df["Activo"].value_counts().reset_index()
activos.columns = ["Activo", "Total"]

fig1 = px.bar(
    activos,
    x="Activo",
    y="Total",
    text="Total"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================================
# ⚙️ GRÁFICO 2: CATEGORÍA
# =====================================================

st.subheader("⚙️ Por categoría")

cat = df["Categoria"].value_counts().reset_index()
cat.columns = ["Categoria", "Total"]

fig2 = px.pie(
    cat,
    names="Categoria",
    values="Total"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 🚨 GRÁFICO 3: IMPACTO
# =====================================================

st.subheader("🚨 Impacto")

imp = df["Impacto"].value_counts().reset_index()
imp.columns = ["Impacto", "Total"]

fig3 = px.bar(
    imp,
    x="Impacto",
    y="Total",
    text="Total"
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# 📋 TABLA FINAL
# =====================================================

st.subheader("📋 Últimos reportes")

st.dataframe(
    df.sort_values("Fecha", ascending=False).head(20),
    use_container_width=True
)

from utils.data_guard import asegurar_esquema

df = asegurar_esquema(df)
