from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Tenant(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inquilino'
        verbose_name_plural = 'Inquilinos'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Usuario(AbstractUser):
    username = None
    first_name = None
    last_name = None
    email = None

    nombre_usuario = models.CharField('nombre de usuario', max_length=150, unique=True)
    correo = models.EmailField('correo electrónico', unique=True)
    nombre = models.CharField('nombre', max_length=30, blank=True)
    apellido = models.CharField('apellido', max_length=150, blank=True)
    inquilino = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name='inquilino'
    )
    telefono = models.CharField('teléfono', max_length=15, blank=True, null=True)
    avatar = models.ImageField('avatar', upload_to='avatares/', blank=True, null=True)
    ingreso_mensual = models.DecimalField(
        'ingreso mensual', max_digits=12, decimal_places=2, default=0
    )
    creado = models.DateTimeField('creado', auto_now_add=True)
    actualizado = models.DateTimeField('actualizado', auto_now=True)

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['correo', 'nombre', 'apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.nombre_usuario
