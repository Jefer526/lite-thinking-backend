# 📦 Lite Thinking Domain

**Core de Dominio** - Modelos Django reutilizables con lógica de negocio

## 🎯 Descripción

Este paquete contiene los **modelos Django puros** del sistema Lite Thinking, diseñados para ser instalados y reutilizados en múltiples backends Django.

### Características:
- ✅ Modelos Django con toda la lógica de negocio
- ✅ Validaciones de dominio integradas
- ✅ Sin acceso directo a base de datos (el backend configura la BD)
- ✅ Empaquetado con Poetry para fácil instalación
- ✅ Listo para usar con `pip install` o Poetry

## 📋 Modelos Incluidos

### 1. **Usuario** (`lite_thinking_domain.models.Usuario`)
- Modelo basado en `AbstractUser`
- Tipos: Administrador y Externo
- Gestión de permisos y accesos

### 2. **Empresa** (`lite_thinking_domain.models.Empresa`)
- Gestión de empresas con validación de NIT
- Activación/desactivación
- Auditoría automática

### 3. **Producto** (`lite_thinking_domain.models.Producto`)
- Productos con código automático
- Precios multi-moneda (USD, COP, EUR)
- Tipos: Físico, Digital, Servicio

### 4. **Inventario** (`lite_thinking_domain.models.Inventario`)
- Control de stock en tiempo real
- Sistema de reservas
- Movimientos de entrada/salida

### 5. **Conversación** (`lite_thinking_domain.models.Conversacion`)
- Sistema de chatbot conversacional
- Mensajes usuario/asistente
- Historial de conversaciones

## 🚀 Instalación

### Desde el repositorio local:
```bash
# Con Poetry (recomendado)
poetry add /path/to/lite_thinking_domain

# Con pip
pip install /path/to/lite_thinking_domain
```

### Desde GitHub:
```bash
poetry add git+https://github.com/tu-usuario/lite-thinking-domain.git
```

## 💻 Uso en Django Backend

### 1. Agregar a `INSTALLED_APPS`:
```python
# settings.py
INSTALLED_APPS = [
    # ... otras apps
    'lite_thinking_domain',
]

# Configurar modelo de usuario personalizado
AUTH_USER_MODEL = 'lite_thinking_domain.Usuario'
```

### 2. Configurar base de datos:
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lite_thinking_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Ejecutar migraciones:
```bash
python manage.py makemigrations lite_thinking_domain
python manage.py migrate
```

### 4. Usar los modelos:
```python
from lite_thinking_domain.models import Empresa, Producto, Inventario

# Crear empresa
empresa = Empresa.objects.create(
    nit="900123456",
    nombre="Mi Empresa",
    direccion="Calle 123",
    telefono="3001234567",
    email="contacto@empresa.com"
)

# Crear producto
producto = Producto.objects.create(
    empresa=empresa,
    codigo="LA-001",
    nombre="Laptop Dell",
    descripcion="Laptop profesional",
    precio_usd=1200.00,
    tipo="fisico"
)

# Consultar inventario
inventario = producto.inventario
print(f"Stock actual: {inventario.cantidad_actual}")
```

## 🏗️ Arquitectura

```
Core de Dominio (este paquete)
    ↓ (se instala con Poetry/pip)
Django Backend
    ├── settings.py (configura DATABASES)
    ├── apps/
    │   ├── serializers.py (DRF)
    │   ├── views.py (APIs REST)
    │   └── urls.py
    └── Usa los modelos del Core
```

## 📝 Validaciones Incluidas

Todos los modelos incluyen validaciones de dominio:
- ✅ NIT válido (9-15 caracteres)
- ✅ Precios positivos
- ✅ Stock no negativo
- ✅ Emails válidos
- ✅ Códigos únicos

## 🧪 Testing

```bash
# Ejecutar tests
poetry run pytest

# Con coverage
poetry run pytest --cov=lite_thinking_domain
```

## 📦 Desarrollo

### Instalar dependencias:
```bash
poetry install
```

### Formatear código:
```bash
poetry run black src/
```

### Linting:
```bash
poetry run flake8 src/
```

## 📄 Licencia

Privado - Lite Thinking © 2024

## 👨‍💻 Autor

Jeffer - Backend Developer
