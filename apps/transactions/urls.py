from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.TransaccionLista.as_view(), name='lista'),
    path('ingresos/', views.IngresoLista.as_view(), name='ingresos'),
    path('ingresos/crear/', views.IngresoCrear.as_view(), name='ingreso_crear'),
    path('ingresos/editar/<int:pk>/', views.IngresoEditar.as_view(), name='ingreso_editar'),
    path('ingresos/eliminar/<int:pk>/', views.IngresoEliminar.as_view(), name='ingreso_eliminar'),
    path('gastos/', views.GastoLista.as_view(), name='gastos'),
    path('gastos/crear/', views.GastoCrear.as_view(), name='gasto_crear'),
    path('gastos/editar/<int:pk>/', views.GastoEditar.as_view(), name='gasto_editar'),
    path('gastos/eliminar/<int:pk>/', views.GastoEliminar.as_view(), name='gasto_eliminar'),
]
