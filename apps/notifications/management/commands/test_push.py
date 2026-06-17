import json
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pywebpush import webpush, WebPushException
from apps.notifications.models import SuscripcionPush


class Command(BaseCommand):
    help = 'Envía una notificación push de prueba a uno o todos los usuarios con suscripción activa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Nombre de usuario específico (opcional: si se omite, envía a todos)',
        )
        parser.add_argument(
            '--titulo',
            type=str,
            default='🔔 Prueba',
            help='Título de la notificación',
        )
        parser.add_argument(
            '--cuerpo',
            type=str,
            default='Notificación de prueba',
            help='Cuerpo de la notificación',
        )

    def handle(self, *args, **options):
        titulo = options['titulo']
        cuerpo = options['cuerpo']
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

        mensaje = {
            'title': titulo,
            'body': cuerpo,
            'url': '/',
            'icon': '/static/img/icon-192.png',
            'badge': '/static/img/badge-72.png',
        }

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
                self.stdout.write(self.style.SUCCESS(f'  ✓ {sub.usuario} — {sub.endpoint[:60]}...'))
                enviadas += 1
            except WebPushException as e:
                code = e.response.status_code if e.response else '?'
                self.stdout.write(self.style.ERROR(f'  ✗ {sub.usuario} — HTTP {code}: {e}'))
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
