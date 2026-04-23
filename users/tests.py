from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import User

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'password': 'strongpass123',
            'email': 'new@example.com'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_token_obtain(self):
        User.objects.create_user(username='tokenuser', password='tokenpass')
        data = {'username': 'tokenuser', 'password': 'tokenpass'}
        response = self.client.post(self.token_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

class UserModelTest(TestCase):
    def test_user_str_method(self):
        """Тест строкового представления пользователя."""
        user = User.objects.create_user(username='testuser_str')
        self.assertEqual(str(user), 'testuser_str')

