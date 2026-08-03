from io import BytesIO
from PIL import Image, ImageOps


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