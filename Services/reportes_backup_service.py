import os
import pandas as pd
from datetime import datetime

from database.supabase_client import supabase

# =====================================================
# CONFIGURACIÓN DEL SISTEMA DE RESPALDO ATLAS
# =====================================================

# Cantidad de reportes necesarios para generar
# automáticamente un nuevo bloque de respaldo.
UMBRAL_REPORTES = 1500


# Tamaño máximo de cada bloque de respaldo.
TAMANO_BLOQUE = 1500


# Carpeta local donde se generarán temporalmente
# los archivos del respaldo.
CARPETA_RESPALDOS = "backups"


# =====================================================
# CONTAR REPORTES
# =====================================================

def obtener_total_reportes():
    """
    Obtiene la cantidad actual de reportes registrados
    en Supabase.
    """

    try:

        respuesta = (
            supabase
            .table("reportes")
            .select("Folio")
            .execute()
        )

        return len(
            respuesta.data or []
        )

    except Exception as e:

        raise Exception(
            f"Error obteniendo total de reportes: {e}"
        )


# =====================================================
# VERIFICAR UMBRAL
# =====================================================

def verificar_umbral():
    """
    Determina si la cantidad actual de reportes
    alcanzó el umbral configurado.

    Devuelve un diccionario con el estado.
    """

    total = obtener_total_reportes()

    return {

        "total_reportes": total,

        "umbral": UMBRAL_REPORTES,

        "umbral_alcanzado": (
            total >= UMBRAL_REPORTES
        )
    }

# =====================================================
# INFORMACIÓN DEL BLOQUE ACTUAL
# =====================================================

def obtener_bloque_actual():
    """
    Determina el bloque al que pertenece el total
    actual de reportes.

    Ejemplo con bloques de 1500:

    1-1500       -> Bloque 1
    1501-3000    -> Bloque 2
    3001-4500    -> Bloque 3
    """

    total = obtener_total_reportes()

    if total == 0:

        return {
            "bloque": 0,
            "inicio": 0,
            "fin": 0,
            "reportes": 0,
            "completo": False
        }

    bloque = (
        (total - 1) // TAMANO_BLOQUE
    ) + 1

    inicio = (
        (bloque - 1) * TAMANO_BLOQUE
    ) + 1

    fin = (
        bloque * TAMANO_BLOQUE
    )

    reportes_en_bloque = (
        total - inicio + 1
    )

    completo = (
        reportes_en_bloque >= TAMANO_BLOQUE
    )

    return {

        "bloque": bloque,

        "inicio": inicio,

        "fin": fin,

        "reportes": reportes_en_bloque,

        "completo": completo
    }

# =====================================================
# VERIFICAR SI UN BLOQUE YA FUE RESPALDADO
# =====================================================

def bloque_ya_respaldado(bloque):
    """
    Comprueba si un bloque ya tiene un respaldo
    registrado como COMPLETADO.
    """

    try:

        respuesta = (
            supabase
            .table("respaldos")
            .select("id")
            .eq("Bloque", bloque)
            .eq("Estado", "COMPLETADO")
            .limit(1)
            .execute()
        )

        return bool(respuesta.data)

    except Exception as e:

        raise Exception(
            f"Error verificando respaldo del bloque: {e}"
        )


# =====================================================
# OBTENER ESTADO DEL BLOQUE
# =====================================================

def estado_bloque_actual():
    """
    Determina si el bloque actual necesita respaldo.
    """

    bloque = obtener_bloque_actual()

    if bloque["bloque"] == 0:

        return {
            **bloque,
            "ya_respaldado": False,
            "necesita_respaldo": False
        }

    ya_respaldado = bloque_ya_respaldado(
        bloque["bloque"]
    )

    necesita_respaldo = (
        bloque["completo"]
        and not ya_respaldado
    )

    return {
        **bloque,
        "ya_respaldado": ya_respaldado,
        "necesita_respaldo": necesita_respaldo
    }

# =====================================================
# CREAR CARPETA DEL BLOQUE
# =====================================================

