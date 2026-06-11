from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DepositoAhorro


@receiver(post_save, sender=DepositoAhorro)
def deposito_creado(sender, instance, created, **kwargs):
    if created:
        instance.meta.monto_actual += instance.monto
        instance.meta.save(update_fields=['monto_actual'])


@receiver(post_delete, sender=DepositoAhorro)
def deposito_eliminado(sender, instance, **kwargs):
    instance.meta.monto_actual -= instance.monto
    instance.meta.save(update_fields=['monto_actual'])
