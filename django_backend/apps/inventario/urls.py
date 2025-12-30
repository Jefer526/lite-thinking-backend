from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventarioViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register(r'inventarios', InventarioViewSet, basename='inventario')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento')

urlpatterns = [path('', include(router.urls))]
