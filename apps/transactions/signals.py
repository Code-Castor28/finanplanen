import logging
from django.db import transaction, IntegrityError
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Ingreso, Gasto
from apps.accounts.models import Cuenta

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Ingreso)
def ingreso_creado(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                updated = Cuenta.objects.filter(
                    pk=instance.cuenta_id
                ).update(balance=F('balance') + instance.monto)
                if updated:
                    logger.info(
                        'Ingreso %s: Cuenta %s += %s',
                        instance.pk, instance.cuenta_id, instance.monto,
                    )
        except IntegrityError:
            logger.critical(
                'Fallo al actualizar balance por Ingreso %s (Cuenta %s)',
                instance.pk, instance.cuenta_id,
            )


@receiver(post_delete, sender=Ingreso)
def ingreso_eliminado(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            updated = Cuenta.objects.filter(
                pk=instance.cuenta_id
            ).update(balance=F('balance') - instance.monto)
            if updated:
                logger.info(
                    'Ingreso %s eliminado: Cuenta %s -= %s',
                    instance.pk, instance.cuenta_id, instance.monto,
                )
    except IntegrityError:
        logger.critical(
            'Fallo al revertir balance por eliminación de Ingreso %s (Cuenta %s)',
            instance.pk, instance.cuenta_id,
        )


@receiver(post_save, sender=Gasto)
def gasto_creado(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                updated = Cuenta.objects.filter(
                    pk=instance.cuenta_id
                ).update(balance=F('balance') - instance.monto)
                if updated:
                    logger.info(
                        'Gasto %s: Cuenta %s -= %s',
                        instance.pk, instance.cuenta_id, instance.monto,
                    )
        except IntegrityError:
            logger.critical(
                'Fallo al actualizar balance por Gasto %s (Cuenta %s)',
                instance.pk, instance.cuenta_id,
            )


@receiver(post_delete, sender=Gasto)
def gasto_eliminado(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            updated = Cuenta.objects.filter(
                pk=instance.cuenta_id
            ).update(balance=F('balance') + instance.monto)
            if updated:
                logger.info(
                    'Gasto %s eliminado: Cuenta %s += %s',
                    instance.pk, instance.cuenta_id, instance.monto,
                )
    except IntegrityError:
        logger.critical(
            'Fallo al revertir balance por eliminación de Gasto %s (Cuenta %s)',
            instance.pk, instance.cuenta_id,
        )
