from datetime import datetime

from database.supabase_client import supabase


def registrar_movimiento(
    folio,
    usuario,
    accion,
    detalle=""
):

    try:

        supabase.table(
            "historial"
        ).insert({

            "Fecha": datetime.now().isoformat(),

            "Folio": folio,

            "Usuario": usuario,

            "Accion": accion,

            "Detalle": detalle

        }).execute()

    except Exception as e:

        print(
            f"Error guardando historial: {e}"
        )