from django.contrib import admin
from .models import SuscripcionPush


@admin.register(SuscripcionPush)
class SuscripcionPushAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'activo', 'creado_en')
    list_filter = ('activo',)
    search_fields = ('usuario__nombre_usuario', 'endpoint')
