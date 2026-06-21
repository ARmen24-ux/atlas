import re


def validar_nombre(nombre):

    return nombre.strip() != ""


def validar_correo(correo):

    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    return bool(
        re.match(
            patron,
            correo
        )
    )


def validar_descripcion(descripcion):

    return descripcion.strip() != ""

