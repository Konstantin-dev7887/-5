FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Установка Python-зависимостей
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копирование проекта
COPY . /app/

# Копируем entrypoint-скрипт и делаем его исполняемым
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Сборка статики
RUN python manage.py collectstatic --noinput || true

ENTRYPOINT ["/entrypoint.sh"]