def crear_carpeta_bloque(bloque):
    """
    Crea la carpeta local correspondiente al bloque.
    """

    carpeta = os.path.join(
        CARPETA_RESPALDOS,
        f"bloque_{bloque:04d}"
    )

    os.makedirs(
        carpeta,
        exist_ok=True
    )

    return carpeta

# =====================================================
# REGISTRAR RESPALDO
# =====================================================

def registrar_respaldo(
    informacion,
    carpeta,
    evidencias
):
    """
    Registra en Supabase que un bloque
    fue respaldado correctamente.
    """

    try:

        datos = {

            "Bloque": informacion["bloque"],

            "Inicio": informacion["inicio"],

            "Fin": informacion["fin"],

            "CantidadReportes": informacion["reportes"],

            "FechaRespaldo": datetime.now().isoformat(),

            "Estado": "COMPLETADO"

        }

        respuesta = (
            supabase
            .table("respaldos")
            .insert(datos)
            .execute()
        )

        if not respuesta.data:

            raise Exception(
                "Supabase no confirmó "
                "el registro del respaldo."
            )

        return respuesta.data

    except Exception as e:

        raise Exception(
            f"Error registrando respaldo: {e}"
        )
# =====================================================
# OBTENER REPORTES DEL BLOQUE
# =====================================================

def obtener_reportes_bloque(inicio, fin):
    """
    Obtiene los reportes correspondientes al bloque.
    """

    try:

        respuesta = (
            supabase
            .table("reportes")
            .select("*")
            .order("FechaCreacion", desc=False)
            .execute()
        )

        datos = respuesta.data or []

        if not datos:
            return pd.DataFrame()

        df = pd.DataFrame(datos)

        # Tomar únicamente el rango solicitado
        df = df.iloc[
            inicio - 1:fin
        ].copy()

        return df

    except Exception as e:

        raise Exception(
            f"Error obteniendo reportes del bloque: {e}"
        )


# =====================================================
# OBTENER HISTORIAL DEL BLOQUE
# =====================================================

def obtener_historial_bloque(folios):
    """
    Obtiene el historial relacionado con los folios
    del bloque.
    """

    if not folios:
        return pd.DataFrame()

    try:

        respuesta = (
            supabase
            .table("historial")
            .select("*")
            .in_("Folio", folios)
            .execute()
        )

        return pd.DataFrame(
            respuesta.data or []
        )

    except Exception as e:

        raise Exception(
            f"Error obteniendo historial del bloque: {e}"
        )


# =====================================================
# OBTENER COMENTARIOS DEL BLOQUE
# =====================================================

def obtener_comentarios_bloque(folios):
    """
    Obtiene los comentarios relacionados con los folios
    del bloque.
    """

    if not folios:
        return pd.DataFrame()

    try:

        respuesta = (
            supabase
            .table("comentarios")
            .select("*")
            .in_("Folio", folios)
            .execute()
        )

        return pd.DataFrame(
            respuesta.data or []
        )

    except Exception as e:

        raise Exception(
            f"Error obteniendo comentarios del bloque: {e}"
        )

# =====================================================
# RESPALDAR UNA EVIDENCIA
# =====================================================

def respaldar_evidencia(
    ruta,
    carpeta_destino
):
    """
    Descarga una evidencia desde Supabase Storage
    y la guarda en la carpeta local del respaldo.

    No elimina ni modifica el archivo original.
    """

    if ruta in ["", None, "nan", "None"]:
        return False

    ruta = str(ruta).strip()

    try:

        archivo = (
            supabase
            .storage
            .from_("evidencias")
            .download(ruta)
        )

        if not archivo:
            raise Exception(
                "Supabase no devolvió contenido."
            )

        os.makedirs(
            carpeta_destino,
            exist_ok=True
        )

        nombre_archivo = os.path.basename(
            ruta
        )

        destino = os.path.join(
            carpeta_destino,
            nombre_archivo
        )

        with open(
            destino,
            "wb"
        ) as f:

            f.write(archivo)

        # Verificar que realmente exista
        # y tenga contenido.
        if not os.path.exists(destino):

            raise Exception(
                "El archivo no fue creado."
            )

        if os.path.getsize(destino) == 0:

            raise Exception(
                "El archivo respaldado está vacío."
            )

        return True

    except Exception as e:

        raise Exception(
            f"Error respaldando evidencia "
            f"'{ruta}': {e}"
        )

