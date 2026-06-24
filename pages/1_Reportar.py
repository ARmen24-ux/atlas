import streamlit as st
import re

from database.catalogos_db import (
    cargar_ubicaciones,
    cargar_activos,
    cargar_categorias,
    cargar_prioridades,
    cargar_impactos
)

from Services.reportes_service import (
    crear_reporte
)

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Reportar incidencia",
    layout="wide"
)

st.title("📋 Reportar incidencia")

# =====================================================
# CARGA DE CATÁLOGOS
# =====================================================

try:

    ubi = cargar_ubicaciones()

    act = cargar_activos()

    cat = cargar_categorias()

    prio = cargar_prioridades()

    imp = cargar_impactos()

except Exception as e:

    st.error(
        f"Error al cargar catálogos: {e}"
    )

    st.stop()

# =====================================================
# UBICACIÓN
# =====================================================

st.subheader("📍 Ubicación")

edificio = st.selectbox(
    "Edificio",
    ubi["Edificio"].unique()
)

areas_filtradas = (
    ubi.loc[
        ubi["Edificio"] == edificio,
        "Area"
    ]
    .dropna()
    .unique()
    .tolist()
)

if not areas_filtradas:

    areas_filtradas = [
        "Sin áreas registradas"
    ]

area = st.selectbox(
    "Área",
    areas_filtradas
)

ubicacion_detalle = st.text_input(
    "Detalle adicional (opcional)"
)

# =====================================================
# FORMULARIO
# =====================================================

with st.form("formulario_reporte"):

    st.subheader(
        "👤 Datos del usuario"
    )

    tipo = st.selectbox(
        "Tipo de usuario",
        [
            "Alumno",
            "Docente",
            "Administrativo"
        ]
    )

    nombre = st.text_input(
        "Nombre"
    )

    correo = st.text_input(
        "Correo"
    )

    st.divider()

    st.subheader(
        "🛠 Información de la incidencia"
    )

    activo = st.selectbox(
        "Activo afectado",
        act["Activo"].unique()
    )

    categoria = st.selectbox(
        "Categoría",
        cat["Categoria"]
        .dropna()
        .tolist()
    )

    prioridad = st.selectbox(
        "Prioridad",
        prio["Prioridad"]
        .dropna()
        .tolist()
)

    descripcion = st.text_area(
        "Descripción del problema"
    )

    impacto = st.selectbox(
        "Impacto",
        imp["Impacto"]
        .dropna()
        .tolist()
    )

    imagen = st.camera_input(
        "Tomar fotografía"
    )

    if imagen is not None:

        st.success(
            "Imagen capturada"
        )

    enviar = st.form_submit_button(
        "Enviar reporte"
    )

# =====================================================
# CREAR REPORTE
# =====================================================

if enviar:

    # ==========================================
    # VALIDACIONES
    # ==========================================

    if nombre.strip() == "":

        st.error(
            "Ingresa tu nombre"
        )

        st.stop()

    if correo.strip() == "":

        st.error(
            "Ingresa un correo"
        )

        st.stop()

    patron_correo = (
        r"^[\w\.-]+@[\w\.-]+\.\w+$"
    )

    if not re.match(
        patron_correo,
        correo
    ):

        st.error(
            "Ingresa un correo válido"
        )

        st.stop()

    if descripcion.strip() == "":

        st.error(
            "Describe el problema"
        )

        st.stop()

    # ==========================================
    # DATOS DEL FORMULARIO
    # ==========================================

    datos = {

        "tipo": tipo,

        "nombre": nombre,

        "correo": correo,

        "edificio": edificio,

        "area": area,

        "ubicacion_detalle":
            ubicacion_detalle,

        "activo": activo,

        "categoria": categoria,

        "impacto": impacto,

        "prioridad": prioridad,

        "descripcion": descripcion,

        "imagen": imagen
    }

    # ==========================================
    # CREAR REPORTE
    # ==========================================

    resultado = crear_reporte(
        datos
    )

    # ==========================================
    # RESPUESTA
    # ==========================================

    if resultado["ok"]:

        st.success(
            resultado["mensaje"]
        )

        st.rerun()

    else:

        st.error(
            resultado["mensaje"]
        )