from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models


class Ingreso(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    cuenta = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.PROTECT,
        verbose_name='cuenta'
    )
    categoria = models.ForeignKey(
        'categories.Categoria', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='categoría'
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='monto'
    )
    fecha = models.DateField(db_index=True, verbose_name='fecha')
    nota = models.TextField(blank=True, verbose_name='nota')
    comprobante = models.FileField(
        upload_to='comprobantes/', blank=True,
        verbose_name='comprobante'
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ingreso'
        verbose_name_plural = 'Ingresos'
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.categoria} → {self.cuenta.nombre} — RD$ {self.monto}'


class Gasto(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    cuenta = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.PROTECT,
        verbose_name='método de pago'
    )
    categoria = models.ForeignKey(
        'categories.Categoria', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='categoría'
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='monto'
    )
    fecha = models.DateField(db_index=True, verbose_name='fecha')
    nota = models.TextField(blank=True, verbose_name='nota')
    comprobante = models.FileField(
        upload_to='comprobantes/', blank=True,
        verbose_name='comprobante'
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.categoria} — {self.cuenta.nombre} — RD$ {self.monto}'
