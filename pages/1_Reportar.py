import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(page_title="Reportar incidencia", layout="wide")
st.title("📋 Reportar incidencia")

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
# CATÁLOGOS
# =====================================================

ubi = pd.read_csv(RUTA_UBI)
act = pd.read_csv(RUTA_ACTIVOS)

ubi.columns = ubi.columns.str.strip()
act.columns = act.columns.str.strip()

# =====================================================
# CSV BASE
# =====================================================

if not os.path.exists(RUTA_CSV):
    df_init = pd.DataFrame(columns=[
        "ID","Folio","FechaCreacion","TipoUsuario","Nombre","Correo",
        "Edificio","Area","UbicacionDetalle","Activo","Categoria",
        "Prioridad","Descripcion","Impacto","Estado",
        "Responsable","FechaActualizacion","Imagen"
    ])
    df_init.to_csv(RUTA_CSV, index=False)

df = pd.read_csv(RUTA_CSV)
df.columns = df.columns.str.strip()

# =====================================================
# FORMULARIO
# =====================================================

with st.form("form"):

    st.subheader("Datos del usuario")

    tipo = st.selectbox("Tipo de usuario", ["Alumno","Docente","Administrativo"])
    nombre = st.text_input("Nombre")
    correo = st.text_input("Correo")

    st.divider()
    st.subheader("Ubicación")

    # =====================================================
    # EDIFICIO
    # =====================================================

    edificio = st.selectbox(
        "Edificio",
        ubi["Edificio"].unique()
    )

    # =====================================================
    # 🔥 FIX REAL DE STREAMLIT (DEPENDENCIA ESTABLE)
    # =====================================================

    areas_filtradas = ubi[ubi["Edificio"] == edificio]["Area"].dropna().unique().tolist()

    if len(areas_filtradas) == 0:
        areas_filtradas = ["Sin áreas registradas"]

    # key dinámica = RECONSTRUYE widget correctamente
    area = st.selectbox(
        "Área",
        options=areas_filtradas,
        key=f"area_{edificio}"
    )

    ubicacion_detalle = st.text_input("Detalle adicional (opcional)")

    st.divider()
    st.subheader("Problema")

    activo = st.selectbox("Activo afectado", act["Activo"].unique())

    categoria = st.selectbox("Categoría", [
        "Electricidad","Plomería","Infraestructura","Mobiliario",
        "Cómputo","Red","Seguridad","Limpieza","Otro"
    ])

    prioridad = st.selectbox("Prioridad", ["Baja","Media","Alta","Crítica"])

    descripcion = st.text_area("Descripción")

    impacto = st.selectbox("Impacto", [
        "No afecta actividades",
        "Afecta parcialmente actividades",
        "Impide actividades"
    ])

    imagen = st.file_uploader("Evidencia", type=["png","jpg","jpeg"])

    enviar = st.form_submit_button("Enviar reporte")

# =====================================================
# GUARDAR
# =====================================================

if enviar:

    if descripcion.strip() == "":
        st.error("Describe el problema")
        st.stop()

    ruta_img = ""

    if imagen:
        nombre_img = datetime.now().strftime("%Y%m%d%H%M%S") + "_" + imagen.name
        ruta_img = os.path.join(CARPETA_IMG, nombre_img)

        with open(ruta_img, "wb") as f:
            f.write(imagen.getbuffer())

    folio = f"UTG-2026-{len(df)+1:05d}"

    nuevo = {
        "ID": len(df)+1,
        "Folio": folio,
        "FechaCreacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "TipoUsuario": tipo,
        "Nombre": nombre,
        "Correo": correo,
        "Edificio": edificio,
        "Area": area,
        "UbicacionDetalle": ubicacion_detalle,
        "Activo": activo,
        "Categoria": categoria,
        "Prioridad": prioridad,
        "Descripcion": descripcion,
        "Impacto": impacto,
        "Estado": "Pendiente",
        "Responsable": "",
        "FechaActualizacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Imagen": ruta_img
    }

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv(RUTA_CSV, index=False)

    st.success(f"Reporte enviado: {folio}")
    st.rerun()

    