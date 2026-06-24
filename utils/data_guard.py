import pandas as pd


# =====================================================
# ESQUEMA OFICIAL DE REPORTES ATLAS
# =====================================================

COLUMNAS_REQUERIDAS = {

    "ID": "",

    "Folio": "",


    # Fechas

    "FechaCreacion": "",

    "FechaAsignacion": "",

    "FechaResolucion": "",

    "FechaCierre": "",

    "FechaActualizacion": "",



    # Usuario

    "TipoUsuario": "",

    "Nombre": "",

    "Correo": "",



    # Ubicación

    "Edificio": "",

    "Area": "",

    "UbicacionDetalle": "",



    # Clasificación

    "Activo": "",

    "Categoria": "",

    "Impacto": "",

    "Prioridad": "",



    # Descripción

    "Descripcion": "",



    # Seguimiento

    "Estado": "Pendiente",

    "Responsable": "",

    "ComentarioCierre": "",



    # Evidencias

    "ImagenApertura": "",

    "ImagenCierre": ""

}



# =====================================================
# ASEGURAR ESQUEMA DE REPORTES
# =====================================================

def asegurar_esquema(df: pd.DataFrame):

    """
    Garantiza que reportes.csv
    tenga la estructura oficial ATLAS.
    """


    if df is None:

        df = pd.DataFrame()



    # Limpiar nombres

    df.columns = (
        df.columns
        .str.strip()
    )



    # =================================================
    # COMPATIBILIDAD VERSIONES ANTERIORES
    # =================================================


    # Imagen antigua

    if "Imagen" in df.columns:


        if "ImagenApertura" not in df.columns:

            df["ImagenApertura"] = (
                df["Imagen"]
            )


        df.drop(
            columns=["Imagen"],
            inplace=True,
            errors="ignore"
        )



    # Fecha antigua

    if "Fecha" in df.columns:


        if "FechaCreacion" not in df.columns:

            df["FechaCreacion"] = (
                df["Fecha"]
            )


        df.drop(
            columns=["Fecha"],
            inplace=True,
            errors="ignore"
        )



    # Crear columnas faltantes

    for columna, valor in COLUMNAS_REQUERIDAS.items():

        if columna not in df.columns:

            df[columna] = valor



    # Orden oficial

    df = df[
        list(COLUMNAS_REQUERIDAS.keys())
    ]



    return df
