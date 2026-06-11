from django.db import models


class Presupuesto(models.Model):
    inquilino = models.ForeignKey(
        'users.Tenant', on_delete=models.CASCADE,
        verbose_name='inquilino'
    )
    usuario = models.ForeignKey(
        'users.Usuario', on_delete=models.CASCADE,
        verbose_name='usuario'
    )
    categoria = models.ForeignKey(
        'categories.Categoria', on_delete=models.CASCADE,
        verbose_name='categoría'
    )
    monto_limite = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='límite mensual'
    )
    monto_gastado = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='monto gastado'
    )
    mes = models.IntegerField(verbose_name='mes')
    año = models.IntegerField(verbose_name='año')
    activo = models.BooleanField(default=True, verbose_name='activo')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        unique_together = ['inquilino', 'categoria', 'mes', 'año']
        ordering = ['-año', '-mes', 'categoria__nombre']

    def __str__(self):
        return f'{self.categoria.nombre} ({self.mes}/{self.año})'

    def progreso_pct(self):
        if self.monto_limite:
            return round(float(self.monto_gastado) / float(self.monto_limite) * 100, 1)
        return 0

    @property
    def restante(self):
        return self.monto_limite - self.monto_gastado

    @property
    def excedido(self):
        return self.monto_gastado - self.monto_limite
