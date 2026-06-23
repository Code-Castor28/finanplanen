from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal
from dateutil.relativedelta import relativedelta


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
        'accounts.Cuenta', on_delete=models.PROTECT,
        related_name='transferencias_origen',
        verbose_name='cuenta origen'
    )
    destino = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.PROTECT,
        related_name='transferencias_destino',
        verbose_name='cuenta destino'
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='monto'
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


class RecurrenciaTransferencia(models.Model):
    PERIODICIDAD_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
    ]

    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    origen = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.PROTECT,
        related_name='recurrencias_origen',
        verbose_name='cuenta origen'
    )
    destino = models.ForeignKey(
        'accounts.Cuenta', on_delete=models.PROTECT,
        related_name='recurrencias_destino',
        verbose_name='cuenta destino'
    )
    monto = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='monto'
    )
    periodicidad = models.CharField(
        max_length=10, choices=PERIODICIDAD_CHOICES,
        verbose_name='periodicidad'
    )
    dia = models.IntegerField(
        default=1, verbose_name='día',
        help_text='Día del mes (1-31) o día de semana (0=lun, 6=dom)'
    )
    proxima_ejecucion = models.DateField(db_index=True, verbose_name='próxima ejecución')
    nota = models.TextField(blank=True, verbose_name='nota')
    activo = models.BooleanField(default=True, db_index=True, verbose_name='activo')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Recurrencia de Transferencia'
        verbose_name_plural = 'Recurrencias de Transferencias'
        ordering = ['proxima_ejecucion']

    def __str__(self):
        return f'{self.origen.nombre} → {self.destino.nombre} ({self.get_periodicidad_display()})'

    def calcular_proxima_ejecucion(self):
        if self.periodicidad == 'diario':
            return self.proxima_ejecucion + relativedelta(days=1)
        elif self.periodicidad == 'semanal':
            return self.proxima_ejecucion + relativedelta(weeks=1)
        elif self.periodicidad == 'mensual':
            return self.proxima_ejecucion + relativedelta(months=1)
        return self.proxima_ejecucion
