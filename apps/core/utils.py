from datetime import date


def calcular_prox_pago(cuenta):
    hoy = date.today()
    try:
        dia = int(cuenta.dia_pago)
    except (ValueError, TypeError):
        return None
    dia = min(dia, 28)
    prox = hoy.replace(day=dia)
    if prox < hoy:
        if prox.month == 12:
            prox = prox.replace(year=prox.year + 1, month=1)
        else:
            prox = prox.replace(month=prox.month + 1)
    return prox
