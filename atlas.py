import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =====================================================
# CONFIGURACION DE PAGINA
# =====================================================

st.set_page_config(
    page_title="ATLAS",
    layout="wide"
)

# =====================================================
# ESTILOS CSS
# =====================================================

st.markdown("""
<style>

/* =====================================================
FONDO GENERAL
===================================================== */

.stApp {
    background-color: #0e1117;
}

/* =====================================================
CONTENEDOR PRINCIPAL
===================================================== */

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* =====================================================
TITULO PRINCIPAL
===================================================== */

.titulo-Atlas {
    text-align: center;
    font-size: 5rem;
    font-weight: 800;
    letter-spacing: 8px;
    color: white;
    margin-bottom: 0;
    margin-top: 10px;
}

/* =====================================================
SUBTITULO
===================================================== */

.subtitulo {
    text-align: center;
    font-size: 1.6rem;
    color: #9ca3af;
    margin-top: 0;
}

/* =====================================================
DESCRIPCION
===================================================== */

.descripcion {
    text-align: center;
    font-size: 1rem;
    color: #d1d5db;
    margin-bottom: 40px;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background-color: #1b222c;
    border-right: 1px solid #2d3748;
}

/* TITULOS SIDEBAR */

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white;
}

/* =====================================================
INPUTS Y TEXTAREA
===================================================== */

.stTextInput input,
.stTextArea textarea {
    background-color: #242c38;
    color: white;
    border: 1px solid #3b4657;
    border-radius: 10px;
}

/* =====================================================
SELECTBOX
===================================================== */

div[data-baseweb="select"] > div {
    background-color: #242c38;
    border: 1px solid #3b4657;
    border-radius: 10px;
}

/* =====================================================
FILE UPLOADER
===================================================== */

section[data-testid="stFileUploader"] {
    background-color: #242c38;
    border-radius: 10px;
    padding: 10px;
    border: 1px solid #3b4657;
}

/* =====================================================
BOTONES
===================================================== */

.stButton > button {
    width: 100%;
    background-color: #334155;
    color: white;
    border-radius: 10px;
    border: none;
    height: 45px;
    font-size: 15px;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background-color: #475569;
    color: white;
}

/* =====================================================
METRICAS
===================================================== */

div[data-testid="stMetric"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 20px;
}

/* =====================================================
TEXTO DE METRICAS
===================================================== */

div[data-testid="stMetricLabel"] {
    color: #9ca3af;
    font-size: 16px;
}

div[data-testid="stMetricValue"] {
    color: white;
}

/* =====================================================
TABLAS
===================================================== */

div[data-testid="stDataFrame"] {
    border: 1px solid #30363d;
    border-radius: 12px;
    overflow: hidden;
}

/* =====================================================
LINEAS DIVISORAS
===================================================== */

hr {
    border-color: #30363d;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# RUTAS
# =====================================================

RUTA_CSV = os.path.join("data", "reportes.csv")
CARPETA_EVIDENCIAS = "evidencias"

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
        "Area",
        "Problema",
        "Descripcion",
        "Prioridad",
        "Estado",
        "Imagen"
    ])

    df_inicial.to_csv(RUTA_CSV, index=False)

# =====================================================
# LEER CSV
# =====================================================

df = pd.read_csv(RUTA_CSV)

# =====================================================
# CORREGIR COLUMNAS FALTANTES
# =====================================================

if "ID" not in df.columns:
    df.insert(0, "ID", range(1, len(df) + 1))

if "Estado" not in df.columns:
    df["Estado"] = "Pendiente"

if "Imagen" not in df.columns:
    df["Imagen"] = ""

df.to_csv(RUTA_CSV, index=False)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<h1 class="titulo-atlas">
ATLAS
</h1>

<p class="subtitulo">
Sistema de reportes de mantenimiento escolar
</p>

<p class="descripcion">
Plataforma institucional para el registro, monitoreo y seguimiento
de incidencias dentro de las instalaciones escolares.
</p>
""", unsafe_allow_html=True)

st.divider()

# =====================================================
# METRICAS
# =====================================================

total_reportes = len(df)

pendientes = len(df[df["Estado"] == "Pendiente"])

en_proceso = len(df[df["Estado"] == "En proceso"])

