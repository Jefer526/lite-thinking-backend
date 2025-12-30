from rest_framework import viewsets
from lite_thinking_domain.models import Inventario, MovimientoInventario
from .serializers import InventarioSerializer, MovimientoInventarioSerializer

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
