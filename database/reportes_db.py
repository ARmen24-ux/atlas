import pandas as pd

from database.supabase_client import supabase

from database.schema import COLUMNAS_REPORTES
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
            return pd.DataFrame(columns=COLUMNAS_REPORTES)

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
    Devuelve un DataFrame filtrado.
    """

    try:

        consulta = (
            supabase
            .table(TABLA)
            .select("*")
        )

        if estado:

            if isinstance(estado, list):

                consulta = consulta.in_("Estado", estado)

            else:

                consulta = consulta.eq(
                    "Estado",
                    estado
                )

        if prioridad:

            if isinstance(prioridad, list):

                consulta = consulta.in_(
                    "Prioridad",
                    prioridad
                )

            else:

                consulta = consulta.eq(
                    "Prioridad",
                    prioridad
                )

        if edificio:

            consulta = consulta.eq(
                "Edificio",
                edificio
            )

        if categoria:

            consulta = consulta.eq(
                "Categoria",
                categoria
            )

        respuesta = consulta.execute()

        df = pd.DataFrame(
            respuesta.data or []
        )

        if df.empty:

            return pd.DataFrame()

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
            f"Error al filtrar reportes: {e}"
        )


# =====================================================
# ESTADÍSTICAS GENERALES
# =====================================================

def estadisticas_generales():
    """
    Indicadores básicos.
    """

    df = cargar_reportes()

    if df.empty:

        return {

            "total": 0,
            "pendientes": 0,
            "asignados": 0,
            "en_proceso": 0,
            "resueltos": 0,
            "cerrados": 0

        }

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


# =====================================================
# EXISTE FOLIO
# =====================================================

def existe_folio(
    folio
):
    """
    Verifica si existe un folio.
    """

    try:

        respuesta = (

            supabase

            .table(TABLA)

            .select(
                "id"
            )

            .eq(
                "Folio",
                folio
            )

            .limit(1)

            .execute()

        )

        return len(
            respuesta.data
        ) > 0

    except:

        return False


# =====================================================
# LISTAR FOLIOS
# =====================================================

def listar_folios():
    """
    Devuelve una lista de folios
    ordenados de forma ascendente.
    """

    try:

        respuesta = (
            supabase
            .table(TABLA)
            .select("Folio")
            .execute()
        )

        folios = [
            r["Folio"]
            for r in respuesta.data or []
            if r.get("Folio")
        ]

        # Orden numérico por el consecutivo final
        folios.sort(
            key=lambda folio: int(
                str(folio).split("-")[-1]
            )
        )

        return folios

    except Exception:
        return []


# =====================================================
# TOTAL REPORTES
# =====================================================

def total_reportes():

    return len(
        cargar_reportes()
    )


# =====================================================
# ÚLTIMO FOLIO
# =====================================================

def ultimo_folio():

    try:

        respuesta = (

            supabase

            .table(TABLA)

            .select(
                "Folio"
            )

            .order(
                "FechaCreacion",
                desc=True
            )

            .limit(1)

            .execute()

        )

        if not respuesta.data:

            return None

        return respuesta.data[0]["Folio"]

    except:

        return None