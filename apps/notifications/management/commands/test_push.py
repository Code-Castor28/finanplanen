import json
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pywebpush import webpush, WebPushException

from apps.accounts.models import Cuenta
from apps.notifications.models import SuscripcionPush


def _calcular_prox_pago(cuenta):
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


class Command(BaseCommand):
    help = 'Envía una notificación push con datos reales del usuario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Nombre de usuario específico (obligatorio para datos reales)',
        )
        parser.add_argument(
            '--titulo',
            type=str,
            default=None,
            help='Título personalizado (opcional: se genera automáticamente)',
        )
        parser.add_argument(
            '--cuerpo',
            type=str,
            default=None,
            help='Cuerpo personalizado (opcional: se genera automáticamente)',
        )

    def handle(self, *args, **options):
        titulo_override = options['titulo']
        cuerpo_override = options['cuerpo']
        usuario_filter = options['usuario']

        vapid_key = settings.VAPID_PRIVATE_KEY
        if not vapid_key:
            self.stdout.write(self.style.ERROR('✗ VAPID_PRIVATE_KEY no está configurada'))
            return

        suscripciones = SuscripcionPush.objects.filter(activo=True).select_related('usuario')

        if usuario_filter:
            suscripciones = suscripciones.filter(usuario__nombre_usuario=usuario_filter)
            if not suscripciones.exists():
                raise CommandError(f'No hay suscripciones activas para el usuario "{usuario_filter}"')

        if not suscripciones.exists():
            self.stdout.write(self.style.WARNING('No hay suscripciones activas'))
            return

        if titulo_override and cuerpo_override:
            mensaje = {
                'title': titulo_override,
                'body': cuerpo_override,
                'url': '/',
                'icon': '/static/img/icon-192.png',
                'badge': '/static/img/badge-72.png',
            }
        else:
            mensaje = self._build_mensaje(suscripciones.first().usuario)

        enviadas = 0
        fallidas = 0

        for sub in suscripciones:
            try:
                webpush(
                    subscription_info={
                        'endpoint': sub.endpoint,
                        'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                    },
                    data=json.dumps(mensaje),
                    vapid_private_key=vapid_key,
                    vapid_claims={'sub': f'mailto:{settings.VAPID_ADMIN_EMAIL}'},
                )
                self.stdout.write(self.style.SUCCESS(f'  ✓ {sub.usuario}'))
                enviadas += 1
            except WebPushException as e:
                code = e.response.status_code if e.response else '?'
                self.stdout.write(self.style.ERROR(f'  ✗ {sub.usuario} — HTTP {code}'))
                if code in (400, 403, 404, 410):
                    sub.delete()
                    self.stdout.write(self.style.WARNING(f'    → Suscripción eliminada'))
                fallidas += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ {sub.usuario} — {e}'))
                fallidas += 1

        resumen = f'Enviadas: {enviadas}, Fallidas: {fallidas}'
        if fallidas == 0:
            self.stdout.write(self.style.SUCCESS(resumen))
        else:
            self.stdout.write(self.style.WARNING(resumen))

    def _build_mensaje(self, usuario):
        tarjetas = Cuenta.objects.filter(
            usuario=usuario, tipo='credito', activo=True
        ).exclude(dia_pago='')

        hoy = date.today()
        mas_urgente = None
        menor_diff = None

        for t in tarjetas:
            prox = _calcular_prox_pago(t)
            if prox is None:
                continue
            diff = (prox - hoy).days
            if diff < 0:
                continue
            if menor_diff is None or diff < menor_diff:
                menor_diff = diff
                mas_urgente = (t, prox, diff)

        if mas_urgente:
            t, prox, diff = mas_urgente
            nombre = t.nombre
            if t.emisor:
                nombre = f'{t.nombre} ({t.emisor})'
            balance = ''
            if t.balance and t.balance > 0:
                balance = f' — ${t.balance:,.2f}'

            if diff == 0:
                return {
                    'title': '📌 Pago HOY',
                    'body': f'HOY vence tu {nombre}{balance}',
                    'url': '/cuentas/',
                    'icon': '/static/img/icon-192.png',
                    'badge': '/static/img/badge-72.png',
                }
            fecha = prox.strftime('%d/%m/%Y')
            return {
                'title': '⚠️ Pago próximo',
                'body': f'Tu {nombre} vence el {fecha}{balance}',
                'url': '/cuentas/',
                'icon': '/static/img/icon-192.png',
                'badge': '/static/img/badge-72.png',
            }

        total = tarjetas.count()
        if total == 0:
            tarjetas = Cuenta.objects.filter(usuario=usuario, activo=True)
            total = tarjetas.count()

        balance_total = sum(t.balance or 0 for t in tarjetas)
        balance_str = f' · Saldo: ${balance_total:,.2f}' if balance_total else ''

        prox_pago_info = None
        prox_diff = None
        for t in tarjetas:
            prox = _calcular_prox_pago(t)
            if prox is None:
                continue
            diff = (prox - hoy).days
            if diff < 0:
                continue
            if prox_diff is None or diff < prox_diff:
                prox_diff = diff
                prox_pago_info = (t, prox)

        if prox_pago_info:
            t, prox = prox_pago_info
            n = t.nombre if not t.emisor else f'{t.nombre} ({t.emisor})'
            return {
                'title': f'📊 {total} tarjetas activas',
                'body': f'Próximo vencimiento: {n} el {prox.strftime("%d/%m/%Y")}{balance_str}',
                'url': '/cuentas/',
                'icon': '/static/img/icon-192.png',
                'badge': '/static/img/badge-72.png',
            }

        return {
            'title': f'📊 {total} tarjetas activas',
            'body': f'Tus finanzas al día{balance_str}',
            'url': '/',
            'icon': '/static/img/icon-192.png',
            'badge': '/static/img/badge-72.png',
        }
