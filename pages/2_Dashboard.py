import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

from utils.data_guard import asegurar_esquema

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="ATLAS Dashboard",
    layout="wide"
)

st.title("📊 ATLAS - Panel de Mantenimiento")

# =====================================================
# PROTECCIÓN DE ACCESO
# =====================================================

if "rol" not in st.session_state:
    st.warning("Acceso restringido")
    st.stop()

if st.session_state.rol not in ["admin", "mantenimiento"]:
    st.error("Sin permisos")
    st.stop()

# =====================================================
# RUTAS
# =====================================================

RUTA_CSV = "data/reportes.csv"

# =====================================================
# CARGA DE DATOS
# =====================================================

if not os.path.exists(RUTA_CSV):
    st.error("No existe el archivo de reportes")
    st.stop()

df = pd.read_csv(RUTA_CSV)

df = asegurar_esquema(df)

# =====================================================
# NORMALIZACIÓN
# =====================================================

df["ID"] = df["ID"].astype(str)

# =====================================================
# FLUJO DE ESTADOS
# =====================================================

TRANSICIONES = {
    "Pendiente": ["Validado", "Rechazado"],
    "Validado": ["Asignado", "Rechazado"],
    "Asignado": ["En proceso"],
    "En proceso": ["Resuelto"],
    "Resuelto": ["Verificado"],
    "Verificado": ["Cerrado"]
}

# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("Filtros")

estado_filtro = st.sidebar.multiselect(
    "Estado",
    sorted(df["Estado"].dropna().unique()),
    default=sorted(df["Estado"].dropna().unique())
)

df_filtrado = df[
    df["Estado"].isin(estado_filtro)
]

# =====================================================
# KPIs
# =====================================================

st.subheader("📌 Indicadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total",
    len(df_filtrado)
)

col2.metric(
    "Pendientes",
    len(
        df_filtrado[
            df_filtrado["Estado"] == "Pendiente"
        ]
    )
)

col3.metric(
    "En proceso",
    len(
        df_filtrado[
            df_filtrado["Estado"] == "En proceso"
        ]
    )
)

col4.metric(
    "Resueltos",
    len(
        df_filtrado[
            df_filtrado["Estado"] == "Resuelto"
        ]
    )
)

st.divider()

# =====================================================
# GRÁFICAS
# =====================================================

colA, colB = st.columns(2)

with colA:

    st.subheader("📊 Tickets por estado")

    estado_counts = (
        df_filtrado
        .groupby("Estado")
        .size()
        .reset_index(name="Cantidad")
    )

    if not estado_counts.empty:

        fig1 = px.bar(
            estado_counts,
            x="Estado",
            y="Cantidad",
            text="Cantidad"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

with colB:

    st.subheader("📊 Tickets por prioridad")

    prioridad_counts = (
        df_filtrado
        .groupby("Prioridad")
        .size()
        .reset_index(name="Cantidad")
    )

    if not prioridad_counts.empty:

        fig2 = px.pie(
            prioridad_counts,
            names="Prioridad",
            values="Cantidad"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

st.divider()

# =====================================================
# GESTIÓN DE TICKETS
# =====================================================

st.subheader("🛠 Gestión de tickets")

if len(df_filtrado) == 0:
    st.warning("No hay tickets disponibles")
    st.stop()

ticket_folio = st.selectbox(
    "Selecciona ticket",
    df_filtrado["Folio"].unique()
)

ticket_df = df[
    df["Folio"] == ticket_folio
]

if ticket_df.empty:
    st.error("Ticket no encontrado")
    st.stop()

ticket = ticket_df.iloc[0]

# =====================================================
# INFORMACIÓN DEL TICKET
# =====================================================

st.write("### Información del ticket")

col1, col2 = st.columns(2)

with col1:

    st.write(f"**Folio:** {ticket['Folio']}")
    st.write(f"**Estado:** {ticket['Estado']}")
    st.write(f"**Prioridad:** {ticket['Prioridad']}")
    st.write(f"**Edificio:** {ticket['Edificio']}")
    st.write(f"**Área:** {ticket['Area']}")
    st.write(f"**Activo:** {ticket['Activo']}")

with col2:

    st.write(f"**Reportó:** {ticket['Nombre']}")
    st.write(f"**Correo:** {ticket['Correo']}")
    st.write(f"**Categoría:** {ticket['Categoria']}")
    st.write(f"**Impacto:** {ticket['Impacto']}")
    st.write(f"**Responsable:** {ticket['Responsable']}")

st.write("### Descripción")

st.info(ticket["Descripcion"])

# =====================================================
# EVIDENCIA
# =====================================================

if str(ticket["ImagenApertura"]).strip() != "":

    if os.path.exists(ticket["ImagenApertura"]):

        st.write("### Evidencia inicial")

        st.image(
            ticket["ImagenApertura"],
            width=500
        )

# =====================================================
# CAMBIO DE ESTADO
# =====================================================

st.divider()

st.subheader("Actualizar ticket")

estado_actual = ticket["Estado"]

opciones_validas = TRANSICIONES.get(
    estado_actual,
    []
)

if len(opciones_validas) == 0:

    st.info(
        "Este ticket no tiene más transiciones disponibles."
    )

    nuevo_estado = estado_actual

else:

    nuevo_estado = st.selectbox(
        "Nuevo estado",
        opciones_validas
    )

responsable = st.text_input(
    "Responsable",
    value=str(ticket["Responsable"])
)

# =====================================================
# ACTUALIZACIÓN
# =====================================================

if st.button("Guardar cambios"):

    ahora = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    indice = df[
        df["Folio"] == ticket_folio
    ].index

    df.loc[indice, "Estado"] = nuevo_estado

    df.loc[indice, "Responsable"] = responsable

    df.loc[indice, "FechaActualizacion"] = ahora

    # ==========================================
    # FECHAS AUTOMÁTICAS
    # ==========================================

    if nuevo_estado == "Asignado":

        fecha_actual = str(
            df.loc[
                indice,
                "FechaAsignacion"
            ].values[0]
        )

        if fecha_actual.strip() == "":
            df.loc[
                indice,
                "FechaAsignacion"
            ] = ahora

    elif nuevo_estado == "Resuelto":

        fecha_actual = str(
            df.loc[
                indice,
                "FechaResolucion"
            ].values[0]
        )

        if fecha_actual.strip() == "":
            df.loc[
                indice,
                "FechaResolucion"
            ] = ahora

    elif nuevo_estado == "Cerrado":

        fecha_actual = str(
            df.loc[
                indice,
                "FechaCierre"
            ].values[0]
        )

        if fecha_actual.strip() == "":
            df.loc[
                indice,
                "FechaCierre"
            ] = ahora

    df.to_csv(
        RUTA_CSV,
        index=False
    )

    st.success(
        "Ticket actualizado correctamente"
    )

    st.rerun()

# =====================================================
# TABLA GENERAL
# =====================================================

st.divider()

st.subheader("📋 Todos los tickets")

columnas_tabla = [
    "Folio",
    "FechaCreacion",
    "Edificio",
    "Area",
    "Categoria",
    "Prioridad",
    "Estado",
    "Responsable"
]

st.dataframe(
    df_filtrado[columnas_tabla]
    .sort_values(
        by="FechaCreacion",
        ascending=False
    ),
    use_container_width=True
)
