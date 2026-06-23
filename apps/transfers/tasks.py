import logging
from datetime import date
from celery import shared_task
from django.db import transaction, OperationalError
from .models import RecurrenciaTransferencia, Transferencia

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True, bind=True, max_retries=3)
def ejecutar_recurrencias(self):
    hoy = date.today()
    try:
        recurrencias = list(
            RecurrenciaTransferencia.objects.select_for_update(nowait=True).filter(
                activo=True, proxima_ejecucion=hoy
            ).select_related('origen', 'destino')
        )
    except OperationalError:
        logger.warning('Recurrencias bloqueadas por otro worker, saltando ejecución')
        return 'Bloqueado por otro worker'

    if not recurrencias:
        return '0 recurrencias ejecutadas'

    try:
        with transaction.atomic():
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
    except Exception as e:
        logger.critical(
            'Error creando transferencias recurrentes: %s', e, exc_info=True
        )
        raise

    logger.info('%s recurrencias ejecutadas', len(recurrencias))
    return f'{len(recurrencias)} recurrencias ejecutadas'
