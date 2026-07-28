import os
import pandas as pd

from utils.data_guard import asegurar_esquema

# =====================================================
# CONFIGURACIÓN
# =====================================================

RUTA_REPORTES = "data/reportes.csv"


# =====================================================
# CARGAR REPORTES
# =====================================================

def cargar_reportes():

    """
    Carga el archivo de reportes asegurando
    el esquema oficial de ATLAS.
    """

    if not os.path.exists(RUTA_REPORTES):

        df = pd.DataFrame()

        df = asegurar_esquema(df)

        df.to_csv(
            RUTA_REPORTES,
            index=False
        )

        return df

    try:

        df = pd.read_csv(
            RUTA_REPORTES,
            keep_default_na=False
        )

        return asegurar_esquema(df)

    except Exception as e:

        raise Exception(
            f"Error al cargar reportes: {e}"
        )


# =====================================================
# GUARDAR REPORTES
# =====================================================

def guardar_reportes(df):

    """
    Guarda el DataFrame de reportes.
    """

    try:

        df = asegurar_esquema(df)

        df.to_csv(
            RUTA_REPORTES,
            index=False
        )

    except Exception as e:

        raise Exception(
            f"Error al guardar reportes: {e}"
        )


# =====================================================
# OBTENER UN REPORTE
# =====================================================

def obtener_reporte(folio):

    """
    Devuelve un único reporte por folio.
    """

    df = cargar_reportes()

    ticket = df[
        df["Folio"] == folio
    ]

    if ticket.empty:

        return None

    return ticket.iloc[0]


# =====================================================
# FILTRAR REPORTES
# =====================================================

def filtrar_reportes(
    estado=None,
    prioridad=None,
    edificio=None,
    categoria=None
):

    """
    Devuelve reportes filtrados.
    Todos los parámetros son opcionales.
    """

    df = cargar_reportes()

    if estado:

        if isinstance(estado, list):

            df = df[
                df["Estado"].isin(estado)
            ]

        else:

            df = df[
                df["Estado"] == estado
            ]

    if prioridad:

        if isinstance(prioridad, list):

            df = df[
                df["Prioridad"].isin(prioridad)
            ]

        else:

            df = df[
                df["Prioridad"] == prioridad
            ]

    if edificio:

        df = df[
            df["Edificio"] == edificio
        ]

    if categoria:

        df = df[
            df["Categoria"] == categoria
        ]

    return df


# =====================================================
# ACTUALIZAR REPORTE
# =====================================================

def actualizar_reporte(
    folio,
    cambios
):

    """
    Actualiza uno o varios campos de un reporte.

    cambios = {
        "Estado":"Asignado",
        "Responsable":"Juan"
    }
    """

    df = cargar_reportes()

    idx = df.index[
        df["Folio"] == folio
    ]

    if len(idx) == 0:

        raise Exception(
            "Reporte no encontrado."
        )

    idx = idx[0]

    for campo, valor in cambios.items():

        if campo in df.columns:

            df.loc[idx, campo] = valor

    guardar_reportes(df)


# =====================================================
# ESTADÍSTICAS GENERALES
# =====================================================

def estadisticas_generales():

    """
    Devuelve indicadores básicos del sistema.
    """

    df = cargar_reportes()

    return {

        "total": len(df),

        "pendientes": len(
            df[
                df["Estado"] == "Pendiente"
            ]
        ),

        "asignados": len(
            df[
                df["Estado"] == "Asignado"
            ]
        ),

        "en_proceso": len(
            df[
                df["Estado"] == "En proceso"
            ]
        ),

        "resueltos": len(
            df[
                df["Estado"] == "Resuelto"
            ]
        ),

        "cerrados": len(
            df[
                df["Estado"] == "Cerrado"
            ]
        )
    }