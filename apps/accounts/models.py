from django.db import models
from django.utils.text import slugify


class Cuenta(models.Model):
    TIPO_CHOICES = [
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
        ('efectivo', 'Efectivo'),
    ]

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
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name='tipo')
    color = models.ForeignKey(
        'theme.Color', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='color'
    )
    icono = models.ForeignKey(
        'theme.Icono', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='icono'
    )
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='balance'
    )
    limite_credito = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name='límite de crédito'
    )
    emisor = models.CharField(
        max_length=100, blank=True, verbose_name='emisor'
    )
    ultimos_digitos = models.CharField(
        max_length=4, blank=True, verbose_name='últimos 4 dígitos'
    )
    dia_corte = models.CharField(
        max_length=20, blank=True, verbose_name='día de corte'
    )
    dia_pago = models.CharField(
        max_length=20, blank=True, verbose_name='día de pago'
    )
    vencimiento = models.CharField(
        max_length=10, blank=True, verbose_name='vencimiento'
    )
    activo = models.BooleanField(default=True, db_index=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        unique_together = ['inquilino', 'slug']

    def __str__(self):
        banco = self.emisor if self.emisor else 'N/A'
        return f'{self.nombre} | {banco} | {self.get_tipo_display()} | RD$ {self.balance:,.2f}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
