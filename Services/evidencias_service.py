from io import BytesIO
from PIL import Image, ImageOps
from datetime import datetime

from database.supabase_client import supabase
import uuid

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
# SUBIR IMAGEN A SUPABASE STORAGE
# =====================================================

def guardar_imagen(archivo):
    """
    Comprime la imagen y la sube al bucket
    'evidencias' de Supabase Storage.

    Devuelve la ruta almacenada en el bucket.
    """

    if archivo is None:
        return ""

    # Comprimir imagen
    imagen = comprimir_imagen(archivo)

    # Nombre único
    nombre = (
        datetime.now().strftime("%Y%m%d%H%M%S")
        + "_"
        + str(uuid.uuid4())[:8]
        + ".jpg"
    )

    ruta = (
        f"apertura/"
        f"{datetime.now().year}/"
        f"{nombre}"
    )

    # Subir al bucket
    supabase.storage.from_("evidencias").upload(
        path=ruta,
        file=imagen.getvalue(),
        file_options={
            "content-type": "image/jpeg"
        }
    )

    return ruta

# =====================================================
# OBTENER URL PÚBLICA
# =====================================================

def obtener_url_publica(ruta):

    if ruta in ["", None]:
        return ""

    respuesta = (
        supabase
        .storage
        .from_("evidencias")
        .get_public_url(ruta)
    )

    return respuesta