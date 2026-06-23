import logging
from django.db import transaction, IntegrityError
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DepositoAhorro, MetaAhorro
from apps.accounts.models import Cuenta

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DepositoAhorro)
def deposito_creado(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                updated_meta = MetaAhorro.objects.filter(
                    pk=instance.meta_id
                ).update(monto_actual=F('monto_actual') + instance.monto)
                if instance.cuenta_id:
                    Cuenta.objects.filter(
                        pk=instance.cuenta_id
                    ).update(balance=F('balance') - instance.monto)
                if updated_meta:
                    logger.info(
                        'Deposito %s: Meta %s += %s',
                        instance.pk, instance.meta_id, instance.monto,
                    )
        except IntegrityError:
            logger.critical(
                'Fallo al actualizar por Deposito %s (Meta %s)',
                instance.pk, instance.meta_id,
            )


@receiver(post_delete, sender=DepositoAhorro)
def deposito_eliminado(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            if instance.meta_id:
                updated_meta = MetaAhorro.objects.filter(
                    pk=instance.meta_id
                ).update(monto_actual=F('monto_actual') - instance.monto)
                if updated_meta:
                    logger.info(
                        'Deposito %s eliminado: Meta %s -= %s',
                        instance.pk, instance.meta_id, instance.monto,
                    )
            if instance.cuenta_id:
                Cuenta.objects.filter(
                    pk=instance.cuenta_id
                ).update(balance=F('balance') + instance.monto)
    except IntegrityError:
        logger.critical(
            'Fallo al revertir por eliminación de Deposito %s (Meta %s)',
            instance.pk, instance.meta_id,
        )
