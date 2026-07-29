import pandas as pd

from database.supabase_client import supabase


# =====================================================
# CONFIGURACIÓN
# =====================================================

TABLA = "reportes"


# =====================================================
# CARGAR REPORTES
# =====================================================

def cargar_reportes():
    """
    Obtiene todos los reportes desde Supabase.
    """

    try:

        respuesta = (
            supabase
            .table(TABLA)
            .select("*")
            .order("FechaCreacion", desc=True)
            .execute()
        )

        datos = respuesta.data or []

        df = pd.DataFrame(datos)

        if df.empty:
            return pd.DataFrame()

        # Convertir fechas
        columnas_fecha = [
            "FechaCreacion",
            "FechaAsignacion",
            "FechaResolucion",
            "FechaCierre",
            "FechaActualizacion"
        ]

        for columna in columnas_fecha:

            if columna in df.columns:

                df[columna] = pd.to_datetime(
                    df[columna],
                    errors="coerce"
                )

        return df

    except Exception as e:

        raise Exception(
            f"Error al cargar reportes desde Supabase: {e}"
        )


# =====================================================
# INSERTAR REPORTE
# =====================================================

def guardar_reporte(datos: dict):
    """
    Inserta un nuevo reporte.
    """

    try:

        respuesta = (
            supabase
            .table(TABLA)
            .insert(datos)
            .execute()
        )

        return respuesta.data

    except Exception as e:

        raise Exception(
            f"Error al guardar reporte: {e}"
        )


# =====================================================
# OBTENER REPORTE POR FOLIO
# =====================================================

def obtener_reporte(folio):
    """
    Devuelve un único reporte.
    """

    try:

        respuesta = (
            supabase
            .table(TABLA)
            .select("*")
            .eq("Folio", folio)
            .limit(1)
            .execute()
        )

        if not respuesta.data:

            return None

        reporte = respuesta.data[0]

        return pd.Series(reporte)

    except Exception as e:

        raise Exception(
            f"Error al obtener reporte: {e}"
        )


# =====================================================
# ACTUALIZAR REPORTE
# =====================================================

def actualizar_reporte(
    folio,
    cambios
):
    """
    Actualiza un reporte usando el Folio.
    """

    try:

        respuesta = (
            supabase
            .table(TABLA)
            .update(cambios)
            .eq("Folio", folio)
            .execute()
        )

        return respuesta.data

    except Exception as e:

        raise Exception(
            f"Error al actualizar reporte: {e}"
        )


# =====================================================
# ELIMINAR REPORTE
# =====================================================

def eliminar_reporte(folio):
    """
    Elimina un reporte.
    """

    try:

        (
            supabase
            .table(TABLA)
            .delete()
            .eq("Folio", folio)
            .execute()
        )

    except Exception as e:

        raise Exception(
            f"Error al eliminar reporte: {e}"
        )