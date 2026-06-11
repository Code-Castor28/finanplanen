from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoriaLista.as_view(), name='lista'),
    path('crear/', views.CategoriaCrear.as_view(), name='crear'),
    path('<int:pk>/editar/', views.CategoriaEditar.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.CategoriaEliminar.as_view(), name='eliminar'),
    path('etiquetas/', views.EtiquetaLista.as_view(), name='etiqueta_lista'),
    path('etiquetas/crear/', views.EtiquetaCrear.as_view(), name='etiqueta_crear'),
    path('etiquetas/<int:pk>/editar/', views.EtiquetaEditar.as_view(), name='etiqueta_editar'),
    path('etiquetas/<int:pk>/eliminar/', views.EtiquetaEliminar.as_view(), name='etiqueta_eliminar'),
]
