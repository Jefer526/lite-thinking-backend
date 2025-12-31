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