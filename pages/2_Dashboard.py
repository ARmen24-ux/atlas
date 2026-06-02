import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils.historial import registrar_movimiento
from utils.data_guard import asegurar_esquema
from utils.sla import calcular_sla
from utils.comentarios import (
    agregar_comentario,
    obtener_comentarios
)

def aplicar_sla(df):
    df = df.copy()
    df["SLA"] = [
        calcular_sla(f["FechaCreacion"], f["Prioridad"])[0]
        for _, f in df.iterrows()
    ]
    return df
# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="ATLAS Dashboard",
    layout="wide"
)

st.title("ATLAS - Panel de Mantenimiento")

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

df = pd.read_csv(
    RUTA_CSV,
    keep_default_na=False
)

df = asegurar_esquema(df)

# =====================================================
# FORZAR COLUMNAS DE TEXTO
# =====================================================

columnas_texto = [
    "Folio",
    "TipoUsuario",
    "Nombre",
    "Correo",
    "Edificio",
    "Area",
    "UbicacionDetalle",
    "Activo",
    "Categoria",
    "Impacto",
    "Prioridad",
    "Descripcion",
    "Estado",
    "Responsable",
    "ComentarioCierre",
    "ImagenApertura",
    "ImagenCierre"
]

for col in columnas_texto:

    if col in df.columns:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
        )

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

df_filtrado = aplicar_sla(
    df[df["Estado"].isin(estado_filtro)]
)

# =====================================================
# KPIs
# =====================================================

st.subheader(" Indicadores")

en_tiempo = len(
    df_filtrado[
        df_filtrado["SLA"] == "En tiempo"
    ]
)

proximos = len(
    df_filtrado[
        df_filtrado["SLA"] == "Próximo a vencer"
    ]
)

vencidos = len(
    df_filtrado[
        df_filtrado["SLA"] == "Vencido"
    ]
)

cumplimiento = 0

if len(df_filtrado) > 0:

    cumplimiento = round(
        (en_tiempo / len(df_filtrado)) * 100,
        1
    )

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🟢 En tiempo",
    en_tiempo
)

col2.metric(
    "🟡 Próximos",
    proximos
)

col3.metric(
    "🔴 Vencidos",
    vencidos
)

col4.metric(
    " SLA %",
    f"{cumplimiento}%"
)

st.divider()

# =====================================================
# GRÁFICAS
# =====================================================

colA, colB = st.columns(2)

with colA:

    st.subheader(" Tickets por estado")

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

    st.subheader(" Tickets por prioridad")

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

st.subheader(" Gestión de tickets")

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
# SLA
# =====================================================

estado_sla, horas_restantes = calcular_sla(
    ticket["FechaCreacion"],
    ticket["Prioridad"]
)

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

if estado_sla == "En tiempo":

    st.success(
        f"SLA: {estado_sla}"
    )

elif estado_sla == "Próximo a vencer":

    st.warning(
        f"SLA: {estado_sla}"
    )

else:

    st.error(
        f"SLA: {estado_sla}"
    )
    
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
st.write("Ruta imagen:")
st.write(ticket["ImagenApertura"])

st.write("Existe:")
st.write(
    os.path.exists(
        ticket["ImagenApertura"]
    )
)
if str(ticket["ImagenApertura"]).strip() != "":

    if os.path.exists(ticket["ImagenApertura"]):

        st.write("### Evidencia inicial")

        st.image(
            ticket["ImagenApertura"],
            width=500
        )

# =====================================================
# FOTO FINAL
# =====================================================

