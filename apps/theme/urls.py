from django.urls import path
from . import views

app_name = 'theme'

urlpatterns = [
    path('colores/', views.ColorLista.as_view(), name='colores_lista'),
    path('colores/crear/', views.ColorCrear.as_view(), name='colores_crear'),
    path('colores/<int:pk>/editar/', views.ColorEditar.as_view(), name='colores_editar'),
    path('colores/<int:pk>/eliminar/', views.ColorEliminar.as_view(), name='colores_eliminar'),
    path('iconos/', views.IconoLista.as_view(), name='iconos_lista'),
    path('iconos/crear/', views.IconoCrear.as_view(), name='iconos_crear'),
    path('iconos/<int:pk>/editar/', views.IconoEditar.as_view(), name='iconos_editar'),
    path('iconos/<int:pk>/eliminar/', views.IconoEliminar.as_view(), name='iconos_eliminar'),
]
