import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Reportar", layout="wide")

RUTA_CSV = "data/reportes.csv"
RUTA_UBICACIONES = "data/catalogo_ubicaciones.csv"
RUTA_ACTIVOS = "data/catalogo_activos.csv"
CARPETA_EVIDENCIAS = "evidencias"

os.makedirs("data", exist_ok=True)
os.makedirs(CARPETA_EVIDENCIAS, exist_ok=True)

# =========================
# CARGA CATÁLOGOS
# =========================

cat_ubi = pd.read_csv(RUTA_UBICACIONES)
cat_act = pd.read_csv(RUTA_ACTIVOS)

cat_ubi.columns = cat_ubi.columns.str.strip()
cat_act.columns = cat_act.columns.str.strip()

# =========================
# CSV REPORTES
# =========================

if not os.path.exists(RUTA_CSV):
    df_init = pd.DataFrame(columns=[
        "ID","Fecha","TipoUsuario","Nombre","Correo",
        "Edificio","Area","Activo","Categoria",
        "Descripcion","Impacto","Estado","Imagen"
    ])
    df_init.to_csv(RUTA_CSV, index=False)

df = pd.read_csv(RUTA_CSV)
df.columns = df.columns.str.strip()

# =========================
# UBICACIÓN
# =========================

st.subheader("Ubicación")

edificio = st.selectbox("Edificio", cat_ubi["Edificio"].unique())

area = st.selectbox(
    "Área",
    cat_ubi[cat_ubi["Edificio"] == edificio]["Area"].unique()
)

# =========================
# FORM
# =========================

with st.form("form"):

    tipo = st.selectbox("Tipo usuario", ["Alumno","Docente","Admin"])
    nombre = st.text_input("Nombre")
    correo = st.text_input("Correo")

    activo = st.selectbox("Activo afectado", cat_act["Activo"].unique())

    categoria = st.selectbox("Categoría", [
        "Electricidad","Plomería","Infraestructura","Mobiliario",
        "Cómputo","Taller","Clima","Red","Seguridad","Limpieza","Otro"
    ])

    descripcion = st.text_area("Descripción")

    impacto = st.selectbox("Impacto", [
        "No afecta actividades",
        "Afecta parcialmente actividades",
        "Impide actividades"
    ])

    imagen = st.file_uploader("Evidencia", type=["png","jpg","jpeg"])

    enviar = st.form_submit_button("Enviar")

# =========================
# GUARDAR
# =========================

if enviar:

    ruta_img = ""

    if imagen:
        nombre_img = datetime.now().strftime("%Y%m%d%H%M%S")+"_"+imagen.name
        ruta_img = os.path.join(CARPETA_EVIDENCIAS, nombre_img)
        with open(ruta_img, "wb") as f:
            f.write(imagen.getbuffer())

    nuevo = {
        "ID": len(df)+1,
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "TipoUsuario": tipo,
        "Nombre": nombre,
        "Correo": correo,
        "Edificio": edificio,
        "Area": area,
        "Activo": activo,
        "Categoria": categoria,
        "Descripcion": descripcion,
        "Impacto": impacto,
        "Estado": "Pendiente",
        "Imagen": ruta_img
    }

    df = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
    df.to_csv(RUTA_CSV, index=False)

    st.success("Reporte guardado")
    st.rerun()
    