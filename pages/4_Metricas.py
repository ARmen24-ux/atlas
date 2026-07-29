import streamlit as st
import pandas as pd
import plotly.express as px

from database.reportes_db import cargar_reportes



# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(

    page_title="ATLAS - Métricas",

    page_icon="📊",

    layout="wide"

)



# =====================================================
# TITULO
# =====================================================

st.title(
    "📊 Métricas de Reportes ATLAS"
)


st.caption(
    "Indicadores estadísticos de incidencias registradas"
)


st.divider()



# =====================================================
# CARGA DE DATOS
# =====================================================

try:

    df = cargar_reportes()


except Exception as e:

    st.error(
        "No fue posible cargar los datos."
    )

    st.exception(e)

    st.stop()



# =====================================================
# VALIDACIÓN DEL ESQUEMA
# =====================================================

COLUMNAS_REQUERIDAS = [

    "Folio",
    "FechaCreacion",
    "Edificio",
    "Area",
    "Categoria",
    "Prioridad",
    "Estado"

]


faltantes = [

    columna
    for columna in COLUMNAS_REQUERIDAS
    if columna not in df.columns

]


if faltantes:

    st.error(

        f"""
        El origen de datos no cumple el esquema oficial de ATLAS.

        Columnas faltantes:

        {faltantes}
        """

    )

    st.stop()



# =====================================================
# NORMALIZACIÓN
# =====================================================

df["FechaCreacion"] = pd.to_datetime(

    df["FechaCreacion"],

    errors="coerce"

)



# eliminar fechas inválidas

df = df.dropna(

    subset=[

        "FechaCreacion"

    ]

)



# =====================================================
# FILTROS DE CONSULTA
# =====================================================

st.subheader(
    "🎛 Filtros de análisis"
)



col1, col2, col3 = st.columns(3)



with col1:

    estado = st.selectbox(

        "Estado",

        [

            "Todos"

        ]
        +
        sorted(

            df["Estado"]
            .dropna()
            .unique()
            .tolist()

        )

    )



with col2:

    edificio = st.selectbox(

        "Edificio",

        [

            "Todos"

        ]
        +
        sorted(

            df["Edificio"]
            .dropna()
            .unique()
            .tolist()

        )

    )



with col3:

    prioridad = st.selectbox(

        "Prioridad",

        [

            "Todos"

        ]
        +
        sorted(

            df["Prioridad"]
            .dropna()
            .unique()
            .tolist()

        )

    )



df_metricas = df.copy()



if estado != "Todos":

    df_metricas = df_metricas[

        df_metricas["Estado"] == estado

    ]



if edificio != "Todos":

    df_metricas = df_metricas[

        df_metricas["Edificio"] == edificio

    ]



if prioridad != "Todos":

    df_metricas = df_metricas[

        df_metricas["Prioridad"] == prioridad

    ]



st.divider()



# =====================================================
# INDICADORES PRINCIPALES
# =====================================================

st.subheader(
    "📌 Indicadores principales"
)



total = len(df_metricas)


pendientes = len(

    df_metricas[

        df_metricas["Estado"]
        .isin(

            [

                "Pendiente",

                "En revisión"

            ]

        )

    ]

)



proceso = len(

    df_metricas[

        df_metricas["Estado"]
        .isin(

            [

                "Asignado",

                "En proceso"

            ]

        )

    ]

)



completados = len(

    df_metricas[

        df_metricas["Estado"]

        ==

        "Completado"

    ]

)



col1, col2, col3, col4 = st.columns(4)



col1.metric(

    "Total reportes",

    total

)



col2.metric(

    "Pendientes",

    pendientes

)



col3.metric(

    "En proceso",

    proceso

)



col4.metric(

    "Completados",

    completados

)



st.divider()



# =====================================================
# DISTRIBUCIÓN POR ESTADO
# =====================================================

st.subheader(

    "📍 Reportes por estado"

)



estado_data = (

    df_metricas["Estado"]

    .value_counts()

    .reset_index()

)



estado_data.columns = [

    "Estado",

    "Cantidad"

]



fig_estado = px.bar(

    estado_data,

    x="Estado",

    y="Cantidad",

    text="Cantidad",

    title="Distribución de estados"

)



st.plotly_chart(

    fig_estado,

    use_container_width=True

)



# =====================================================
# REPORTES POR EDIFICIO
# =====================================================

st.subheader(

    "🏢 Reportes por edificio"

)



edificio_data = (

    df_metricas["Edificio"]

    .value_counts()

    .reset_index()

)



edificio_data.columns = [

    "Edificio",

    "Cantidad"

]



fig_edificio = px.pie(

    edificio_data,

    names="Edificio",

    values="Cantidad",

    title="Distribución por edificio"

)



st.plotly_chart(

    fig_edificio,

    use_container_width=True

)



# =====================================================
# CATEGORÍAS PRINCIPALES
# =====================================================

st.subheader(

    "🏷 Categorías más frecuentes"

)



categoria_data = (

    df_metricas["Categoria"]

    .value_counts()

    .head(10)

    .reset_index()

)



categoria_data.columns = [

    "Categoria",

    "Cantidad"

]



fig_categoria = px.bar(

    categoria_data,

    x="Categoria",

    y="Cantidad",

    text="Cantidad",

    title="Top categorías"

)



st.plotly_chart(

    fig_categoria,

    use_container_width=True

)



# =====================================================
# EVOLUCIÓN TEMPORAL
# =====================================================

st.subheader(

    "📅 Tendencia de creación de reportes"

)



tiempo = (

    df_metricas

    .set_index("FechaCreacion")

    .resample("D")

    .size()

    .reset_index()

)



tiempo.columns = [

    "Fecha",

    "Cantidad"

]



fig_tiempo = px.line(

    tiempo,

    x="Fecha",

    y="Cantidad",

    markers=True,

    title="Reportes creados por día"

)



st.plotly_chart(

    fig_tiempo,

    use_container_width=True

)



# =====================================================
# TABLA RESUMEN
# =====================================================

st.subheader(

    "📑 Resumen de datos"

)



resumen = df_metricas[

    [

        "Folio",

        "FechaCreacion",

        "Edificio",

        "Area",

        "Categoria",

        "Prioridad",

        "Estado"

    ]

].copy()



resumen["FechaCreacion"] = resumen[

    "FechaCreacion"

].dt.strftime(

    "%d/%m/%Y %H:%M"

)



resumen = resumen.rename(

    columns={

        "FechaCreacion":"Fecha",

        "Area":"Área",

        "Categoria":"Categoría"

    }

)



st.dataframe(

    resumen,

    use_container_width=True,

    hide_index=True

)