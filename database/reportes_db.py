import pandas as pd
import os

from utils.data_guard import asegurar_esquema

RUTA_REPORTES = "data/reportes.csv"


def cargar_reportes():

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


def guardar_reportes(df):

    try:

        df.to_csv(
            RUTA_REPORTES,
            index=False
        )

    except Exception as e:

        raise Exception(
            f"Error al guardar reportes: {e}"
        )
    