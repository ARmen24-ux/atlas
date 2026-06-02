import streamlit as st
import pandas as pd
import os

from utils.data_guard import asegurar_esquema

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="ATLAS",
    layout="wide"
)

# =====================================================
# ESTILO
# =====================================================

st.markdown("""
<style>

.main-title{
    text-align:center;
    font-size:60px;
    font-weight:700;
}

.subtitle{
    text-align:center;
    color:#888;
    font-size:20px;
}

.kpi-card{
    padding:10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CARGA DE DATOS
# =====================================================

RUTA_CSV = "data/reportes.csv"

if not os.path.exists(RUTA_CSV):

    st.error(
        "No existe data/reportes.csv"
    )

    st.stop()

df = pd.read_csv(
    RUTA_CSV,
    keep_default_na=False
)

df = asegurar_esquema(df)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    """
    <div class='main-title'>
    ATLAS
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class='subtitle'>
    Sistema Institucional de Gestión de Mantenimiento
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

st.info(
    """
ATLAS permite registrar, monitorear y dar seguimiento
a incidencias de mantenimiento dentro de las instalaciones
de la universidad.

La plataforma centraliza reportes, evidencias fotográficas,
historial de movimientos y métricas operativas para mejorar
los tiempos de respuesta y la trazabilidad de cada incidencia.
"""
)

# =====================================================
# KPI
# =====================================================

total_tickets = len(df)

pendientes = len(
    df[
        df["Estado"] == "Pendiente"
    ]
)

en_proceso = len(
    df[
        df["Estado"].isin(
            [
                "Asignado",
                "En proceso"
            ]
        )
    ]
)

resueltos = len(
    df[
        df["Estado"] == "Resuelto"
    ]
)

cerrados = len(
    df[
        df["Estado"] == "Cerrado"
    ]
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Tickets",
        total_tickets
    )

with col2:
    st.metric(
        "Pendientes",
        pendientes
    )

with col3:
    st.metric(
        "En proceso",
        en_proceso
    )

with col4:
    st.metric(
        "Resueltos",
        resueltos
    )

with col5:
    st.metric(
        "Cerrados",
        cerrados
    )

st.divider()

# =====================================================
# FLUJO
# =====================================================

col_a, col_b = st.columns(2)

with col_a:

    st.subheader(
        "Flujo de atención"
    )

    st.markdown(
        """
1. Reporte de incidencia

2. Validación

3. Asignación

4. Atención

5. Resolución

6. Verificación

7. Cierre
"""
    )

with col_b:

    st.subheader(
        "Beneficios"
    )

    st.markdown(
        """
Evidencias fotográficas

Historial completo

Seguimiento en tiempo real

Indicadores operativos

Control de mantenimiento

Trazabilidad de reportes

Centralización de incidencias
"""
    )

st.divider()

# =====================================================
# ESTADÍSTICAS RÁPIDAS
# =====================================================

st.subheader(
    "Distribución por prioridad"
)

prioridad_counts = (
    df["Prioridad"]
    .value_counts()
)

if not prioridad_counts.empty:

    st.bar_chart(
        prioridad_counts
    )

st.divider()

# =====================================================
# ÚLTIMOS REPORTES
# =====================================================

st.subheader(
    "Últimos reportes registrados"
)

columnas = [
    "Folio",
    "FechaCreacion",
    "Edificio",
    "Area",
    "Categoria",
    "Prioridad",
    "Estado"
]

columnas = [
    c
    for c in columnas
    if c in df.columns
]

if len(df) > 0:

    tabla = (
        df[columnas]
        .sort_values(
            by="FechaCreacion",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No existen reportes registrados."
    )

st.divider()

# =====================================================
# INFORMACIÓN DEL SISTEMA
# =====================================================

st.subheader(
    "Acerca del sistema"
)

st.write(
    """
ATLAS fue desarrollado como una plataforma para la gestión
de incidencias de mantenimiento dentro de la Universidad
Tecnológica de Guaymas.

Su objetivo es facilitar el reporte de fallas por parte de
alumnos, docentes y personal administrativo, permitiendo
adjuntar evidencias y dar seguimiento al proceso de atención
hasta el cierre de cada reporte.
"""
)

# =====================================================
# PIE DE PÁGINA
# =====================================================

st.caption(
    "ATLAS • Sistema Institucional de Gestión de Mantenimiento"
)