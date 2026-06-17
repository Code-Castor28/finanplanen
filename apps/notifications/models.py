from django.db import models
from django.conf import settings


class SuscripcionPush(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='suscripciones_push',
    )
    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'suscripciones_push'
        verbose_name = 'Suscripción Push'
        verbose_name_plural = 'Suscripciones Push'

    def __str__(self):
        return f'Suscripción de {self.usuario} ({self.endpoint[:50]}...)'
