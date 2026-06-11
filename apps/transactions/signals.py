from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Ingreso, Gasto


@receiver(post_save, sender=Ingreso)
def ingreso_creado(sender, instance, created, **kwargs):
    if created:
        instance.cuenta.balance += instance.monto
        instance.cuenta.save(update_fields=['balance'])


@receiver(post_delete, sender=Ingreso)
def ingreso_eliminado(sender, instance, **kwargs):
    instance.cuenta.balance -= instance.monto
    instance.cuenta.save(update_fields=['balance'])


@receiver(post_save, sender=Gasto)
def gasto_creado(sender, instance, created, **kwargs):
    if created:
        instance.cuenta.balance -= instance.monto
        instance.cuenta.save(update_fields=['balance'])


@receiver(post_delete, sender=Gasto)
def gasto_eliminado(sender, instance, **kwargs):
    instance.cuenta.balance += instance.monto
    instance.cuenta.save(update_fields=['balance'])
