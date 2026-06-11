from datetime import date
from celery import shared_task
from .models import RecurrenciaTransferencia, Transferencia
from apps.accounts.models import Cuenta


@shared_task
def ejecutar_recurrencias():
    hoy = date.today()
    recurrencias = RecurrenciaTransferencia.objects.filter(
        activo=True, proxima_ejecucion=hoy
    ).select_related('origen', 'destino', 'inquilino', 'usuario')

    for r in recurrencias:
        Transferencia.objects.create(
            inquilino=r.inquilino,
            usuario=r.usuario,
            origen=r.origen,
            destino=r.destino,
            monto=r.monto,
            fecha=hoy,
            nota=r.nota,
        )
        r.proxima_ejecucion = r.calcular_proxima_ejecucion()
        r.save(update_fields=['proxima_ejecucion'])

    return f'{recurrencias.count()} recurrencias ejecutadas'


@shared_task
def recordatorio_tarjetas_credito():
    from datetime import date, timedelta
    hoy = date.today()
    en_5_dias = hoy + timedelta(days=5)

    tarjetas = Cuenta.objects.filter(
        tipo='credito', activo=True
    ).exclude(dia_pago='')

    recordatorios = []
    for t in tarjetas:
        try:
            dia_pago = int(t.dia_pago)
            prox_pago = hoy.replace(day=min(dia_pago, 28))
            if prox_pago < hoy:
                if prox_pago.month == 12:
                    prox_pago = prox_pago.replace(year=prox_pago.year + 1, month=1)
                else:
                    prox_pago = prox_pago.replace(month=prox_pago.month + 1)
            if hoy <= prox_pago <= en_5_dias:
                recordatorios.append(f'{t.nombre}: pago vence el {prox_pago}')
        except (ValueError, TypeError):
            pass

    return f'{len(recordatorios)} recordatorios pendientes: {" | ".join(recordatorios)}' if recordatorios else 'Sin recordatorios'
