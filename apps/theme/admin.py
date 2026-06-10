from django.contrib import admin
from .models import Color, Icono


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'hex', 'inquilino', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'slug']


@admin.register(Icono)
class IconoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'clase_css', 'inquilino', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'slug']
