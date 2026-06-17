from datetime import date
from celery import shared_task
from .models import RecurrenciaTransferencia, Transferencia


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
