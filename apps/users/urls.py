from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'users'

urlpatterns = [
    path('ingresar/', views.IniciarSesion.as_view(), name='ingresar'),
    path('salir/', LogoutView.as_view(next_page='users:ingresar'), name='salir'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
