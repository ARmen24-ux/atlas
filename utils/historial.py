from datetime import datetime
from database.supabase_client import supabase


def registrar_movimiento(
    folio,
    usuario,
    accion,
    detalle=""
):
    try:

        respuesta = (
            supabase
            .table("historial")
            .insert({
                "Folio": folio,
                "Fecha": datetime.now().isoformat(),
                "Usuario": usuario,
                "Accion": accion,
                "Detalle": detalle
            })
            .execute()
        )

        return respuesta

    except Exception as e:

        print(f"Error guardando historial: {e}")

        return None