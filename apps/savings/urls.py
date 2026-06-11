from django.urls import path
from . import views

app_name = 'savings'

urlpatterns = [
    path('', views.MetaAhorroLista.as_view(), name='lista'),
    path('crear/', views.MetaAhorroCrear.as_view(), name='meta_crear'),
    path('editar/<int:pk>/', views.MetaAhorroEditar.as_view(), name='meta_editar'),
    path('eliminar/<int:pk>/', views.MetaAhorroEliminar.as_view(), name='meta_eliminar'),
    path('deposito/crear/', views.DepositoAhorroCrear.as_view(), name='deposito_crear'),
    path('deposito/eliminar/<int:pk>/', views.DepositoAhorroEliminar.as_view(), name='deposito_eliminar'),
]