if str(ticket["ImagenCierre"]).strip() != "":

    if os.path.exists(
        ticket["ImagenCierre"]
    ):

        st.write(
            "### Evidencia final"
        )

        st.image(
            ticket["ImagenCierre"],
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

# =====================================================
# VALIDACIÓN DE TRANSICIÓN
# =====================================================

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


# =====================================================
# RESPONSABLE
# =====================================================

responsable = st.text_input(
    "Responsable",
    value=str(ticket["Responsable"])
)

# =====================================================
# EVIDENCIA DE CIERRE
# =====================================================

imagen_cierre = None

if nuevo_estado == "Resuelto":

    st.write(
        "### 📷 Evidencia de cierre"
    )

    imagen_cierre = st.file_uploader(
        "Fotografía del trabajo realizado",
        type=["png", "jpg", "jpeg"],
        key="img_cierre"
    )

# =====================================================
# ACTUALIZACIÓN
# =====================================================

if nuevo_estado == "Resuelto" and imagen_cierre is None:

    st.error(
        "Debes adjuntar evidencia de cierre."
    )

    st.stop()
    
if st.button("Guardar cambios"):

    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")
    estado_anterior = ticket["Estado"]

    idx = df.index[df["Folio"] == ticket_folio]

    if len(idx) == 0:
        st.error("Ticket no encontrado")
        st.stop()

    idx = idx[0]

    cambios = {}

    if nuevo_estado != estado_anterior:
        cambios["Estado"] = nuevo_estado

    if responsable != ticket["Responsable"]:
        cambios["Responsable"] = responsable

    cambios["FechaActualizacion"] = ahora

    # aplicar cambios de forma segura
    for k, v in cambios.items():
        df.loc[idx, k] = v

    # ==========================================
    # FECHAS AUTOMÁTICAS
    # ==========================================

    if nuevo_estado == "Asignado":

        if str(df.loc[idx, "FechaAsignacion"]).strip() == "":
            df.loc[idx, "FechaAsignacion"] = ahora

    elif nuevo_estado == "Resuelto":

        if str(df.loc[idx, "FechaResolucion"]).strip() == "":
            df.loc[idx, "FechaResolucion"] = ahora

    elif nuevo_estado == "Cerrado":

        if str(df.loc[idx, "FechaCierre"]).strip() == "":
            df.loc[idx, "FechaCierre"] = ahora

    # ====== IMAGEN CIERRE ======
    if imagen_cierre is not None:

        os.makedirs("evidencias", exist_ok=True)

        nombre_img = (
            datetime.now().strftime("%Y%m%d%H%M%S")
            + "_CIERRE_"
            + imagen_cierre.name
        )

        ruta_img = os.path.join("evidencias", nombre_img)

        with open(ruta_img, "wb") as f:
            f.write(imagen_cierre.getbuffer())

        df.loc[idx, "ImagenCierre"] = ruta_img
        
    registrar_movimiento(
        folio=ticket_folio,
        usuario=st.session_state.get(
            "usuario",
            "Sistema"
        ),
        accion="Cambio de estado",
        detalle=f"{estado_anterior} → {nuevo_estado}"
    )

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

# =====================================================
# CALCULAR SLA PARA TABLA
# =====================================================
df_filtrado = df_filtrado.copy()

df_filtrado["SLA"] = [
    calcular_sla(
        f["FechaCreacion"],
        f["Prioridad"]
    )[0]
    for _, f in df_filtrado.iterrows()
]

df_filtrado["HorasRestantes"] = [
    calcular_sla(
        f["FechaCreacion"],
        f["Prioridad"]
    )[1]
    for _, f in df_filtrado.iterrows()
]

columnas_tabla = [
    "Folio",
    "FechaCreacion",
    "Edificio",
    "Area",
    "Categoria",
    "Prioridad",
    "Estado",
    "SLA",
    "Responsable",
    "HorasRestantes"
]

st.dataframe(
    df_filtrado[columnas_tabla]
    .sort_values(
        by="FechaCreacion",
        ascending=False
    ),
    use_container_width=True
)

# =====================================================
# Bitácora técnica
# =====================================================

st.divider()

st.subheader("📝 Bitácora técnica")

comentarios_ticket = obtener_comentarios(
    ticket_folio
)

if comentarios_ticket.empty:

    st.info(
        "No existen comentarios registrados."
    )

else:

    comentarios_ticket = comentarios_ticket.sort_values(
        by="Fecha",
        ascending=False
    )

    for _, comentario in comentarios_ticket.iterrows():

        with st.container():

            st.markdown(
                f"""
                **{comentario['Fecha']}**

                👤 {comentario['Usuario']}

                {comentario['Comentario']}
                """
            )

            st.divider()

# =====================================================
# NUEVO COMENTARIO
# =====================================================

st.write("### Agregar comentario")

nuevo_comentario = st.text_area(
    "Comentario técnico",
    key="nuevo_comentario"
)

if st.button(
    "Guardar comentario"
):

    if nuevo_comentario.strip() == "":

        st.warning(
            "Escribe un comentario."
        )

    else:

        agregar_comentario(
            folio=ticket_folio,
            usuario=st.session_state.get(
                "usuario",
                "Sistema"
            ),
            comentario=nuevo_comentario
        )

        registrar_movimiento(
            folio=ticket_folio,
            usuario=st.session_state.get(
                "usuario",
                "Sistema"
            ),
            accion="Comentario",
            detalle=nuevo_comentario
        )

        st.success(
            "Comentario agregado."
        )

        st.rerun()

# =====================================================
# HISTORIAL DEL TICKET
# =====================================================

st.divider()

st.subheader("🕓 Historial del ticket")

try:

    historial = pd.read_csv(
        "data/historial.csv",
        keep_default_na=False
    )

    historial_ticket = historial[
        historial["Folio"] == ticket_folio
    ]

    if historial_ticket.empty:

        st.info(
            "No existen movimientos registrados para este ticket."
        )

    else:

        historial_ticket = historial_ticket.sort_values(
            by="Fecha",
            ascending=False
        )

        st.dataframe(
            historial_ticket,
            use_container_width=True
        )

except Exception as e:

    st.warning(
        f"No fue posible cargar el historial: {e}"
    )