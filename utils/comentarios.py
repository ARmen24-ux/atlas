import pandas as pd
import os
from datetime import datetime

RUTA_COMENTARIOS = "data/comentarios.csv"


def iniciar_comentarios():

    if not os.path.exists(RUTA_COMENTARIOS):

        df = pd.DataFrame(columns=[
            "ID",
            "Folio",
            "Fecha",
            "Usuario",
            "Comentario"
        ])

        df.to_csv(
            RUTA_COMENTARIOS,
            index=False
        )


def agregar_comentario(
    folio,
    usuario,
    comentario
):

    iniciar_comentarios()

    df = pd.read_csv(
        RUTA_COMENTARIOS,
        keep_default_na=False
    )

    nuevo_id = len(df) + 1

    nuevo = {
        "ID": nuevo_id,
        "Folio": folio,
        "Fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        ),
        "Usuario": usuario,
        "Comentario": comentario
    }

    df = pd.concat(
        [df, pd.DataFrame([nuevo])],
        ignore_index=True
    )

    df.to_csv(
        RUTA_COMENTARIOS,
        index=False
    )


def obtener_comentarios(folio):

    iniciar_comentarios()

    df = pd.read_csv(
        RUTA_COMENTARIOS,
        keep_default_na=False
    )

    return df[
        df["Folio"] == folio
    ]