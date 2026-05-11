from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

from users.models import User
from .models import Habit
from .tasks import send_habit_reminders


class HabitTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.client.force_authenticate(user=self.user)
        self.habit_data = {
            'place': 'Дом',
            'time': '10:00:00',
            'action': 'Читать',
            'duration': 30,
            'periodicity': 1,
            'is_pleasant': False,
            'reward': 'Кофе',
        }

    def test_create_habit(self):
        response = self.client.post(
            reverse('habit-list-create'),
            self.habit_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)

    def test_list_habits(self):
        Habit.objects.create(user=self.user, **self.habit_data)
        response = self.client.get(reverse('habit-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class HabitValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='valuser', password='valpass')
        self.client.force_authenticate(user=self.user)

    def test_cannot_set_both_related_habit_and_reward(self):
        pleasant = Habit.objects.create(
            user=self.user, place='Дом', time='10:00', action='Чай',
            is_pleasant=True, duration=30
        )
        data = {
            'place': 'Дом', 'time': '10:00', 'action': 'Зарядка',
            'is_pleasant': False, 'related_habit': pleasant.id, 'reward': 'Кофе',
            'duration': 30, 'periodicity': 1
        }
        response = self.client.post(
            reverse('habit-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(len(response.data) > 0)  # есть ошибка

    def test_duration_cannot_exceed_120(self):
        data = {
            'place': 'Дом', 'time': '10:00', 'action': 'Зарядка',
            'is_pleasant': False, 'reward': 'Кофе',
            'duration': 150, 'periodicity': 1
        }
        response = self.client.post(
            reverse('habit-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_set_related_habit_not_pleasant(self):
        not_pleasant = Habit.objects.create(
            user=self.user, place='Дом', time='10:00', action='Чай',
            is_pleasant=False, duration=30
        )
        data = {
            'place': 'Дом', 'time': '10:00', 'action': 'Зарядка',
            'is_pleasant': False, 'related_habit': not_pleasant.id,
            'duration': 30, 'periodicity': 1
        }
        response = self.client.post(
            reverse('habit-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pleasant_habit_cannot_have_reward_or_related(self):
        pleasant_related = Habit.objects.create(
            user=self.user, place='Дом', time='10:00', action='Чай',
            is_pleasant=True, duration=30
        )
        # с вознаграждением
        data1 = {
            'place': 'Дом', 'time': '10:00', 'action': 'Отдых',
            'is_pleasant': True, 'reward': 'Печенье', 'duration': 30
        }
        response1 = self.client.post(
            reverse('habit-list-create'), data1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        # со связанной привычкой
        data2 = {
            'place': 'Дом', 'time': '10:00', 'action': 'Отдых',
            'is_pleasant': True, 'related_habit': pleasant_related.id, 'duration': 30
        }
        response2 = self.client.post(
            reverse('habit-list-create'), data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_periodicity_min_value(self):
        data = {
            'place': 'Дом', 'time': '10:00', 'action': 'Зарядка',
            'is_pleasant': False, 'reward': 'Кофе',
            'duration': 30, 'periodicity': 0   # меньше минимума
        }
        response = self.client.post(
            reverse('habit-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_periodicity_max_value(self):
        data = {
            'place': 'Дом', 'time': '10:00', 'action': 'Зарядка',
            'is_pleasant': False, 'reward': 'Кофе',
            'duration': 30, 'periodicity': 8   # больше 7
        }
        response = self.client.post(
            reverse('habit-list-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_public_habits_accessible_without_auth(self):
        Habit.objects.create(user=self.user, place='Парк', time='12:00',
                             action='Бег', is_public=True, duration=30)
        self.client.logout()
        response = self.client.get(reverse('public-habit-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class HabitPermissionsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1', password='pass1')
        self.user2 = User.objects.create_user(
            username='user2', password='pass2')
        self.habit = Habit.objects.create(
            user=self.user1, place='Дом', time='10:00', action='Бег', duration=30
        )
        self.url = reverse('habit-detail', kwargs={'pk': self.habit.pk})

    def test_owner_can_edit_habit(self):
        self.client.force_authenticate(user=self.user1)
        data = {'action': 'Бегать быстро'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_owner_cannot_edit_habit(self):
        self.client.force_authenticate(user=self.user2)
        data = {'action': 'Бегать быстро'}
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CeleryTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='taskuser', password='pass')
        self.user.telegram_chat_id = '123456'
        self.user.save()
        self.habit = Habit.objects.create(
            user=self.user, place='Дом', time=timezone.now().time(),
            action='Тест', duration=30
        )

    @patch('habits.tasks.telebot.TeleBot')
    def test_send_habit_reminders_task(self, mock_bot):
        send_habit_reminders()
        self.assertTrue(mock_bot.called)
