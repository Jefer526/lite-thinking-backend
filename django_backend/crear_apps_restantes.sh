#!/bin/bash

# Script para crear las apps restantes: productos, inventario, ia

# PRODUCTOS
cat > apps/productos/__init__.py << 'EOF'
# Productos app
EOF

cat > apps/productos/apps.py << 'EOF'
from django.apps import AppConfig

class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.productos'
    verbose_name = 'Productos'
EOF

cat > apps/productos/serializers.py << 'EOF'
from rest_framework import serializers
from lite_thinking_domain.models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
EOF

cat > apps/productos/views.py << 'EOF'
from rest_framework import viewsets
from lite_thinking_domain.models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
EOF

cat > apps/productos/urls.py << 'EOF'
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

router = DefaultRouter()
router.register(r'', ProductoViewSet, basename='producto')

urlpatterns = [path('', include(router.urls))]
EOF

# INVENTARIO
cat > apps/inventario/__init__.py << 'EOF'
# Inventario app
EOF

cat > apps/inventario/apps.py << 'EOF'
from django.apps import AppConfig

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventario'
    verbose_name = 'Inventario'
EOF

cat > apps/inventario/serializers.py << 'EOF'
from rest_framework import serializers
from lite_thinking_domain.models import Inventario, MovimientoInventario

class InventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventario
        fields = '__all__'

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = '__all__'
EOF

cat > apps/inventario/views.py << 'EOF'
from rest_framework import viewsets
from lite_thinking_domain.models import Inventario, MovimientoInventario
from .serializers import InventarioSerializer, MovimientoInventarioSerializer

class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
EOF

cat > apps/inventario/urls.py << 'EOF'
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventarioViewSet, MovimientoInventarioViewSet

router = DefaultRouter()
router.register(r'inventarios', InventarioViewSet, basename='inventario')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento')

urlpatterns = [path('', include(router.urls))]
EOF

# IA
cat > apps/ia/__init__.py << 'EOF'
# IA app
EOF

cat > apps/ia/apps.py << 'EOF'
from django.apps import AppConfig

class IAConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ia'
    verbose_name = 'Inteligencia Artificial'
EOF

cat > apps/ia/serializers.py << 'EOF'
from rest_framework import serializers
from lite_thinking_domain.models import Conversacion, Mensaje

class ConversacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversacion
        fields = '__all__'

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = '__all__'
EOF

cat > apps/ia/views.py << 'EOF'
from rest_framework import viewsets
from lite_thinking_domain.models import Conversacion, Mensaje
from .serializers import ConversacionSerializer, MensajeSerializer

class ConversacionViewSet(viewsets.ModelViewSet):
    queryset = Conversacion.objects.all()
    serializer_class = ConversacionSerializer

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer
EOF

cat > apps/ia/urls.py << 'EOF'
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversacionViewSet, MensajeViewSet

router = DefaultRouter()
router.register(r'conversaciones', ConversacionViewSet, basename='conversacion')
router.register(r'mensajes', MensajeViewSet, basename='mensaje')

urlpatterns = [path('', include(router.urls))]
EOF

echo "✅ Apps creadas: productos, inventario, ia"
