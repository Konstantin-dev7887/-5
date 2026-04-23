from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.conf import settings
import json

class TelegramWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('telegram_webhook')

    def test_webhook_requires_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)  # Method not allowed

    def test_webhook_with_start_command(self):
        payload = {
            'update_id': 12345,
            'message': {
                'message_id': 1,
                'from': {'id': 111, 'username': 'testuser'},
                'chat': {'id': 111},
                'text': '/start'
            }
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

class TelegramWebhookErrorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('telegram_webhook')

    def test_webhook_handles_invalid_json(self):
        """Тест на обработку некорректного JSON."""
        response = self.client.post(
            self.url,
            data='not a json',
            content_type='application/json'
        )
        # Ожидается код 500, так как в нашем view стоит общий except
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['status'], 'error')

    def test_webhook_handles_user_not_found(self):
        """Тест на случай, если пользователь с таким username не найден."""
        payload = {
            'update_id': 12345,
            'message': {
                'message_id': 1,
                'from': {'id': 222, 'username': 'unknown_user_123'},
                'chat': {'id': 222},
                'text': '/start'
            }
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Статус должен быть 200 (мы отправляем JsonResponse со статусом ok),
        # ошибка логируется внутри, но ответ всё равно 200
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

