from Services.reportes_backup_service import (
    estado_bloque_actual,
    exportar_bloque
)


def ejecutar_respaldo_si_corresponde():
    """
    Verifica el estado del bloque actual y ejecuta
    el respaldo únicamente cuando corresponde.

    No hace nada si:
    - No existen reportes.
    - El bloque todavía está incompleto.
    - El bloque ya fue respaldado.

    Devuelve información del resultado.
    """

    try:

        estado = estado_bloque_actual()

        # ---------------------------------------------
        # NO HAY REPORTES
        # ---------------------------------------------

        if estado["bloque"] == 0:

            return {
                "ejecutado": False,
                "motivo": "No existen reportes."
            }

        # ---------------------------------------------
        # BLOQUE INCOMPLETO
        # ---------------------------------------------

        if not estado["completo"]:

            return {
                "ejecutado": False,
                "motivo": "El bloque todavía no está completo.",
                "bloque": estado["bloque"],
                "reportes": estado["reportes"]
            }

        # ---------------------------------------------
        # YA FUE RESPALDADO
        # ---------------------------------------------

        if estado["ya_respaldado"]:

            return {
                "ejecutado": False,
                "motivo": "El bloque ya fue respaldado.",
                "bloque": estado["bloque"]
            }

        # ---------------------------------------------
        # EJECUTAR RESPALDO
        # ---------------------------------------------

        resultado = exportar_bloque(
            estado["bloque"]
        )

        return {
            "ejecutado": True,
            "motivo": "Respaldo generado correctamente.",
            "resultado": resultado
        }

    except Exception as e:

        raise Exception(
            f"Error ejecutando respaldo automático: {e}"
        )