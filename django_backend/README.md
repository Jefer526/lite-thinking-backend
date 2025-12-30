# 🚀 Django Backend - Lite Thinking

**Backend Django que instala y usa el Core de Dominio**

---

## ✅ Estructura Creada:

```
django_backend/
├── pyproject.toml          # Poetry + Core de Dominio
├── .env.example            # Variables de entorno
├── manage.py               # Django management
├── config/
│   ├── settings.py         # ✅ USA AUTH_USER_MODEL del Core
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── apps/
    ├── autenticacion/      # ✅ COMPLETO
    │   ├── serializers.py
    │   ├── views.py
    │   ├── permissions.py
    │   ├── urls.py
    │   └── apps.py
    ├── empresas/           # ✅ COMPLETO
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   └── apps.py
    ├── productos/          # ⚠️ CREAR (ver abajo)
    ├── inventario/         # ⚠️ CREAR (ver abajo)
    └── ia/                 # ⚠️ CREAR (ver abajo)
```

---

## 🔧 INSTALACIÓN Y CONFIGURACIÓN

### **1. Preparar el Entorno**

```bash
# Ir al directorio del backend
cd django_backend

# Instalar Poetry si no lo tienes
curl -sSL https://install.python-poetry.org | python3 -

# Instalar dependencias (incluye el Core de Dominio)
poetry install

# Activar el entorno virtual
poetry shell
```

### **2. Configurar Variables de Entorno**

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

**Variables importantes:**
```env
SECRET_KEY=tu-secret-key-super-secreta
DEBUG=True
DB_NAME=lite_thinking_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### **3. Configurar PostgreSQL**

```bash
# Crear la base de datos
psql -U postgres
CREATE DATABASE lite_thinking_db;
\q
```

### **4. Ejecutar Migraciones**

```bash
# Crear migraciones del Core de Dominio
python manage.py makemigrations lite_thinking_domain

# Aplicar todas las migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

### **5. Ejecutar el Servidor**

```bash
# Correr el servidor de desarrollo
python manage.py runserver

# El servidor estará en: http://localhost:8000
# Admin: http://localhost:8000/admin
```

---

## 📝 CREAR LAS APPS RESTANTES

Las apps **productos**, **inventario** e **ia** siguen el mismo patrón que **empresas**. 

### **Patrón para cada app:**

#### **1. serializers.py**

```python
from rest_framework import serializers
from lite_thinking_domain.models import Producto  # Cambiar según modelo

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
```

#### **2. views.py**

```python
from rest_framework import viewsets
from lite_thinking_domain.models import Producto  # Cambiar según modelo
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
```

#### **3. urls.py**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

router = DefaultRouter()
router.register(r'', ProductoViewSet, basename='producto')

urlpatterns = [
    path('', include(router.urls)),
]
```

#### **4. apps.py**

```python
from django.apps import AppConfig

class ProductosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.productos'
    verbose_name = 'Productos'
```

#### **5. __init__.py**

```python
# Productos app
```

---

## 🎯 APPS A CREAR

### **App: productos**
- Modelo del Core: `Producto`
- Funcionalidades: CRUD productos, código automático, precios multi-moneda

### **App: inventario**
- Modelos del Core: `Inventario`, `MovimientoInventario`
- Funcionalidades: Entrada/salida, ajustes, reportes

### **App: ia**
- Modelos del Core: `Conversacion`, `Mensaje`
- Funcionalidades: Chatbot con Google Gemini

---

## 🧪 PROBAR LOS ENDPOINTS

### **Autenticación:**

```bash
# Registro
curl -X POST http://localhost:8000/api/auth/usuarios/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Admin",
    "last_name": "User",
    "tipo": "administrador"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'
```

### **Empresas:**

```bash
# Listar empresas (requiere token)
curl http://localhost:8000/api/empresas/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Crear empresa
curl -X POST http://localhost:8000/api/empresas/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nit": "900123456",
    "nombre": "Mi Empresa",
    "direccion": "Calle 123",
    "telefono": "3001234567",
    "email": "contacto@empresa.com"
  }'
```

---

## 📂 ARCHIVOS ADICIONALES (Opcional)

### **Signal para crear inventario automáticamente:**

```python
# apps/productos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from lite_thinking_domain.models import Producto, Inventario

@receiver(post_save, sender=Producto)
def crear_inventario_automatico(sender, instance, created, **kwargs):
    if created:
        Inventario.objects.create(
            producto=instance,
            cantidad_actual=0,
            ubicacion=""
        )
```

---

## ✅ VENTAJAS DE ESTA ARQUITECTURA

1. ✅ **Modelos en el Core** - Lógica de negocio centralizada
2. ✅ **Backend ligero** - Solo serializers, views, urls
3. ✅ **Fácil de testear** - Tests separados por capa
4. ✅ **Escalable** - Agregar nuevas apps es simple
5. ✅ **Mantenible** - Cambios en modelos solo en el Core

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Completar las 3 apps restantes (productos, inventario, ia)
2. ✅ Agregar admin.py para cada app si lo necesitas
3. ✅ Crear tests para cada endpoint
4. ✅ Configurar CORS para tu frontend
5. ✅ Deploy a producción (Render, Railway, AWS)

---

## 📞 SOPORTE

Si tienes dudas sobre cómo crear las apps restantes, sigue el patrón de **empresas** y **autenticacion** que ya están completas.

**¡Todo listo para empezar a desarrollar!** 🎉
