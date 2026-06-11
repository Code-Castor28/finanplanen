from django.contrib import admin
from .models import Categoria, Etiqueta


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'color', 'icono', 'deducible', 'activo']
    list_filter = ['activo', 'deducible']
    search_fields = ['nombre']


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'color', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']
    filter_horizontal = ['categorias']
