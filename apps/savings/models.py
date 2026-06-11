from django.db import models
from django.utils.text import slugify


class MetaAhorro(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    nombre = models.CharField(max_length=100, verbose_name='nombre')
    slug = models.SlugField()
    meta = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='meta'
    )
    monto_actual = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='monto actual'
    )
    fecha_limite = models.DateField(
        null=True, blank=True, verbose_name='fecha límite'
    )
    color = models.ForeignKey(
        'theme.Color', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='color'
    )
    icono = models.ForeignKey(
        'theme.Icono', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='icono'
    )
    nota = models.TextField(blank=True, verbose_name='nota')
    activo = models.BooleanField(default=True, verbose_name='activo')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Meta de Ahorro'
        verbose_name_plural = 'Metas de Ahorro'
        unique_together = ['inquilino', 'slug']
        ordering = ['-creado']

    def __str__(self):
        return self.nombre

    def progreso_pct(self):
        if self.meta:
            return round(float(self.monto_actual) / float(self.meta) * 100, 1)
        return 0

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class DepositoAhorro(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    meta = models.ForeignKey(
        MetaAhorro, on_delete=models.CASCADE,
        related_name='depositos',
        verbose_name='meta de ahorro'
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='monto'
    )
    fecha = models.DateField(verbose_name='fecha')
    nota = models.TextField(blank=True, verbose_name='nota')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.meta.nombre} — RD$ {self.monto}'
