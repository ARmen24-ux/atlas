import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(page_title="ATLAS Dashboard", layout="wide")
st.title("📊 ATLAS - Panel de Gestión de Mantenimiento")

# =====================================================
# PROTECCIÓN DE ACCESO
# =====================================================

if "rol" not in st.session_state:
    st.warning("Acceso restringido. Inicia sesión.")
    st.stop()

rol = st.session_state.rol

if rol not in ["admin", "mantenimiento"]:
    st.error("No tienes permisos para este panel.")
    st.stop()

# =====================================================
# RUTA CSV
# =====================================================

RUTA_CSV = "data/reportes.csv"

if not os.path.exists(RUTA_CSV):
    st.error("No existe el archivo de reportes")
    st.stop()

df = pd.read_csv(RUTA_CSV)
df.columns = df.columns.str.strip()

# =====================================================
# BLINDAJE DE COLUMNAS
# =====================================================

columnas_base = [
    "ID","Fecha","TipoUsuario","Nombre","Correo",
    "Edificio","Area","Categoria","Impacto",
    "Descripcion","Estado","Prioridad","Responsable"
]

for col in columnas_base:
    if col not in df.columns:
        df[col] = "Sin dato"

# =====================================================
# FLUJO DE ESTADOS (ATLAS)
# =====================================================

TRANSICIONES = {
    "Pendiente": ["Validado", "Rechazado"],
    "Validado": ["Asignado", "Rechazado"],
    "Asignado": ["En proceso"],
    "En proceso": ["Resuelto"],
    "Resuelto": ["Cerrado"]
}

# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("🔎 Filtros")

estado_filtro = st.sidebar.multiselect(
    "Estado",
    df["Estado"].unique(),
    default=df["Estado"].unique()
)

df = df[df["Estado"].isin(estado_filtro)]

# =====================================================
# KPIs
# =====================================================

st.subheader("📌 Indicadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", len(df))
col2.metric("Pendientes", len(df[df["Estado"] == "Pendiente"]))
col3.metric("En proceso", len(df[df["Estado"] == "En proceso"]))
col4.metric("Resueltos", len(df[df["Estado"] == "Resuelto"]))

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
        title="Distribución por estado"
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

estado_actual = ticket["Estado"]

opciones_validas = TRANSICIONES.get(estado_actual, [])

if len(opciones_validas) == 0:
    st.info("Este ticket no puede cambiar de estado")
    nuevo_estado = estado_actual
else:
    nuevo_estado = st.selectbox(
        "Nuevo estado",
        opciones_validas
    )

responsable = st.text_input("Responsable (opcional)", value=ticket.get("Responsable", ""))

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
    df.sort_values(by="Fecha", ascending=False),
    use_container_width=True
)