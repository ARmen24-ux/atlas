import pandas as pd

# =====================================================
# ESQUEMA OFICIAL DEL SISTEMA ATLAS
# =====================================================

ESQUEMA_BASE = {
    "ID": "int",
    "Fecha": "str",
    "TipoUsuario": "str",
    "Nombre": "str",
    "Correo": "str",
    "Edificio": "str",
    "Area": "str",
    "Activo": "str",
    "Categoria": "str",
    "Descripcion": "str",
    "Impacto": "str",
    "Estado": "str",
    "Prioridad": "str",
    "Imagen": "str"
}

# =====================================================
# FUNCIÓN DE BLINDAJE
# =====================================================

def asegurar_esquema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garantiza que el DataFrame tenga todas las columnas del sistema ATLAS.
    Si faltan, las crea automáticamente sin romper la app.
    """

    df.columns = df.columns.str.strip()

    for col, tipo in ESQUEMA_BASE.items():
        if col not in df.columns:
            df[col] = "Sin dato"

    return df
