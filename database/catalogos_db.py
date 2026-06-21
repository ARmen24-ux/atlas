import pandas as pd

RUTA_UBICACIONES = "data/catalogo_ubicaciones.csv"
RUTA_ACTIVOS = "data/catalogo_activos.csv"


def cargar_ubicaciones():

    df = pd.read_csv(
        RUTA_UBICACIONES
    )

    df.columns = df.columns.str.strip()

    return df


def cargar_activos():

    df = pd.read_csv(
        RUTA_ACTIVOS
    )

    df.columns = df.columns.str.strip()

    return df
