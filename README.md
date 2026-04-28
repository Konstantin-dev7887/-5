# Трекер привычек (Habit Tracker)

API для управления полезными привычками с напоминаниями в Telegram. Создано на Django REST Framework.

## Локальный запуск

1. Клонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd habit_tracker
```

1. Установите зависимости:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```
2. Создайте файл .env на основе .env.example и заполните его.
3. Примените миграции:
   ```bash
   python manage.py migrate
   ```
4. Запустите сервер:
   ```bash
   python manage.py runserver
   ```

Запуск через Docker Compose

1. Скопируйте .env.example в .env и отредактируйте.
2. Запустите одной командой:
   ```bash
   docker compose up -d --build
   ```
3. Откройте http://localhost/swagger/

CI/CD (GitHub Actions)

При пуше в main автоматически:

· запускаются тесты и линтинг,
· собираются Docker-образы,
· проект деплоится на виртуальной машине GitHub (раннере) и проверяется доступность API.

Необходимые секреты в репозитории: DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY, TELEGRAM_BOT_TOKEN.

Документация API

Swagger UI: /swagger/
ReDoc: /redoc/

Технологии

Python, Django REST Framework, PostgreSQL, Redis, Celery, Telegram Bot API, Docker, Nginx, GitHub Actions.
