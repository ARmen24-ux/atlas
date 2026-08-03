from io import BytesIO
from PIL import Image, ImageOps
import os
from datetime import datetime


# =====================================================
# CONFIGURACIÓN
# =====================================================

MAX_PIXELS = 1600          # Resolución máxima
CALIDAD_JPG = 82           # Calidad JPEG


# =====================================================
# COMPRIMIR IMAGEN
# =====================================================

def comprimir_imagen(archivo):
    """
    Recibe un UploadedFile de Streamlit.

    Devuelve:

        bytes_jpg
    """

    if archivo is None:
        return None

    # ---------------------------------------------
    # Abrir imagen
    # ---------------------------------------------

    imagen = Image.open(archivo)

    # ---------------------------------------------
    # Corregir orientación EXIF
    # ---------------------------------------------

    imagen = ImageOps.exif_transpose(imagen)

    # ---------------------------------------------
    # Convertir a RGB
    # (PNG puede venir en RGBA)
    # ---------------------------------------------

    if imagen.mode != "RGB":
        imagen = imagen.convert("RGB")

    # ---------------------------------------------
    # Redimensionar
    # ---------------------------------------------

    imagen.thumbnail(
        (MAX_PIXELS, MAX_PIXELS)
    )

    # ---------------------------------------------
    # Guardar en memoria
    # ---------------------------------------------

    salida = BytesIO()

    imagen.save(

        salida,

        format="JPEG",

        quality=CALIDAD_JPG,

        optimize=True

    )

    salida.seek(0)

    return salida

# =====================================================
# GUARDAR IMAGEN (COMPATIBILIDAD)
# =====================================================

CARPETA = "assets/evidencias"


def guardar_imagen(archivo):
    """
    Guarda una imagen comprimida localmente.

    Esta función existe únicamente para mantener
    compatibilidad con el sistema actual mientras
    se migra a Supabase Storage.
    """

    if archivo is None:
        return ""

    os.makedirs(
        CARPETA,
        exist_ok=True
    )

    nombre = (
        datetime.now().strftime("%Y%m%d%H%M%S")
        + "_"
        + archivo.name.rsplit(".", 1)[0]
        + ".jpg"
    )

    ruta = os.path.join(
        CARPETA,
        nombre
    )

    imagen = comprimir_imagen(archivo)

    with open(ruta, "wb") as f:
        f.write(imagen.getvalue())

    return ruta