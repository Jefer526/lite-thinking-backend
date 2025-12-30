"""
URL Configuration para Lite Thinking Backend
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # APIs
    path('api/auth/', include('apps.autenticacion.urls')),
    path('api/empresas/', include('apps.empresas.urls')),
    path('api/productos/', include('apps.productos.urls')),
    path('api/inventario/', include('apps.inventario.urls')),
    path('api/ia/', include('apps.ia.urls')),
]

# Servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar el admin
admin.site.site_header = "Lite Thinking - Administración"
admin.site.site_title = "Lite Thinking Admin"
admin.site.index_title = "Panel de Administración"
