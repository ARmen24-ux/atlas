import pandas as pd
import os


RUTA_UBICACIONES = "data/catalogo_ubicaciones.csv"
RUTA_ACTIVOS = "data/catalogo_activos.csv"
RUTA_CATEGORIAS = "data/catalogo_categorias.csv"
RUTA_PRIORIDADES = "data/catalogo_prioridades.csv"
RUTA_IMPACTOS = "data/catalogo_impactos.csv"


def cargar_csv(ruta):

    if not os.path.exists(ruta):
        return pd.DataFrame()

    df = pd.read_csv(ruta)

    df.columns = df.columns.str.strip()

    return df


def cargar_ubicaciones():
    return cargar_csv(RUTA_UBICACIONES)


def cargar_activos():
    return cargar_csv(RUTA_ACTIVOS)


def cargar_categorias():
    return cargar_csv(RUTA_CATEGORIAS)


def cargar_prioridades():
    return cargar_csv(RUTA_PRIORIDADES)


def cargar_impactos():
    return cargar_csv(RUTA_IMPACTOS)