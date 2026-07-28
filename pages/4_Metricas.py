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

st.title("📊 Métricas ATLAS")

st.caption(
    "Indicadores de desempeño de incidencias registradas"
)


st.divider()



# =====================================================
# CARGA DE DATOS
# =====================================================


try:

    df = cargar_reportes()


except Exception as e:

    st.error(
        "No fue posible cargar las métricas."
    )

    st.exception(e)

    st.stop()



if df.empty:

    st.info(
        "No existen datos suficientes para generar métricas."
    )

    st.stop()



# =====================================================
# VALIDACIÓN
# =====================================================


columnas = [

    "folio",
    "estado",
    "prioridad"

]


faltantes = [

    c for c in columnas
    if c not in df.columns

]


if faltantes:

    st.error(
        f"Faltan columnas necesarias: {faltantes}"
    )

    st.stop()



# =====================================================
# KPI PRINCIPALES
# =====================================================


total_reportes = len(df)



pendientes = len(

    df[
        df["estado"]
        .str.lower()
        .isin(
            [
                "pendiente",
                "en revisión",
                "asignado",
                "en proceso"
            ]
        )
    ]

)



completados = len(

    df[
        df["estado"]
        .str.lower()
        ==
        "completado"
    ]

)



prioridad_alta = len(

    df[
        df["prioridad"]
        .str.lower()
        ==
        "alta"
    ]

)



# =====================================================
# TARJETAS KPI
# =====================================================


st.subheader(
    "📌 Indicadores generales"
)



col1, col2, col3, col4 = st.columns(4)



with col1:

    st.metric(

        "Total reportes",

        total_reportes

    )



with col2:

    st.metric(

        "Pendientes",

        pendientes

    )



with col3:

    st.metric(

        "Completados",

        completados

    )



with col4:

    st.metric(

        "Prioridad alta",

        prioridad_alta

    )



st.divider()



# =====================================================
# DISTRIBUCIÓN POR ESTADO
# =====================================================


st.subheader(
    "📍 Reportes por estado"
)



estado_df = (

    df["estado"]

    .value_counts()

    .reset_index()

)



estado_df.columns = [

    "Estado",

    "Cantidad"

]



fig_estado = px.bar(

    estado_df,

    x="Estado",

    y="Cantidad",

    text="Cantidad",

    title="Distribución actual de tickets"

)



st.plotly_chart(

    fig_estado,

    use_container_width=True

)



# =====================================================
# DISTRIBUCIÓN POR PRIORIDAD
# =====================================================


st.subheader(
    "⚠️ Reportes por prioridad"
)



prioridad_df = (

    df["prioridad"]

    .value_counts()

    .reset_index()

)



prioridad_df.columns = [

    "Prioridad",

    "Cantidad"

]



fig_prioridad = px.pie(

    prioridad_df,

    names="Prioridad",

    values="Cantidad",

    title="Distribución de prioridades"

)



st.plotly_chart(

    fig_prioridad,

    use_container_width=True

)

# =====================================================
# FASE 2
# ANÁLISIS OPERATIVO
# =====================================================


st.divider()


st.header(
    "📈 Análisis operativo"
)



# =====================================================
# REPORTES POR EDIFICIO
# =====================================================


st.subheader(
    "🏢 Reportes por edificio"
)



if "edificio" in df.columns:


    edificio_df = (

        df["edificio"]

        .value_counts()

        .reset_index()

    )


    edificio_df.columns = [

        "Edificio",

        "Cantidad"

    ]



    fig_edificio = px.bar(

        edificio_df,

        x="Edificio",

        y="Cantidad",

        text="Cantidad",

        title="Concentración de incidencias por edificio"

    )


    st.plotly_chart(

        fig_edificio,

        use_container_width=True

    )


else:

    st.info(
        "No existe información de edificios."
    )



# =====================================================
# CATEGORÍAS FRECUENTES
# =====================================================


st.subheader(
    "🔧 Principales categorías de falla"
)



if "categoria" in df.columns:


    categoria_df = (

        df["categoria"]

        .value_counts()

        .head(10)

        .reset_index()

    )


    categoria_df.columns = [

        "Categoría",

        "Cantidad"

    ]



    fig_categoria = px.bar(

        categoria_df,

        x="Cantidad",

        y="Categoría",

        orientation="h",

        text="Cantidad",

        title="Categorías con mayor frecuencia"

    )


    st.plotly_chart(

        fig_categoria,

        use_container_width=True

    )


else:

    st.info(
        "No existe información de categorías."
    )



# =====================================================
# TENDENCIA TEMPORAL
# =====================================================


st.subheader(
    "📅 Tendencia mensual"
)



if "fecha" in df.columns:


    df["fecha"] = pd.to_datetime(

        df["fecha"],

        errors="coerce"

    )


    tendencia = (

        df

        .dropna(subset=["fecha"])

        .groupby(

            df["fecha"]
            .dt
            .to_period("M")

        )

        .size()

        .reset_index()

    )


    tendencia.columns = [

        "Mes",

        "Cantidad"

    ]


    tendencia["Mes"] = (

        tendencia["Mes"]

        .astype(str)

    )



    fig_tendencia = px.line(

        tendencia,

        x="Mes",

        y="Cantidad",

        markers=True,

        title="Evolución mensual de reportes"

    )


    st.plotly_chart(

        fig_tendencia,

        use_container_width=True

    )



