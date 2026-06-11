from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transferencia


@receiver(post_save, sender=Transferencia)
def transferencia_creada(sender, instance, created, **kwargs):
    if created:
        instance.origen.balance -= instance.monto
        instance.origen.save(update_fields=['balance'])
        instance.destino.balance += instance.monto
        instance.destino.save(update_fields=['balance'])


@receiver(post_delete, sender=Transferencia)
def transferencia_eliminada(sender, instance, **kwargs):
    instance.origen.balance += instance.monto
    instance.origen.save(update_fields=['balance'])
    instance.destino.balance -= instance.monto
    instance.destino.save(update_fields=['balance'])
