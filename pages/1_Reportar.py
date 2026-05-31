import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Reportar incidencia",
    layout="wide"
)

st.title("📋 Reportar incidencia")

st.write(
    "Utilice este formulario para reportar problemas "
    "en las instalaciones universitarias."
)

# =====================================================
# RUTAS
# =====================================================

RUTA_CSV = os.path.join("data", "reportes.csv")
CARPETA_EVIDENCIAS = "evidencias"
RUTA_CATALOGO = os.path.join("data", "catalogo_ubicaciones.csv")

# =====================================================
# CREAR CARPETAS
# =====================================================

os.makedirs("data", exist_ok=True)
os.makedirs(CARPETA_EVIDENCIAS, exist_ok=True)

# =====================================================
# CREAR CSV SI NO EXISTE
# =====================================================

if not os.path.exists(RUTA_CSV):

    df_inicial = pd.DataFrame(columns=[
        "ID",
        "Fecha",
        "TipoUsuario",
        "Nombre",
        "Correo",
        "Edificio",
        "Area",
        "Categoria",
        "Descripcion",
        "Impacto",
        "Estado",
        "Imagen"
    ])

    df_inicial.to_csv(RUTA_CSV, index=False)

# =====================================================
# LEER CSV
# =====================================================

df = pd.read_csv(RUTA_CSV)

# =====================================================
# CARGAR CATÁLOGO DE UBICACIONES
# =====================================================

catalogo = pd.read_csv(RUTA_CATALOGO)

catalogo["Edificio"] = catalogo["Edificio"].str.strip()
catalogo["Area"] = catalogo["Area"].str.strip()

# =====================================================
# FORMULARIO
# =====================================================

with st.form("formulario_reporte"):

    st.subheader("Información del reportante")

    tipo_usuario = st.selectbox(
        "Tipo de usuario",
        ["Alumno", "Docente", "Administrativo"]
    )

    nombre = st.text_input("Nombre (opcional)")
    correo = st.text_input("Correo institucional (opcional)")

    st.divider()

    # =====================================================
    # UBICACIÓN (CONTROLADA)
    # =====================================================

    st.subheader("Ubicación")

    edificios = catalogo["Edificio"].unique()
    edificio = st.selectbox("Edificio", edificios)

    areas_filtradas = catalogo[
        catalogo["Edificio"] == edificio
    ]["Area"].unique()

    area = st.selectbox("Área", areas_filtradas)

    st.divider()

    # =====================================================
    # INFORMACIÓN DEL PROBLEMA
    # =====================================================

    st.subheader("Información del problema")

    categoria = st.selectbox(
        "Categoría",
        [
            "Electricidad",
            "Plomería",
            "Infraestructura",
            "Mobiliario",
            "Equipos de Cómputo",
            "Equipos de Taller",
            "Climatización",
            "Internet y Red",
            "Seguridad",
            "Limpieza",
            "Otro"
        ]
    )

    descripcion = st.text_area("Descripción del problema")

    impacto = st.selectbox(
        "Impacto del problema",
        [
            "No afecta actividades",
            "Afecta parcialmente actividades",
            "Impide realizar actividades"
        ]
    )

    st.divider()

    # =====================================================
    # EVIDENCIA
    # =====================================================

    imagen = st.file_uploader(
        "Subir evidencia",
        type=["png", "jpg", "jpeg"]
    )

    enviar = st.form_submit_button("Enviar reporte")

# =====================================================
# GUARDAR REPORTE
# =====================================================

if enviar:

    if descripcion.strip() == "":
        st.error("Debe describir el problema.")
        st.stop()

    ruta_imagen = ""

    if imagen is not None:

        nombre_imagen = (
            datetime.now().strftime("%Y%m%d%H%M%S")
            + "_"
            + imagen.name
        )

        ruta_imagen = os.path.join(
            CARPETA_EVIDENCIAS,
            nombre_imagen
        )

        with open(ruta_imagen, "wb") as archivo:
            archivo.write(imagen.getbuffer())

    nuevo_id = len(df) + 1

    nuevo_reporte = {
        "ID": nuevo_id,
        "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "TipoUsuario": tipo_usuario,
        "Nombre": nombre,
        "Correo": correo,
        "Edificio": edificio,
        "Area": area,
        "Categoria": categoria,
        "Descripcion": descripcion,
        "Impacto": impacto,
        "Estado": "Pendiente",
        "Imagen": ruta_imagen
    }

    df = pd.concat([df, pd.DataFrame([nuevo_reporte])], ignore_index=True)

    df.to_csv(RUTA_CSV, index=False)

    st.success("Reporte enviado correctamente.")
    st.balloons()

    st.rerun()
    