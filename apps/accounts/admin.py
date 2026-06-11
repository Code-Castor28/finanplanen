from django.contrib import admin
from .models import Cuenta


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'balance', 'color', 'activo']
    list_filter = ['tipo', 'activo']
    search_fields = ['nombre', 'emisor']
