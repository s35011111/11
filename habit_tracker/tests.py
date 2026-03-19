# Create your tests here.

from django.test import TestCase
from django.utils import timezone

from habit_tracker.models import Habit, CustomUser
from habit_tracker.tasks import send_habit_reminders
from unittest.mock import patch
from django.test import override_settings

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class HabitReminderTest(APITestCase):
    @patch('habit_tracker.tasks.Bot.send_message')
    def test_send_reminder(self, mock_send):
        from habit_tracker.tasks import send_habit_reminders
        send_habit_reminders()
        mock_send.assert_called_once()


User = get_user_model()


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class HabitAPITest(APITestCase):
    def setUp(self):
        self.regular_user = User.objects.create_user(username='test',
                                                     password='test123')

        refresh = RefreshToken.for_user(self.regular_user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_habit(self):
        data = {
            'place': 'Home',
            'action': 'Drink water',
            'habit_type': 'useful',
            'reward': 'Feel good',
            'start_time': '2025-03-17T10:00:00Z',
            'duration': '10',
            'periodicity': 1,
            'is_public': True,
            'user': 1
        }
        response = self.client.post('/api/habits/', data, format='json')
        self.assertEqual(response.data['action'], 'Drink water')
        self.assertEqual(response.status_code, 201)

    def test_user_login(self):

        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.data[0]['username'], 'test')


class TaskTest(TestCase):
    @patch('habit_tracker.tasks.Bot.send_message')
    def test_send_habit_reminders(self, mock_send):
        user = CustomUser.objects.create(username='tester',
                                         telegram_chat_id='12345')
        habit = Habit.objects.create(
            user=user,
            action='Test',
            start_time=timezone.now() - timezone.timedelta(minutes=5),
            next_reminder=timezone.now() - timezone.timedelta(minutes=1),
            periodicity=1,
            duration='10',
            is_public=True,
            habit_type='pleasant',


        )
        send_habit_reminders()
        mock_send.assert_called_once_with(chat_id='12345', text=...)
        habit.refresh_from_db()
        self.assertGreater(habit.next_reminder, timezone.now())
