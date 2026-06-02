import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

from utils.data_guard import asegurar_esquema
from utils.historial import registrar_movimiento

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Reportar incidencia",
    layout="wide"
)

st.title(" Reportar incidencia")

# =====================================================
# RUTAS
# =====================================================

RUTA_CSV = "data/reportes.csv"
RUTA_UBI = "data/catalogo_ubicaciones.csv"
RUTA_ACTIVOS = "data/catalogo_activos.csv"
CARPETA_IMG = "evidencias"

os.makedirs("data", exist_ok=True)
os.makedirs(CARPETA_IMG, exist_ok=True)

# =====================================================
# CARGA DE CATÁLOGOS
# =====================================================

ubi = pd.read_csv(RUTA_UBI)
act = pd.read_csv(RUTA_ACTIVOS)

ubi.columns = ubi.columns.str.strip()
act.columns = act.columns.str.strip()

# =====================================================
# CARGA DE REPORTES
# =====================================================

if not os.path.exists(RUTA_CSV):

    df_init = pd.DataFrame()

    df_init = asegurar_esquema(df_init)

    df_init.to_csv(
        RUTA_CSV,
        index=False
    )

df = pd.read_csv(
    RUTA_CSV,
    keep_default_na=False
)

df = asegurar_esquema(df)

df.to_csv(
    RUTA_CSV,
    index=False
)


# =====================================================
# UBICACIÓN
# =====================================================

st.subheader(" Ubicación")

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
    areas_filtradas = ["Sin áreas registradas"]

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

    st.subheader(" Datos del usuario")

    tipo = st.selectbox(
        "Tipo de usuario",
        [
            "Alumno",
            "Docente",
            "Administrativo"
        ]
    )

    nombre = st.text_input("Nombre")

    correo = st.text_input("Correo")

    st.divider()

    st.subheader(" Información de la incidencia")

    activo = st.selectbox(
        "Activo afectado",
        act["Activo"].unique()
    )

    categoria = st.selectbox(
        "Categoría",
        [
            "Electricidad",
            "Plomería",
            "Infraestructura",
            "Mobiliario",
            "Cómputo",
            "Red",
            "Seguridad",
            "Limpieza",
            "Otro"
        ]
    )

    prioridad = st.selectbox(
        "Prioridad",
        [
            "Baja",
            "Media",
            "Alta",
            "Crítica"
        ]
    )

    descripcion = st.text_area(
        "Descripción del problema"
    )

    impacto = st.selectbox(
        "Impacto",
        [
            "No afecta actividades",
            "Afecta parcialmente",
            "Impide actividades"
        ]
    )

    imagen = st.file_uploader(
        "Evidencia fotográfica",
        type=["png", "jpg", "jpeg"]
    )

    enviar = st.form_submit_button(
        "Enviar reporte"
    )

# =====================================================
# GUARDAR REPORTE
# =====================================================

if enviar:

    if nombre.strip() == "":
        st.error("Ingresa tu nombre")
        st.stop()

    if correo.strip() == "":
        st.error("Ingresa un correo")
        st.stop()
    
    patron_correo = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    if not re.match(patron_correo, correo):
        st.error("Ingresa un correo válido")
        st.stop()

    if descripcion.strip() == "":
        st.error("Describe el problema")
        st.stop()

    # =================================================
    # IMAGEN APERTURA
    # =================================================

    ruta_img = ""

    if imagen is not None:

        nombre_img = (
            datetime.now().strftime("%Y%m%d%H%M%S")
            + "_"
            + imagen.name
        )

        ruta_img = os.path.join(
            CARPETA_IMG,
            nombre_img
        )

        with open(ruta_img, "wb") as archivo:
            archivo.write(
                imagen.getbuffer()
            )

    # =================================================
    # ID SEGURO
    # =================================================

    if len(df) == 0:

        nuevo_id = 1

    else:

        nuevo_id = (
            pd.to_numeric(
                df["ID"],
                errors="coerce"
            )
            .fillna(0)
            .max()
            + 1
        )

        nuevo_id = int(nuevo_id)

    # =================================================
    # FOLIO
    # =================================================

    folio = f"UTG-2026-{nuevo_id:05d}"

    fecha_actual = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    # =================================================
    # NUEVO REPORTE
    # =================================================

    nuevo = {

        "ID": nuevo_id,

        "Folio": folio,

        "FechaCreacion": fecha_actual,

        "FechaAsignacion": "",

        "FechaResolucion": "",

        "FechaCierre": "",

        "FechaActualizacion": fecha_actual,

        "TipoUsuario": tipo,

        "Nombre": nombre,

        "Correo": correo,

        "Edificio": edificio,

        "Area": area,

        "UbicacionDetalle": ubicacion_detalle,

        "Activo": activo,

        "Categoria": categoria,

        "Impacto": impacto,

        "Prioridad": prioridad,

        "Descripcion": descripcion,

        "Estado": "Pendiente",

        "Responsable": "",

        "ComentarioCierre": "",

        "ImagenApertura": ruta_img,

        "ImagenCierre": ""
    }

    # =================================================
    # GUARDAR
    # =================================================

    df = pd.concat(
        [
            df,
            pd.DataFrame([nuevo])
        ],
        ignore_index=True
    )

    df = asegurar_esquema(df)

    df.to_csv(
        RUTA_CSV,
        index=False
    )

    registrar_movimiento(
        folio=folio,
        usuario=nombre,
        accion="Creación",
        detalle="Reporte creado por usuario"
    )

    st.success(
        f"Reporte enviado correctamente.\n\nFolio: {folio}"
    )

    st.rerun()