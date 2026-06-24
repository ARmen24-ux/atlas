import pandas as pd
import os
from datetime import datetime


# =====================================================
# CONFIGURACIÓN
# =====================================================

RUTA_COMENTARIOS = "data/comentarios.csv"


# =====================================================
# ESQUEMA OFICIAL DE COMENTARIOS ATLAS
# =====================================================

COLUMNAS_COMENTARIOS = {
    "ID": "",
    "Folio": "",
    "Fecha": "",
    "Usuario": "",
    "Comentario": ""
}


# =====================================================
# INICIALIZAR ARCHIVO
# =====================================================

def iniciar_comentarios():

    if not os.path.exists(RUTA_COMENTARIOS):

        df = pd.DataFrame(
            columns=COLUMNAS_COMENTARIOS.keys()
        )

        df.to_csv(
            RUTA_COMENTARIOS,
            index=False
        )


# =====================================================
# ASEGURAR ESQUEMA
# =====================================================

def asegurar_esquema_comentarios(df):

    # Limpiar espacios
    df.columns = df.columns.str.strip()


    # Compatibilidad versiones anteriores
    if "reporte_id" in df.columns:

        df["Folio"] = df["reporte_id"]

        df.drop(
            columns=["reporte_id"],
            inplace=True
        )


    # Crear columnas faltantes
    for columna, valor in COLUMNAS_COMENTARIOS.items():

        if columna not in df.columns:

            df[columna] = valor


    # Orden oficial

    df = df[
        list(COLUMNAS_COMENTARIOS.keys())
    ]


    return df



# =====================================================
# AGREGAR COMENTARIO
# =====================================================

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


    df = asegurar_esquema_comentarios(df)


    nuevo_id = (
        len(df) + 1
    )


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
        [
            df,
            pd.DataFrame([nuevo])
        ],
        ignore_index=True
    )


    df.to_csv(
        RUTA_COMENTARIOS,
        index=False
    )



# =====================================================
# OBTENER COMENTARIOS DE UN TICKET
# =====================================================

def obtener_comentarios(folio):

    iniciar_comentarios()


    df = pd.read_csv(
        RUTA_COMENTARIOS,
        keep_default_na=False
    )


    df = asegurar_esquema_comentarios(df)


    return df[
        df["Folio"] == folio
    ]