# =====================================================
# RESPALDAR EVIDENCIAS DEL BLOQUE
# =====================================================

def respaldar_evidencias_bloque(
    df_reportes,
    carpeta_bloque
):
    """
    Respalda las evidencias de apertura y cierre
    correspondientes a los reportes del bloque.

    Las evidencias inexistentes se omiten para que
    no detengan el respaldo completo.
    """

    carpeta_apertura = os.path.join(
        carpeta_bloque,
        "evidencias",
        "apertura"
    )

    carpeta_cierre = os.path.join(
        carpeta_bloque,
        "evidencias",
        "cierre"
    )

    respaldadas_apertura = 0
    respaldadas_cierre = 0

    # =============================================
    # EVIDENCIAS DE APERTURA
    # =============================================

    for _, reporte in df_reportes.iterrows():

        ruta = str(
            reporte.get(
                "ImagenApertura",
                ""
            )
        ).strip()

        if ruta in ["", "nan", "None"]:
            continue

        try:

            if respaldar_evidencia(
                ruta,
                carpeta_apertura
            ):

                respaldadas_apertura += 1

        except Exception as e:

            print(
                f"⚠ Evidencia de apertura omitida: "
                f"{ruta}"
            )

            print(e)

    # =============================================
    # EVIDENCIAS DE CIERRE
    # =============================================

    for _, reporte in df_reportes.iterrows():

        ruta = str(
            reporte.get(
                "ImagenCierre",
                ""
            )
        ).strip()

        if ruta in ["", "nan", "None"]:
            continue

        try:

            if respaldar_evidencia(
                ruta,
                carpeta_cierre
            ):

                respaldadas_cierre += 1

        except Exception as e:

            print(
                f"⚠ Evidencia de cierre omitida: "
                f"{ruta}"
            )

            print(e)

    return {
        "apertura": respaldadas_apertura,
        "cierre": respaldadas_cierre
    }
# =====================================================
# REGISTRAR RESPALDO
# =====================================================
def registrar_respaldo(
    bloque,
    inicio,
    fin,
    cantidad_reportes
):
    try:

        respuesta = (
            supabase
            .table("respaldos")
            .insert({
                "Bloque": bloque,
                "Inicio": inicio,
                "Fin": fin,
                "CantidadReportes": cantidad_reportes,
                "FechaRespaldo": datetime.now().isoformat(),
                "Estado": "COMPLETADO"
            })
            .execute()
        )

        return respuesta.data

    except Exception as e:

        raise Exception(
            f"Error registrando respaldo: {e}"
        )
# =====================================================
# VERIFICAR ARCHIVOS DEL RESPALDO
# =====================================================

def verificar_respaldo(carpeta_bloque):
    """
    Verifica que los archivos principales del respaldo
    existan y contengan información.
    """

    archivos_requeridos = [
        "reportes.csv",
        "historial.csv",
        "comentarios.csv"
    ]

    archivos_verificados = []

    for nombre in archivos_requeridos:

        ruta = os.path.join(
            carpeta_bloque,
            nombre
        )

        if not os.path.exists(ruta):
            raise Exception(
                f"No se encontró el archivo de respaldo: {ruta}"
            )

        if os.path.getsize(ruta) == 0:
            raise Exception(
                f"El archivo de respaldo está vacío: {ruta}"
            )

        archivos_verificados.append(ruta)

    return {
        "correcto": True,
        "archivos": archivos_verificados
    }
# =====================================================
# EXPORTAR BLOQUE
# =====================================================

