import json
import logging
from datetime import date, timedelta
from celery import shared_task
from pywebpush import webpush, WebPushException
from django.conf import settings
from apps.accounts.models import Cuenta
from apps.core.utils import calcular_prox_pago
from .models import SuscripcionPush

logger = logging.getLogger(__name__)


@shared_task(
    name='apps.notifications.tasks.enviar_recordatorios_push',
    ignore_result=True, bind=True, max_retries=3,
)
def enviar_recordatorios_push(self):
    hoy = date.today()
    dias_aviso = [0, 2, 5, 7]

    tarjetas = Cuenta.objects.filter(
        tipo='credito', activo=True
    ).exclude(dia_pago='').select_related('usuario', 'inquilino')

    vapid_key = settings.VAPID_PRIVATE_KEY
    if not vapid_key:
        logger.error('VAPID_PRIVATE_KEY no está configurada')
        return 'Error: llaves VAPID no configuradas'

    enviadas = 0
    for t in tarjetas:
        prox = calcular_prox_pago(t)
        if prox is None:
            continue
        diff = (prox - hoy).days
        if diff not in dias_aviso:
            continue

        total_a_pagar = max(t.limite_credito - t.balance, 0)
        monto_str = f'RD$ {total_a_pagar:,.2f}'

        if diff > 0:
            titulo = '⚠️ Pago próximo'
            cuerpo = f'{t.nombre} ({t.emisor})\nVence: {prox.strftime("%d/%m/%Y")}\nMonto: {monto_str}'
        else:
            titulo = '📌 Pago HOY'
            cuerpo = f'{t.nombre} ({t.emisor})\nVence: HOY\nMonto: {monto_str}'

        mensaje = {
            'title': titulo,
            'body': cuerpo,
            'url': '/cuentas/',
            'icon': '/static/img/icon-192.png',
            'badge': '/static/img/badge-72.png',
        }

        for sub in SuscripcionPush.objects.filter(
            usuario=t.usuario, activo=True
        ).only('endpoint', 'p256dh', 'auth'):
            try:
                webpush(
                    subscription_info={
                        'endpoint': sub.endpoint,
                        'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                    },
                    data=json.dumps(mensaje),
                    vapid_private_key=vapid_key,
                    vapid_claims={'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'},
                    timeout=10,
                )
                enviadas += 1
            except WebPushException as e:
                code = e.response.status_code if e.response else None
                if code in (400, 403, 404, 410):
                    sub.delete()
                else:
                    logger.error(f'Push error {code}: {e}')
            except Exception as e:
                logger.error(f'Push inesperado: {e}')

    return f'{enviadas} notificaciones enviadas'
