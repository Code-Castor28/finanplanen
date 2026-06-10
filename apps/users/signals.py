from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Usuario, Tenant


@receiver(post_save, sender=Usuario)
def crear_inquilino_auto(sender, instance, created, **kwargs):
    if created and not instance.inquilino:
        tenant = Tenant.objects.create(
            nombre=f"Inquilino de {instance.nombre_usuario}",
            slug=slugify(instance.nombre_usuario),
        )
        Usuario.objects.filter(pk=instance.pk).update(inquilino=tenant)