def exportar_bloque(bloque):
    """
    Exporta reportes, historial, comentarios
    y evidencias correspondientes a un bloque.
    """

    informacion = obtener_bloque_actual()

    # ---------------------------------------------
    # VALIDAR BLOQUE
    # ---------------------------------------------

    if informacion["bloque"] != bloque:

        raise Exception(
            f"El bloque {bloque} no corresponde "
            "al bloque actual."
        )

    # ---------------------------------------------
    # VALIDAR QUE EL BLOQUE ESTÉ COMPLETO
    # ---------------------------------------------

    if not informacion["completo"]:

        raise Exception(
            f"El bloque {bloque} todavía no está completo."
        )

    # ---------------------------------------------
    # VALIDAR SI YA FUE RESPALDADO
    # ---------------------------------------------

    if bloque_ya_respaldado(bloque):

        raise Exception(
            f"El bloque {bloque} ya fue respaldado."
        )

    # ---------------------------------------------
    # CREAR CARPETA
    # ---------------------------------------------

    carpeta = crear_carpeta_bloque(
        bloque
    )

    # ---------------------------------------------
    # OBTENER REPORTES
    # ---------------------------------------------

    df_reportes = obtener_reportes_bloque(
        informacion["inicio"],
        informacion["fin"]
    )

    if df_reportes.empty:

        raise Exception(
            "No se encontraron reportes para respaldar."
        )

    # ---------------------------------------------
    # OBTENER FOLIOS
    # ---------------------------------------------

    folios = (
        df_reportes["Folio"]
        .dropna()
        .astype(str)
        .tolist()
    )

    # ---------------------------------------------
    # OBTENER HISTORIAL
    # ---------------------------------------------

    df_historial = obtener_historial_bloque(
        folios
    )

    # ---------------------------------------------
    # OBTENER COMENTARIOS
    # ---------------------------------------------

    df_comentarios = obtener_comentarios_bloque(
        folios
    )

    # ---------------------------------------------
    # EXPORTAR REPORTES
    # ---------------------------------------------

    archivo_reportes = os.path.join(
        carpeta,
        "reportes.csv"
    )

    df_reportes.to_csv(
        archivo_reportes,
        index=False,
        encoding="utf-8-sig"
    )

    # ---------------------------------------------
    # EXPORTAR HISTORIAL
    # ---------------------------------------------

    archivo_historial = os.path.join(
        carpeta,
        "historial.csv"
    )

    df_historial.to_csv(
        archivo_historial,
        index=False,
        encoding="utf-8-sig"
    )

    # ---------------------------------------------
    # EXPORTAR COMENTARIOS
    # ---------------------------------------------

    archivo_comentarios = os.path.join(
        carpeta,
        "comentarios.csv"
    )

    df_comentarios.to_csv(
        archivo_comentarios,
        index=False,
        encoding="utf-8-sig"
    )

    # ---------------------------------------------
    # RESPALDAR EVIDENCIAS
    # ---------------------------------------------

    evidencias = respaldar_evidencias_bloque(
        df_reportes,
        carpeta
    )

    # ---------------------------------------------
    # VERIFICAR ARCHIVOS
    # ---------------------------------------------

    verificacion = verificar_respaldo(
        carpeta
    )

    if not verificacion["correcto"]:

        raise Exception(
            "La verificación del respaldo falló."
        )

    # ---------------------------------------------
    # REGISTRAR RESPALDO
    # ---------------------------------------------

    registro = registrar_respaldo(
        bloque=bloque,
        inicio=informacion["inicio"],
        fin=informacion["fin"],
        cantidad_reportes=len(df_reportes)
    )

    # ---------------------------------------------
    # RESULTADO FINAL
    # ---------------------------------------------

    return {

        "bloque": bloque,

        "carpeta": carpeta,

        "reportes": len(df_reportes),

        "historial": len(df_historial),

        "comentarios": len(df_comentarios),

        "evidencias_apertura":
            evidencias["apertura"],

        "evidencias_cierre":
            evidencias["cierre"],

        "verificacion":
            verificacion,

        "registro_respaldo":
            registro,

        "fecha":
            datetime.now().isoformat()
    }