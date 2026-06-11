from django.urls import path
from . import views

app_name = 'transfers'

urlpatterns = [
    path('', views.TransferenciaLista.as_view(), name='lista'),
    path('crear/', views.TransferenciaCrear.as_view(), name='crear'),
    path('editar/<int:pk>/', views.TransferenciaEditar.as_view(), name='editar'),
    path('eliminar/<int:pk>/', views.TransferenciaEliminar.as_view(), name='eliminar'),
]
