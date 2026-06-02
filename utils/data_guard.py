import pandas as pd

# =====================================================
# ESQUEMA OFICIAL DE ATLAS
# =====================================================

COLUMNAS_REQUERIDAS = {
    "ID": "",
    "Folio": "",

    "FechaCreacion": "",
    "FechaAsignacion": "",
    "FechaResolucion": "",
    "FechaCierre": "",
    "FechaActualizacion": "",

    "TipoUsuario": "",
    "Nombre": "",
    "Correo": "",

    "Edificio": "",
    "Area": "",
    "UbicacionDetalle": "",

    "Activo": "",
    "Categoria": "",

    "Impacto": "",
    "Prioridad": "",

    "Descripcion": "",

    "Estado": "Pendiente",

    "Responsable": "",

    "ComentarioCierre": "",

    "ImagenApertura": "",
    "ImagenCierre": ""
}

# =====================================================
# ASEGURAR ESQUEMA
# =====================================================

def asegurar_esquema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garantiza que el DataFrame tenga todas las columnas
    requeridas por ATLAS.

    Si una columna no existe se crea automáticamente.
    """

    # Limpiar espacios en nombres de columnas
    df.columns = df.columns.str.strip()

    # Crear columnas faltantes
    for columna, valor_default in COLUMNAS_REQUERIDAS.items():

        if columna not in df.columns:
            df[columna] = valor_default

    # =================================================
    # COMPATIBILIDAD CON VERSIONES ANTERIORES
    # =================================================

    # Imagen -> ImagenApertura
    if "Imagen" in df.columns:

        df["ImagenApertura"] = (
            df["ImagenApertura"]
            .replace("", pd.NA)
            .fillna(df["Imagen"])
        )

        df.drop(
            columns=["Imagen"],
            inplace=True,
            errors="ignore"
        )

    # Fecha -> FechaCreacion
    if "Fecha" in df.columns:

        df["FechaCreacion"] = df["Fecha"]

        df.drop(
            columns=["Fecha"],
            inplace=True,
            errors="ignore"
        )

    # =================================================
    # ORDENAR COLUMNAS
    # =================================================

    columnas_finales = list(COLUMNAS_REQUERIDAS.keys())

    df = df.reindex(columns=columnas_finales)

    return df
