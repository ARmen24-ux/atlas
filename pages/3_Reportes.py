import streamlit as st
import pandas as pd
import os

from utils.reportes_db import cargar_reportes


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
# CARGA
# =====================================================


try:

    df = cargar_reportes()


except Exception as e:

    st.error(
        "No fue posible cargar los reportes."
    )

    st.exception(e)

    st.stop()



if df.empty:

    st.info(
        "Actualmente no existen reportes registrados."
    )

    st.stop()



# =====================================================
# NORMALIZACIÓN
# =====================================================


df["fecha"] = pd.to_datetime(
    df["fecha"],
    errors="coerce"
)



df = df.sort_values(
    "fecha",
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

        df_filtrado["folio"]
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

        ["Todos"]
        +
        sorted(
            df["estado"]
            .dropna()
            .unique()
            .tolist()
        )

    )



with col2:

    prioridad = st.selectbox(

        "Prioridad",

        ["Todos"]
        +
        sorted(
            df["prioridad"]
            .dropna()
            .unique()
            .tolist()
        )

    )



with col3:

    edificio = st.selectbox(

        "Edificio",

        ["Todos"]
        +
        sorted(
            df["edificio"]
            .dropna()
            .unique()
            .tolist()
        )

    )



if estado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["estado"] == estado
    ]



if prioridad != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["prioridad"] == prioridad
    ]



if edificio != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["edificio"] == edificio
    ]



# =====================================================
# RESULTADOS
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
# TABLA
# =====================================================


st.subheader(
    "📑 Reportes registrados"
)



tabla = df_filtrado[

[
"folio",
"fecha",
"edificio",
"area",
"categoria",
"prioridad",
"estado"
]

].copy()



tabla["fecha"] = tabla["fecha"].dt.strftime(
    "%d/%m/%Y %H:%M"
)



tabla.columns=[

"Folio",
"Fecha",
"Edificio",
"Área",
"Categoría",
"Prioridad",
"Estado"

]



seleccion = st.dataframe(

    tabla,

    use_container_width=True,

    hide_index=True,

    selection_mode="single-row",

    on_select="rerun"

)



# =====================================================
# EXPORTAR CONSULTA
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
# DETALLE
# =====================================================


st.divider()

st.subheader(
    "🔎 Detalle del reporte"
)



if seleccion.selection.rows:


    indice = seleccion.selection.rows[0]


    reporte = df_filtrado.iloc[indice]



    col1,col2,col3,col4 = st.columns(4)



    col1.metric(
        "Folio",
        reporte["folio"]
    )


    col2.metric(
        "Estado",
        reporte["estado"]
    )


    col3.metric(
        "Prioridad",
        reporte["prioridad"]
    )


    col4.metric(

        "Fecha",

        reporte["fecha"]
        .strftime("%d/%m/%Y")

    )



    st.divider()



    st.markdown(
        "### 📍 Ubicación"
    )


    st.write(
        f"""
        **Edificio:** {reporte.get('edificio','N/A')}

        **Área:** {reporte.get('area','N/A')}

        **Activo:** {reporte.get('activo','No registrado')}
        """
    )



    st.markdown(
        "### 🏷 Clasificación"
    )


    st.write(
        f"""
        **Categoría:** {reporte.get('categoria','N/A')}

        **Impacto:** {reporte.get('impacto','No registrado')}
        """
    )



    st.markdown(
        "### 📝 Descripción"
    )


    st.info(

        reporte.get(
            "descripcion",
            "Sin descripción"
        )

    )



    st.markdown(
        "### 📷 Evidencia inicial"
    )


    evidencia = reporte.get(
        "evidencia_url",
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