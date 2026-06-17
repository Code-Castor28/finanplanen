from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('api/guardar/', views.guardar_suscripcion, name='guardar'),
    path('api/eliminar/', views.eliminar_suscripcion, name='eliminar'),
]
