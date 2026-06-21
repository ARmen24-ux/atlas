import os
from datetime import datetime


CARPETA = "assets/evidencias"


def guardar_imagen(imagen):

    if imagen is None:

        return ""

    os.makedirs(
        CARPETA,
        exist_ok=True
    )

    nombre = (
        datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
        + "_"
        + imagen.name
    )

    ruta = os.path.join(
        CARPETA,
        nombre
    )

    with open(
        ruta,
        "wb"
    ) as f:

        f.write(
            imagen.getbuffer()
        )

    return ruta

