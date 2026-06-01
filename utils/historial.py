import pandas as pd
import os
from datetime import datetime

RUTA_HISTORIAL = "data/historial.csv"

COLUMNAS_HISTORIAL = [
    "Fecha",
    "Folio",
    "Usuario",
    "Accion",
    "Detalle"
]

def inicializar_historial():

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(RUTA_HISTORIAL):

        pd.DataFrame(
            columns=COLUMNAS_HISTORIAL
        ).to_csv(
            RUTA_HISTORIAL,
            index=False
        )


def registrar_movimiento(
    folio,
    usuario,
    accion,
    detalle=""
):

    inicializar_historial()

    df = pd.read_csv(
        RUTA_HISTORIAL,
        keep_default_na=False
    )

    nuevo = {
        "Fecha": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "Folio": folio,
        "Usuario": usuario,
        "Accion": accion,
        "Detalle": detalle
    }

    df = pd.concat(
        [df, pd.DataFrame([nuevo])],
        ignore_index=True
    )

    df.to_csv(
        RUTA_HISTORIAL,
        index=False
    )