from datetime import datetime, timedelta


SLA_HORAS = {
    "Baja": 168,
    "Media": 72,
    "Alta": 24,
    "Crítica": 4
}


def calcular_sla(fecha_creacion, prioridad):

    try:

        fecha = datetime.strptime(
            fecha_creacion,
            "%Y-%m-%d %H:%M"
        )

    except:

        return "Sin datos", 0

    horas_sla = SLA_HORAS.get(
        prioridad,
        72
    )

    fecha_limite = fecha + timedelta(
        hours=horas_sla
    )

    ahora = datetime.now()

    horas_restantes = (
        fecha_limite - ahora
    ).total_seconds() / 3600

    if horas_restantes < 0:

        return "Vencido", horas_restantes

    elif horas_restantes <= horas_sla * 0.25:

        return "Próximo a vencer", horas_restantes

    else:

        return "En tiempo", horas_restantes