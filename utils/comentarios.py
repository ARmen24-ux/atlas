from datetime import datetime

import pandas as pd

from database.supabase_client import supabase


# =====================================================
# AGREGAR COMENTARIO
# =====================================================

def agregar_comentario(
    folio,
    usuario,
    comentario
):

    try:

        supabase.table(
            "comentarios"
        ).insert({

            "Folio": folio,

            "Fecha": datetime.now().isoformat(),

            "Usuario": usuario,

            "Comentario": comentario

        }).execute()

    except Exception as e:

        import streamlit as st

        st.error(
            f"Error guardando comentario: {e}"
        )

        raise


# =====================================================
# OBTENER COMENTARIOS
# =====================================================

def obtener_comentarios(folio):

    try:

        respuesta = (
            supabase
            .table("comentarios")
            .select("*")
            .eq(
                "Folio",
                folio
            )
            .order(
                "Fecha",
                desc=True
            )
            .execute()
        )

        return pd.DataFrame(
            respuesta.data
        )

    except Exception as e:

        print(
            f"Error consultando comentarios: {e}"
        )

        return pd.DataFrame()