from datetime import datetime
import pandas as pd

from database.reportes_db import (
    cargar_reportes,
    guardar_reporte
)

from Services.evidencias_service import (
    guardar_imagen
)

from utils.historial import (
    registrar_movimiento
)


def crear_reporte(datos):

    try:

        # ==========================
        # Cargar reportes existentes
        # ==========================

        df = cargar_reportes()

        # ==========================
        # Guardar imagen
        # ==========================

        ruta_img = guardar_imagen(
            datos.get("imagen")
        )

        # ==========================
        # Generar ID
        # ==========================

        if len(df) == 0:

            nuevo_id = 1

        else:

            nuevo_id = (
                pd.to_numeric(
                    df["ID"],
                    errors="coerce"
                )
                .fillna(0)
                .max()
                + 1
            )

            nuevo_id = int(nuevo_id)

        # ==========================
        # Generar folio
        # ==========================

        anio = datetime.now().year

        contador = len(df) + 1

        folio = f"UTG-{anio}-{contador:05d}"

        # ==========================
        # Fechas
        # ==========================

        fecha_actual = datetime.now().strftime(
            "%Y-%m-%d %H:%M"
        )

        # ==========================
        # Construir reporte
        # ==========================

        nuevo = {

            "Folio": folio,

            "FechaCreacion": fecha_actual,

            "FechaAsignacion": "",

            "FechaResolucion": "",

            "FechaCierre": "",

            "FechaActualizacion": fecha_actual,

            "Edificio": datos["edificio"],

            "Area": datos["area"],

            "UbicacionDetalle":
                datos["ubicacion_detalle"],

            "Activo": datos["activo"],

            "Categoria": datos["categoria"],

            "Impacto": datos["impacto"],

            "Prioridad": datos["prioridad"],

            "Descripcion":
                datos["descripcion"],

            "Estado": "Pendiente",

            "Responsable": "Sin asignar",

            "ComentarioCierre": "",

            "ImagenApertura": ruta_img,

            "ImagenCierre": ""
        }

        # ==========================
        # Guardar
        # ==========================

        guardar_reporte(nuevo)

        # ==========================
        # Historial
        # ==========================

        registrar_movimiento(
            folio=folio,
            usuario="Sistema",
            accion="Creación",
            detalle="Reporte creado por usuario"
        )

        print("Historial registrado:", folio)

        # ==========================
        # Respuesta
        # ==========================

        return {

            "ok": True,

            "folio": folio,

            "mensaje":
                f"Reporte enviado correctamente. Folio: {folio}"
        }

    except Exception as e:

        return {

            "ok": False,

            "mensaje":
                f"Error al crear reporte: {e}"
        }