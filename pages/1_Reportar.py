import streamlit as st

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

from Services.evidencias_service import comprimir_imagen
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

        jpg = comprimir_imagen(imagen)

        st.success(
            "Imagen capturada"
        )

        st.write(
            f"📦 Tamaño original: {imagen.size/1024:.1f} KB"
        )

        st.write(
            f"🗜️ Tamaño comprimido: {len(jpg.getvalue())/1024:.1f} KB"
        )

        st.image(
            jpg,
            caption="Vista previa comprimida",
            use_container_width=True
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

    if descripcion.strip() == "":

        st.error(
            "Describe el problema"
        )

        st.stop()

    # ==========================================
    # DATOS DEL FORMULARIO
    # ==========================================

    datos = {

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