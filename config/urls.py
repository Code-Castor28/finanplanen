from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('acceso/', include('apps.users.urls')),
    path('tema/', include('apps.theme.urls')),
    path('cuentas/', include('apps.accounts.urls')),
    path('presupuestos/', include('apps.budgets.urls')),
    path('categorias/', include('apps.categories.urls')),
    path('ahorros/', include('apps.savings.urls')),
    path('transacciones/', include('apps.transactions.urls')),
    path('transferencias/', include('apps.transfers.urls')),
    path('', include('apps.core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
