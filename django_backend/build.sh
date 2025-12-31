#!/usr/bin/env bash
set -o errexit

# Instalar lite_thinking_domain desde el directorio padre
pip install -e ../lite_thinking_domain

# Instalar dependencias del backend
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --no-input

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario usando Python
python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username=os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@litethinking.com'),
        password=os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123'),
        tipo='administrador',
        activo=True
    )
    print('✅ Superusuario creado')
else:
    print('⚠️ Ya existe un superusuario')
END


python manage.py activar_usuarios nombre_usuario_externo
