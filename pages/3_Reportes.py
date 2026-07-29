import streamlit as st
import pandas as pd
import os

from database.reportes_db import cargar_reportes


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="ATLAS - Reportes",
    page_icon="📋",
    layout="wide"
)


# =====================================================
# TITULO
# =====================================================

st.title("📋 Consulta de Reportes")

st.caption(
    "Consulta pública de incidencias registradas en ATLAS"
)

st.divider()



# =====================================================
# CARGA DE DATOS
# =====================================================

try:

    df = cargar_reportes()

except Exception as e:

    st.error(
        "No fue posible cargar los reportes."
    )

    st.exception(e)

    st.stop()



# =====================================================
# VALIDACIÓN DE ESQUEMA
# =====================================================

COLUMNAS_BASE = [

    "Folio",
    "FechaCreacion",
    "Edificio",
    "Area",
    "Categoria",
    "Prioridad",
    "Estado"

]


faltantes = [

    col for col in COLUMNAS_BASE
    if col not in df.columns

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


df = df.sort_values(
    "FechaCreacion",
    ascending=False
)



# =====================================================
# BUSCADOR
# =====================================================

st.subheader(
    "🔎 Buscar reporte"
)


busqueda = st.text_input(

    "Buscar por folio",

    placeholder="Ejemplo: UTG-2026-00015"

)



df_filtrado = df.copy()



if busqueda:

    df_filtrado = df_filtrado[

        df_filtrado["Folio"]
        .astype(str)
        .str.contains(
            busqueda,
            case=False,
            na=False
        )

    ]



# =====================================================
# FILTROS
# =====================================================

st.subheader(
    "🎛 Filtros"
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



with col3:

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




if estado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Estado"] == estado
    ]



if prioridad != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Prioridad"] == prioridad
    ]



if edificio != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["Edificio"] == edificio
    ]



# =====================================================
# MÉTRICAS
# =====================================================

st.divider()


col1, col2 = st.columns(2)


with col1:

    st.metric(

        "Reportes encontrados",

        len(df_filtrado)

    )


with col2:

    st.metric(

        "Total histórico",

        len(df)

    )



# =====================================================
# TABLA PRINCIPAL
# =====================================================

st.subheader(
    "📑 Reportes registrados"
)



tabla = df_filtrado[

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



tabla["FechaCreacion"] = tabla[
    "FechaCreacion"
].dt.strftime(
    "%d/%m/%Y %H:%M"
)



tabla = tabla.rename(

    columns={

        "FechaCreacion": "Fecha",
        "Area": "Área",
        "Categoria": "Categoría"

    }

)



seleccion = st.dataframe(

    tabla,

    use_container_width=True,

    hide_index=True,

    selection_mode="single-row",

    on_select="rerun"

)



# =====================================================
# EXPORTACIÓN
# =====================================================

st.download_button(

    label="📥 Descargar consulta",

    data=tabla.to_csv(
        index=False
    ),

    file_name="reportes_consulta.csv",

    mime="text/csv"

)



# =====================================================
# DETALLE DEL REPORTE
# =====================================================

st.divider()


st.subheader(
    "🔎 Detalle del reporte"
)



if seleccion.selection.rows:


    indice = seleccion.selection.rows[0]


    reporte = df_filtrado.iloc[indice]



    col1, col2, col3, col4 = st.columns(4)



    col1.metric(

        "Folio",

        reporte["Folio"]

    )



    col2.metric(

        "Estado",

        reporte["Estado"]

    )



    col3.metric(

        "Prioridad",

        reporte["Prioridad"]

    )



    col4.metric(

        "Fecha",

        reporte["FechaCreacion"]
        .strftime("%d/%m/%Y")

    )



    st.divider()



    st.markdown(
        "### 📍 Ubicación"
    )


    st.write(

        f"""
        **Edificio:** {reporte.get('Edificio','N/A')}

        **Área:** {reporte.get('Area','N/A')}

        **Activo:** {reporte.get('Activo','No registrado')}
        """

    )



    st.markdown(
        "### 🏷 Clasificación"
    )


    st.write(

        f"""
        **Categoría:** {reporte.get('Categoria','N/A')}

        **Impacto:** {reporte.get('Impacto','No registrado')}
        """

    )



    st.markdown(
        "### 📝 Descripción"
    )


    st.info(

        reporte.get(

            "Descripcion",

            "Sin descripción"

        )

    )



    st.markdown(
        "### 📷 Evidencia inicial"
    )



    evidencia = reporte.get(

        "ImagenApertura",

        None

    )



    if evidencia and os.path.exists(evidencia):

        st.image(

            evidencia,

            use_container_width=True

        )

    else:

        st.info(
            "Sin evidencia fotográfica."
        )



else:


    st.info(

        "Seleccione un reporte para consultar detalles."

    )