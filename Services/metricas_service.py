def obtener_kpis(df):

    return {

        "tickets": len(df),

        "pendientes": len(
            df[df["Estado"] == "Pendiente"]
        ),

        "en_proceso": len(
            df[
                df["Estado"].isin(
                    ["Asignado", "En proceso"]
                )
            ]
        ),

        "resueltos": len(
            df[df["Estado"] == "Resuelto"]
        ),

        "cerrados": len(
            df[df["Estado"] == "Cerrado"]
        )
    }