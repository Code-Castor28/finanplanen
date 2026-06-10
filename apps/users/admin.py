from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Tenant, Usuario


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'slug', 'activo', 'creado']
    prepopulated_fields = {'slug': ['nombre']}


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('nombre_usuario', 'password')}),
        ('Información personal', {
            'fields': ('nombre', 'apellido', 'correo', 'telefono', 'avatar')
        }),
        ('Finanzas', {
            'fields': ('ingreso_mensual', 'inquilino')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas', {
            'fields': ('last_login', 'date_joined', 'creado', 'actualizado')
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('nombre_usuario', 'correo', 'nombre', 'apellido', 'password1', 'password2'),
        }),
    )
    list_display = ('nombre_usuario', 'correo', 'nombre', 'apellido', 'inquilino', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('nombre_usuario', 'correo', 'nombre', 'apellido')
    ordering = ('nombre_usuario',)
    readonly_fields = ('creado', 'actualizado')
