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
from database.supabase_client import supabase
from Services.evidencias_service import obtener_url_publica

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
# CARGA DE REPORTES DESDE SUPABASE
# =====================================================

try:

    respuesta = (
        supabase
        .table("reportes")
        .select("*")
        .execute()
    )

    df = pd.DataFrame(
        respuesta.data
    )

except Exception as e:

    st.error(
        f"Error cargando reportes: {e}"
    )

    st.stop()


if df.empty:

    st.warning(
        "No existen reportes registrados."
    )

    st.stop()
# =====================================================
# FORZAR COLUMNAS DE TEXTO
# =====================================================

columnas_texto = [
    "Folio",
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

if "ID" in df.columns:
    df["ID"] = df["ID"].astype(str)

# =====================================================
# FLUJO DE ESTADOS
# =====================================================

TRANSICIONES = {
    "Pendiente": ["Asignado", "Rechazado"],
    "Asignado": ["En proceso"],
    "En proceso": ["Resuelto"],
    "Resuelto": ["Cerrado"]
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

    st.write(f"**Categoría:** {ticket['Categoria']}")
    st.write(f"**Impacto:** {ticket['Impacto']}")
    st.write(f"**Responsable:** {ticket['Responsable']}")

st.write("### Descripción")

st.info(ticket["Descripcion"])

# =====================================================
# EVIDENCIA INICIAL
# =====================================================

ruta_imagen = str(
    ticket.get("ImagenApertura", "")
).strip()

if ruta_imagen not in ["", "nan", "None"]:

    st.write("### Evidencia inicial")

    url = obtener_url_publica(ruta_imagen)

    st.image(
        url,
        caption="Evidencia inicial",
        use_container_width=True
    )
# =====================================================
# FOTO FINAL
# =====================================================

ruta_cierre = str(
    ticket.get("ImagenCierre", "")
).strip()


if ruta_cierre not in ["", "nan", "None"]:

    st.write(
        "### Evidencia final"
    )

    url_cierre = obtener_url_publica(
        ruta_cierre
    )

    st.image(
        url_cierre,
        caption="Evidencia final",
        use_container_width=True
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

if st.button("Guardar cambios"):

    if (
        nuevo_estado == "Resuelto"
        and imagen_cierre is None
    ):
        
        st.error(
            "Debes adjuntar evidencia de cierre."
        )
        st.stop()


    ahora = datetime.now().strftime("%Y-%m-%d %H:%M")

    estado_anterior = ticket["Estado"]


    cambios = {}


    # Cambio de estado
    if nuevo_estado != estado_anterior:
        cambios["Estado"] = nuevo_estado


    # Cambio de responsable
    if responsable != ticket["Responsable"]:
        cambios["Responsable"] = responsable


    cambios["FechaActualizacion"] = ahora


    # ==========================================
    # FECHAS AUTOMÁTICAS
    # ==========================================

    if nuevo_estado == "Asignado":

        if str(ticket["FechaAsignacion"]).strip() == "":
            cambios["FechaAsignacion"] = ahora


    elif nuevo_estado == "Resuelto":

        if str(ticket["FechaResolucion"]).strip() == "":
            cambios["FechaResolucion"] = ahora


    elif nuevo_estado == "Cerrado":

        if str(ticket["FechaCierre"]).strip() == "":
            cambios["FechaCierre"] = ahora



    # ==========================================
    # IMAGEN DE CIERRE
    # ==========================================

    if imagen_cierre is not None:

        os.makedirs(
            "evidencias",
            exist_ok=True
        )


        nombre_img = (
            datetime.now().strftime("%Y%m%d%H%M%S")
            + "_CIERRE_"
            + imagen_cierre.name
        )


        ruta_img = os.path.join(
            "evidencias",
            nombre_img
        )


        with open(
            ruta_img,
            "wb"
        ) as f:

            f.write(
                imagen_cierre.getbuffer()
            )


        cambios["ImagenCierre"] = ruta_img



    # ==========================================
    # ACTUALIZAR SUPABASE
    # ==========================================

    try:

        supabase.table("reportes").update(
            cambios
        ).eq(
            "Folio",
            ticket_folio
        ).execute()


        registrar_movimiento(
            folio=ticket_folio,
            usuario="Sistema",
            accion="Cambio de estado",
            detalle=f"{estado_anterior} → {nuevo_estado}"
        )


        st.success(
            "Ticket actualizado correctamente"
        )


        st.rerun()


    except Exception as e:

        st.error(
            f"Error actualizando ticket: {e}"
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
            usuario="Sistema",
            comentario=nuevo_comentario
        )

        registrar_movimiento(
            folio=ticket_folio,
            usuario="Sistema",
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

    respuesta = (
        supabase
        .table("historial")
        .select("*")
        .eq("Folio", ticket_folio)
        .execute()
    )

    historial_ticket = pd.DataFrame(
        respuesta.data
    )

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