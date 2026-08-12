from database.supabase_client import supabase

from Services.evidencias_service import (
    eliminar_imagen_supabase
)


# =====================================================
# OBTENER REPORTE PARA ELIMINACIÓN
# =====================================================

def obtener_datos_eliminacion(folio):
    """
    Obtiene el reporte y la información relacionada
    necesaria antes de eliminarlo.
    """

    try:

        respuesta = (
            supabase
            .table("reportes")
            .select("*")
            .eq("Folio", folio)
            .limit(1)
            .execute()
        )

        if not respuesta.data:

            return None

        reporte = respuesta.data[0]

        return {
            "folio": folio,

            "imagen_apertura": (
                reporte.get("ImagenApertura") or ""
            ).strip(),

            "imagen_cierre": (
                reporte.get("ImagenCierre") or ""
            ).strip()
        }

    except Exception as e:

        raise Exception(
            f"Error preparando eliminación: {e}"
        )


# =====================================================
# ELIMINAR HISTORIAL
# =====================================================

def eliminar_historial(folio):
    """
    Elimina el historial relacionado con el folio.
    """

    try:

        (
            supabase
            .table("historial")
            .delete()
            .eq("Folio", folio)
            .execute()
        )

        return True

    except Exception as e:

        raise Exception(
            f"Error al eliminar historial: {e}"
        )


# =====================================================
# ELIMINAR COMENTARIOS
# =====================================================

def eliminar_comentarios(folio):
    """
    Elimina los comentarios relacionados con el folio.
    """

    try:

        (
            supabase
            .table("comentarios")
            .delete()
            .eq("Folio", folio)
            .execute()
        )

        return True

    except Exception as e:

        raise Exception(
            f"Error al eliminar comentarios: {e}"
        )


# =====================================================
# VERIFICAR REPORTE
# =====================================================

def verificar_reporte_eliminado(folio):
    """
    Comprueba que el reporte ya no exista.
    """

    try:

        respuesta = (
            supabase
            .table("reportes")
            .select("Folio")
            .eq("Folio", folio)
            .limit(1)
            .execute()
        )

        return not bool(respuesta.data)

    except Exception as e:

        raise Exception(
            f"Error verificando eliminación: {e}"
        )


# =====================================================
# ELIMINAR REPORTE COMPLETO
# =====================================================

def eliminar_reporte_completo(folio):
    """
    Elimina un reporte y sus elementos relacionados.

    Incluye:

    - Evidencia de apertura
    - Evidencia de cierre
    - Historial
    - Comentarios
    - Reporte principal
    """

    if not folio:

        return {
            "exito": False,
            "mensaje": "El folio es obligatorio."
        }

    try:

        # =================================================
        # 1. PREPARAR INFORMACIÓN
        # =================================================

        datos = obtener_datos_eliminacion(
            folio
        )

        if datos is None:

            return {
                "exito": False,
                "mensaje": (
                    f"No existe el reporte {folio}."
                )
            }

        # =================================================
        # 2. ELIMINAR EVIDENCIA DE APERTURA
        # =================================================

        if datos["imagen_apertura"]:

            eliminar_imagen_supabase(
                datos["imagen_apertura"]
            )

        # =================================================
        # 3. ELIMINAR EVIDENCIA DE CIERRE
        # =================================================

        if datos["imagen_cierre"]:

            eliminar_imagen_supabase(
                datos["imagen_cierre"]
            )

        # =================================================
        # 4. ELIMINAR HISTORIAL
        # =================================================

        eliminar_historial(
            folio
        )

        # =================================================
        # 5. ELIMINAR COMENTARIOS
        # =================================================

        eliminar_comentarios(
            folio
        )

        # =================================================
        # 6. ELIMINAR REPORTE
        # =================================================

        (
            supabase
            .table("reportes")
            .delete()
            .eq("Folio", folio)
            .execute()
        )

        # =================================================
        # 7. VERIFICAR
        # =================================================

        eliminado = verificar_reporte_eliminado(
            folio
        )

        if not eliminado:

            return {
                "exito": False,
                "mensaje": (
                    f"El reporte {folio} "
                    "no pudo verificarse como eliminado."
                )
            }

        # =================================================
        # 8. RESULTADO
        # =================================================

        return {
            "exito": True,
            "mensaje": (
                f"El reporte {folio} "
                "fue eliminado correctamente."
            )
        }

    except Exception as e:

        return {
            "exito": False,
            "mensaje": (
                f"No fue posible eliminar "
                f"el reporte {folio}: {e}"
            )
        }