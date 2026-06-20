from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.CuentaLista.as_view(), name='lista'),
    path('crear/', views.CuentaCrear.as_view(), name='crear'),
    path('<int:pk>/editar/', views.CuentaEditar.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.CuentaEliminar.as_view(), name='eliminar'),
    path('validar-campo/', views.validar_campo, name='validar_campo'),
]
