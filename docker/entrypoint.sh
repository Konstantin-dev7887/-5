#!/bin/sh

echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database started"

# Применяем миграции
python manage.py migrate --noinput

# Собираем статику
python manage.py collectstatic --noinput

# Запускаем gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
