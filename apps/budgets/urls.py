from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.PresupuestoLista.as_view(), name='lista'),
]
