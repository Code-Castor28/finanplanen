from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
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
    color = models.ForeignKey(
        'theme.Color', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='color'
    )
    icono = models.ForeignKey(
        'theme.Icono', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='icono'
    )
    deducible = models.BooleanField(default=False, verbose_name='fiscalmente deducible')
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        unique_together = ['inquilino', 'slug']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Etiqueta(models.Model):
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
    color = models.ForeignKey(
        'theme.Color', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='color'
    )
    categorias = models.ManyToManyField(
        Categoria, blank=True, verbose_name='categorías'
    )
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'
        unique_together = ['inquilino', 'slug']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
