from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from apps.transactions.models import Gasto
from .models import Presupuesto


def actualizar_monto_gastado(categoria, mes, año, inquilino):
    total = Gasto.objects.filter(
        inquilino=inquilino,
        categoria=categoria,
        fecha__month=mes,
        fecha__year=año,
    ).aggregate(total=Sum('monto'))['total'] or 0

    Presupuesto.objects.filter(
        inquilino=inquilino,
        categoria=categoria,
        mes=mes,
        año=año,
    ).update(monto_gastado=total)


@receiver(post_save, sender=Gasto)
@receiver(post_delete, sender=Gasto)
def gasto_actualiza_presupuesto(sender, instance, **kwargs):
    actualizar_monto_gastado(
        categoria=instance.categoria,
        mes=instance.fecha.month,
        año=instance.fecha.year,
        inquilino=instance.inquilino,
    )
