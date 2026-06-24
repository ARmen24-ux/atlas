import pandas as pd

RUTA_UBICACIONES = "data/catalogo_ubicaciones.csv"
RUTA_ACTIVOS = "data/catalogo_activos.csv"
RUTA_CATEGORIAS = "data/catalogo_categorias.csv"
RUTA_PRIORIDADES = "data/catalogo_prioridades.csv"
RUTA_IMPACTOS = "data/catalogo_impactos.csv"


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


def cargar_categorias():

    df = pd.read_csv(
        RUTA_CATEGORIAS
    )

    df.columns = df.columns.str.strip()

    return df


def cargar_prioridades():

    df = pd.read_csv(
        RUTA_PRIORIDADES
    )

    df.columns = df.columns.str.strip()

    return df


def cargar_impactos():

    df = pd.read_csv(
        RUTA_IMPACTOS
    )

    df.columns = df.columns.str.strip()

    return df