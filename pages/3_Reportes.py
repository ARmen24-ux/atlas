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

st.title("Consulta de Reportes")

st.caption(
    "Consulta pública de incidencias registradas en ATLAS"
)


st.divider()



# =====================================================
# CARGA
# =====================================================

try:
    df = cargar_reportes()
    
    # Mostrar columnas en formato organizado
    st.write("### Estructura de columnas disponibles")
    
    # Crear 3 columnas para mostrar los nombres
    col1, col2, col3 = st.columns(3)
    
    # Obtener lista de columnas
    columnas = df.columns.tolist()
    
    # Dividir en grupos
    chunk_size = len(columnas) // 3
    if len(columnas) % 3 != 0:
        chunk_size += 1
    
    with col1:
        st.write("**Columnas 1-{}**".format(min(chunk_size, len(columnas))))
        for col in columnas[:chunk_size]:
            st.write(f"• {col}")
    
    with col2:
        inicio = chunk_size
        fin = min(chunk_size * 2, len(columnas))
        st.write("**Columnas {}-{}**".format(inicio+1, fin))
        for col in columnas[inicio:fin]:
            st.write(f"• {col}")
    
    with col3:
        inicio = chunk_size * 2
        st.write("**Columnas {}-{}**".format(inicio+1, len(columnas)))
        for col in columnas[inicio:]:
            st.write(f"• {col}")
    
    st.divider()
    
    # Mostrar los datos en tabla
    st.write("### 📊 Vista previa de datos")
    st.dataframe(df.head(10), use_container_width=True)
    
except Exception as e:
    st.error("No fue posible cargar los reportes.")
    st.exception(e)
    st.stop()



# =====================================================
# NORMALIZACIÓN
# =====================================================


df["FechaCreacion"] = pd.to_datetime(
    df["Fecha"],
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

        ["Todos"]
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

        ["Todos"]
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

        ["Todos"]
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
"Folio",
"FechaCreacion",
"Edificio",
"Área",
"Categoría",
"Prioridad",
"Estado"
]

].copy()



tabla["FechaCreacion"] = tabla["FechaCreacion"].dt.strftime(
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

        reporte["Fecha"]
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