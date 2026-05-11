from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch
import json
import time


class TelegramWebhookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('telegram_webhook')

    def test_webhook_requires_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    @patch('telegram_bot.views.bot')  # Подменяем бота
    def test_webhook_with_start_command(self, mock_bot):
        payload = {
            'update_id': 12345,
            'message': {
                'message_id': 1,
                'from': {
                    'id': 111,
                    'is_bot': False,
                    'first_name': 'Test',
                    'username': 'testuser'
                },
                'chat': {
                    'id': 111,
                    'type': 'private'
                },
                'date': int(time.time()),
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
        # Бот вызывается
        self.assertTrue(mock_bot.send_message.called)


class TelegramWebhookErrorTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('telegram_webhook')

    def test_webhook_handles_invalid_json(self):
        response = self.client.post(
            self.url,
            data='not a json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['status'], 'error')

    @patch('telegram_bot.views.bot')  # Подменяем бота
    def test_webhook_handles_user_not_found(self, mock_bot):
        payload = {
            'update_id': 12345,
            'message': {
                'message_id': 1,
                'from': {
                    'id': 222,
                    'is_bot': False,
                    'first_name': 'Unknown',
                    'username': 'unknown_user_123'
                },
                'chat': {
                    'id': 222,
                    'type': 'private'
                },
                'date': int(time.time()),
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
        self.assertTrue(mock_bot.send_message.called)