# =====================================================
# ÁREAS CRÍTICAS
# =====================================================


st.subheader(
    "📍 Áreas con mayor número de incidencias"
)



if "area" in df.columns:


    area_df = (

        df["area"]

        .value_counts()

        .head(10)

        .reset_index()

    )


    area_df.columns = [

        "Área",

        "Cantidad"

    ]



    fig_area = px.bar(

        area_df,

        x="Área",

        y="Cantidad",

        text="Cantidad",

        title="Carga de mantenimiento por área"

    )


    st.plotly_chart(

        fig_area,

        use_container_width=True

    )


else:

    st.info(
        "No existe información de áreas."
    )

# =====================================================
# FASE 3
# SLA Y DESEMPEÑO OPERATIVO
# =====================================================


st.divider()


st.header(
    "⏱ SLA y desempeño operativo"
)



# =====================================================
# PREPARACIÓN DE FECHAS
# =====================================================


df_sla = df.copy()



df_sla["fecha"] = pd.to_datetime(

    df_sla["fecha"],

    errors="coerce"

)



if "fecha_cierre" in df_sla.columns:


    df_sla["fecha_cierre"] = pd.to_datetime(

        df_sla["fecha_cierre"],

        errors="coerce"

    )



# =====================================================
# TIEMPO PROMEDIO DE RESOLUCIÓN
# =====================================================


st.subheader(
    "⏱ Tiempo promedio de resolución"
)



if "fecha_cierre" in df_sla.columns:


    cerrados = df_sla[

        df_sla["fecha_cierre"].notna()

    ].copy()



    if not cerrados.empty:


        cerrados["horas_resolucion"] = (

            cerrados["fecha_cierre"]

            -
            cerrados["fecha"]

        ).dt.total_seconds() / 3600



        promedio = round(

            cerrados["horas_resolucion"]

            .mean(),

            2

        )



        st.metric(

            "Horas promedio",

            f"{promedio} h"

        )


    else:


        st.info(
            "No existen tickets cerrados para calcular SLA."
        )


else:


    st.info(
        "La información de cierre todavía no está disponible."
    )



# =====================================================
# CUMPLIMIENTO SLA
# =====================================================


st.subheader(
    "📊 Cumplimiento SLA"
)



if "fecha_cierre" in df_sla.columns:


    sla_data = df_sla[

        df_sla["fecha_cierre"].notna()

    ].copy()



    if not sla_data.empty:


        def obtener_sla(prioridad):

            prioridad = str(prioridad).lower()


            if prioridad == "alta":

                return 24


            elif prioridad == "media":

                return 72


            else:

                return 168



        sla_data["sla_horas"] = (

            sla_data["prioridad"]

            .apply(obtener_sla)

        )



        sla_data["horas_real"] = (

            sla_data["fecha_cierre"]

            -

            sla_data["fecha"]

        ).dt.total_seconds() / 3600



        sla_data["cumple"] = (

            sla_data["horas_real"]

            <=

            sla_data["sla_horas"]

        )



        cumplimiento = round(

            sla_data["cumple"]

            .mean()

            *

            100,

            1

        )



        col1, col2 = st.columns(2)



        with col1:

            st.metric(

                "Cumplimiento SLA",

                f"{cumplimiento}%"

            )



        with col2:

            fuera = len(

                sla_data[

                    sla_data["cumple"] == False

                ]

            )


            st.metric(

                "Fuera SLA",

                fuera

            )



# =====================================================
# AGING DE TICKETS ABIERTOS
# =====================================================


st.subheader(
    "📅 Aging de tickets abiertos"
)



abiertos = df_sla[

    ~df_sla["estado"]

    .str.lower()

    .isin(

        [

            "completado",

            "cancelado"

        ]

    )

].copy()



if not abiertos.empty:


    ahora = pd.Timestamp.now()



    abiertos["dias_abierto"] = (

        ahora

        -

        abiertos["fecha"]

    ).dt.days



    def rango_edad(dias):

        if dias <= 1:

            return "0-24 horas"


        elif dias <= 3:

            return "1-3 días"


        else:

            return "+3 días"



    abiertos["rango"] = (

        abiertos["dias_abierto"]

        .apply(rango_edad)

    )



    aging = (

        abiertos["rango"]

        .value_counts()

        .reset_index()

    )



    aging.columns = [

        "Antigüedad",

        "Cantidad"

    ]



    fig_aging = px.bar(

        aging,

        x="Antigüedad",

        y="Cantidad",

        text="Cantidad",

        title="Antigüedad de incidencias abiertas"

    )



    st.plotly_chart(

        fig_aging,

        use_container_width=True

    )


else:


    st.info(
        "No existen tickets abiertos."
    )

# =====================================================
# PIE DE PÁGINA
# =====================================================


st.caption(

    "Módulo de análisis ATLAS - Solo consulta"

)