urgentes = len(df[df["Prioridad"] == "Urgente"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total", total_reportes)
col2.metric("Pendientes", pendientes)
col3.metric("En proceso", en_proceso)
col4.metric("Urgentes", urgentes)

st.divider()

# =====================================================
# FORMULARIO
# =====================================================

with st.sidebar.form("formulario_reporte"):

    area = st.selectbox(
        "Área afectada",
        [
            "Salón",
            "Laboratorio",
            "Oficina",
            "Auditorio",
            "Baño",
            "Pasillo",
            "Taller",
            "Otro"
        ]
    )

    problema = st.text_input("Problema detectado")

    descripcion = st.text_area("Descripción del problema")

    prioridad = st.selectbox(
        "Prioridad",
        [
            "Baja",
            "Media",
            "Alta",
            "Urgente"
        ]
    )

    imagen = st.file_uploader(
        "Subir evidencia",
        type=["png", "jpg", "jpeg"]
    )

    enviar = st.form_submit_button("Guardar reporte")
    
# =====================================================
# GUARDAR REPORTE
# =====================================================

if enviar:

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
        "Area": area,
        "Problema": problema,
        "Descripcion": descripcion,
        "Prioridad": prioridad,
        "Estado": "Pendiente",
        "Imagen": ruta_imagen
    }

    df = pd.concat(
        [df, pd.DataFrame([nuevo_reporte])],
        ignore_index=True
    )

    df.to_csv(RUTA_CSV, index=False)

    st.success("Reporte guardado correctamente")

    st.rerun()

# =====================================================
# TABLA DE REPORTES
# =====================================================

st.subheader("Tabla de reportes")

if df.empty:

    st.info("No existen reportes registrados.")

else:

    # =================================================
    # FILTROS
    # =================================================

    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:

        filtro_area = st.selectbox(
            "Filtrar por área",
            ["Todas"] + list(df["Area"].unique())
        )

    with col_f2:

        filtro_prioridad = st.selectbox(
            "Filtrar por prioridad",
            ["Todas"] + list(df["Prioridad"].unique())
        )

    with col_f3:

        filtro_estado = st.selectbox(
            "Filtrar por estado",
            ["Todos"] + list(df["Estado"].unique())
        )

    # =================================================
    # APLICAR FILTROS
    # =================================================

    df_filtrado = df.copy()

    if filtro_area != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Area"] == filtro_area
        ]

    if filtro_prioridad != "Todas":

        df_filtrado = df_filtrado[
            df_filtrado["Prioridad"] == filtro_prioridad
        ]

    if filtro_estado != "Todos":

        df_filtrado = df_filtrado[
            df_filtrado["Estado"] == filtro_estado
        ]

    # =================================================
    # TABLA
    # =================================================

    tabla = df_filtrado.copy()

    tabla["Imagen"] = tabla["Imagen"].apply(
        lambda x: "Disponible"
        if pd.notna(x) and x != ""
        else "Sin imagen"
    )

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # =================================================
    # CONSULTAR REPORTE
    # =================================================

    st.subheader("Consultar reporte")

    lista_reportes = list(df_filtrado["ID"])

    reporte_seleccionado = st.selectbox(
        "Seleccionar número de reporte",
        lista_reportes
    )

    reporte = df_filtrado[
        df_filtrado["ID"] == reporte_seleccionado
    ].iloc[0]

    col_info, col_imagen = st.columns([2, 1.5])

    # =================================================
    # INFORMACION
    # =================================================

    with col_info:

        st.write(f"Fecha: {reporte['Fecha']}")
        st.write(f"Área: {reporte['Area']}")
        st.write(f"Problema: {reporte['Problema']}")
        st.write(f"Descripción: {reporte['Descripcion']}")
        st.write(f"Prioridad: {reporte['Prioridad']}")

        estados = [
            "Pendiente",
            "En proceso",
            "Resuelto"
        ]

        nuevo_estado = st.selectbox(
            "Estado del reporte",
            estados,
            index=estados.index(reporte["Estado"])
        )

        if st.button("Actualizar estado"):

            df.loc[
                df["ID"] == reporte["ID"],
                "Estado"
            ] = nuevo_estado

            df.to_csv(RUTA_CSV, index=False)

            st.success("Estado actualizado")

            st.rerun()

    # =================================================
    # IMAGEN
    # =================================================

    with col_imagen:

        st.subheader("Evidencia")

        if (
            pd.notna(reporte["Imagen"])
            and reporte["Imagen"] != ""
            and os.path.exists(reporte["Imagen"])
        ):

            st.image(
                reporte["Imagen"],
                use_container_width=True
            )

        else:

            st.warning("No hay evidencia disponible")

# =====================================================
# DESCARGAR CSV
# =====================================================

st.divider()

with open(RUTA_CSV, "rb") as archivo:

    st.download_button(
        label="Descargar reportes CSV",
        data=archivo,
        file_name="reportes.csv",
        mime="text/csv"
    )

