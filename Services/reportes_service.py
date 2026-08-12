from datetime import datetime

from database.reportes_db import (
    cargar_reportes,
    guardar_reporte
)

from Services.evidencias_service import (
    subir_imagen_supabase
)

from Services.backup_manager_service import (
    ejecutar_respaldo_si_corresponde
)

from utils.historial import (
    registrar_movimiento
)


# =====================================================
# CREAR REPORTE
# =====================================================

def crear_reporte(datos):

    try:

        # ==========================================
        # Obtener reportes existentes
        # ==========================================

        df = cargar_reportes()

        # ==========================================
        # Guardar imagen
        # ==========================================

        ruta_imagen = subir_imagen_supabase(
            datos["imagen"],
            carpeta="apertura"
        )

        # ==========================================
        # Generar Folio
        # ==========================================

        anio = datetime.now().year

        consecutivo = len(df) + 1

        folio = f"UTG-{anio}-{consecutivo:05d}"

        # ==========================================
        # Fecha actual
        # ==========================================

        ahora = datetime.now()

        # ==========================================
        # Construir registro
        # ==========================================

        reporte = {

            "Folio": folio,

            "FechaCreacion": ahora.isoformat(),

            "FechaActualizacion": ahora.isoformat(),

            "Estado": "Pendiente",

            "Prioridad": datos["prioridad"],

            "Categoria": datos["categoria"],

            "Area": datos["area"],

            "Edificio": datos["edificio"],

            "Activo": datos["activo"],

            "Descripcion": datos["descripcion"],

            "Impacto": datos["impacto"],

            "ImagenApertura": ruta_imagen,

            "ImagenCierre": None,

            "UsuarioReporta": "Sistema",

            "UsuarioAsignado": None,

            "SLAHoras": None,

            "SLACumplido": None

        }

        # ==========================================
        # Insertar en Supabase
        # ==========================================

        guardar_reporte(reporte)


        # ==========================================
        # Historial
        # ==========================================

        registrar_movimiento(

            folio=folio,

            usuario="Sistema",

            accion="Creación",

            detalle="Reporte creado"

        )


        # =====================================================
        # VERIFICAR RESPALDO AUTOMÁTICO
        # =====================================================

        try:

            resultado_respaldo = (
                ejecutar_respaldo_si_corresponde()
            )

        except Exception as e:

            resultado_respaldo = {
                "ejecutado": False,
                "error": str(e)
            }

        return {

            "ok": True,

            "folio": folio,

            "mensaje": f"Reporte registrado correctamente.\n\nFolio: {folio}"

        }

    except Exception as e:

        return {

            "ok": False,

            "mensaje": str(e)

        }