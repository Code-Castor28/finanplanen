from django.db import models
from django.utils.text import slugify


class Color(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    nombre = models.CharField(max_length=100)
    slug = models.SlugField()
    hex = models.CharField(max_length=7, help_text='#RRGGBB')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colores'
        unique_together = ['inquilino', 'slug']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        if not self.hex.startswith('#'):
            self.hex = f'#{self.hex}'
        super().save(*args, **kwargs)


class Icono(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    nombre = models.CharField(max_length=100)
    slug = models.SlugField()
    clase_css = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Icono'
        verbose_name_plural = 'Iconos'
        unique_together = ['inquilino', 'slug']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
