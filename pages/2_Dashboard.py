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

    fig1 = px.bar(
        df["Estado"].value_counts().reset_index(),
        x="index",
        y="Estado",
        labels={"index":"Estado","Estado":"Cantidad"}
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
# GESTIÓN DE TICKETS
# =====================================================

st.subheader("🛠 Gestión de tickets")

ticket_id = st.selectbox("Selecciona ticket (ID)", df["ID"])

ticket = df[df["ID"] == ticket_id].iloc[0]

st.write("### Información del ticket")
st.write(ticket)

nuevo_estado = st.selectbox(
    "Cambiar estado",
    ["Pendiente","En revisión","Asignado","En proceso","Completado","Cancelado"],
    index=0
)

responsable = st.text_input("Responsable (opcional)")

if st.button("Actualizar ticket"):

    df.loc[df["ID"] == ticket_id, "Estado"] = nuevo_estado
    df.loc[df["ID"] == ticket_id, "Responsable"] = responsable
    df.loc[df["ID"] == ticket_id, "FechaActualizacion"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    df.to_csv(RUTA_CSV, index=False)

    st.success("Ticket actualizado correctamente")
    st.rerun()

st.divider()

# =====================================================
# TABLA GENERAL
# =====================================================

st.subheader("📋 Todos los tickets")

st.dataframe(
    df.sort_values(by="FechaCreacion", ascending=False),
    use_container_width=True
)
