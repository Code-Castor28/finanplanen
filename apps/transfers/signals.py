import logging
from django.db import transaction, IntegrityError
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transferencia
from apps.accounts.models import Cuenta

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transferencia)
def transferencia_creada(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                updated_origen = Cuenta.objects.filter(
                    pk=instance.origen_id
                ).update(balance=F('balance') - instance.monto)
                updated_destino = Cuenta.objects.filter(
                    pk=instance.destino_id
                ).update(balance=F('balance') + instance.monto)
                if updated_origen and updated_destino:
                    logger.info(
                        'Transferencia %s: Origen %s -= %s, Destino %s += %s',
                        instance.pk, instance.origen_id, instance.monto,
                        instance.destino_id, instance.monto,
                    )
        except IntegrityError:
            logger.critical(
                'Fallo al actualizar balances por Transferencia %s (Origen %s, Destino %s)',
                instance.pk, instance.origen_id, instance.destino_id,
            )


@receiver(post_delete, sender=Transferencia)
def transferencia_eliminada(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            updated_origen = Cuenta.objects.filter(
                pk=instance.origen_id
            ).update(balance=F('balance') + instance.monto)
            updated_destino = Cuenta.objects.filter(
                pk=instance.destino_id
            ).update(balance=F('balance') - instance.monto)
            if updated_origen and updated_destino:
                logger.info(
                    'Transferencia %s eliminada: Origen %s += %s, Destino %s -= %s',
                    instance.pk, instance.origen_id, instance.monto,
                    instance.destino_id, instance.monto,
                )
    except IntegrityError:
        logger.critical(
            'Fallo al revertir balances por eliminación de Transferencia %s',
            instance.pk,
        )
