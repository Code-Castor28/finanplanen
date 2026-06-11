from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.PresupuestoLista.as_view(), name='lista'),
    path('crear/', views.PresupuestoCrear.as_view(), name='crear'),
    path('editar/<int:pk>/', views.PresupuestoEditar.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.PresupuestoEliminar.as_view(), name='eliminar'),
]
