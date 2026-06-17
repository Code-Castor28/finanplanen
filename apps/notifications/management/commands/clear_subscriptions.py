from django.core.management.base import BaseCommand
from apps.notifications.models import SuscripcionPush


class Command(BaseCommand):
    help = 'Elimina todas las suscripciones push (útil tras regenerar llaves VAPID)'

    def handle(self, *args, **options):
        count = SuscripcionPush.objects.count()
        SuscripcionPush.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'{count} suscripciones eliminadas'))
