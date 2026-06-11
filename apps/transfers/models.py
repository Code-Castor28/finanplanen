from django.db import models
from decimal import Decimal


class Transferencia(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    origen = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.CASCADE,
        related_name='transferencias_origen',
        verbose_name='cuenta origen'
    )
    destino = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.CASCADE,
        related_name='transferencias_destino',
        verbose_name='cuenta destino'
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='monto'
    )
    fecha = models.DateField(verbose_name='fecha')
    nota = models.TextField(blank=True, verbose_name='nota')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transferencia'
        verbose_name_plural = 'Transferencias'
        ordering = ['-fecha', '-creado']

    def __str__(self):
        return f'{self.origen.nombre} → {self.destino.nombre} — RD$ {self.monto}'
