# habits/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpRequest
from rest_framework.test import APIClient
from habits.models import Habit, HabitLog
from habits.serializers import HabitSerializer


class HabitModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Создаём приятную привычку для связи
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Pleasant Habit',
            place='Home',
            time='08:00',
            action='Relax',
            is_pleasant=True,
            frequency=1,
            frequency_unit='days',
            duration=0  # Добавлено для избежания NULL
        )
        self.habit_data = {
            'user': self.user,
            'name': 'Test Habit',
            'place': 'Office',
            'time': '09:00',
            'action': 'Drink water',
            'is_pleasant': False,
            'frequency': 1,
            'frequency_unit': 'days',
            'reward': '',  # Пустая награда, чтобы можно было использовать related_habit
            'related_habit': self.pleasant_habit,  # Экземпляр для прямого create()
            'duration': 0  # Добавлено
        }

    def test_habit_creation(self):
        habit = Habit.objects.create(**self.habit_data)
        self.assertEqual(habit.name, 'Test Habit')
        self.assertEqual(habit.user, self.user)

    def test_habit_str(self):
        habit = Habit.objects.create(**self.habit_data)
        self.assertEqual(str(habit), 'testuser: Test Habit')  # Обновлено для соответствия __str__

    def test_duration_validation(self):
        self.habit_data['duration'] = 130  # >120
        habit = Habit(**self.habit_data)
        with self.assertRaises(Exception):  # Ожидаем ValidationError
            habit.full_clean()


class HabitSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.request = HttpRequest()
        self.request.user = self.user
        # Создаём приятную привычку для связи
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Pleasant Habit',
            place='Home',
            time='08:00',
            action='Relax',
            is_pleasant=True,
            frequency=1,
            frequency_unit='days',
            duration=0  # Добавлено для избежания NULL
        )
        self.data = {
            'name': 'Test Habit',
            'place': 'Office',
            'time': '09:00',
            'action': 'Drink water',
            'is_pleasant': False,
            'frequency': 1,
            'frequency_unit': 'days',
            'reward': 'Candy',  # Награда для неприятной привычки
            'related_habit': None,  # None, чтобы избежать конфликта с reward
            'duration': 0  # Добавлено
        }
        self.serializer = HabitSerializer(data=self.data, context={'request': self.request})

    def test_serializer_valid(self):
        self.assertTrue(self.serializer.is_valid())

    def test_serializer_invalid_duration(self):
        self.data['duration'] = 130
        serializer = HabitSerializer(data=self.data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

    def test_serializer_reward_only_for_unpleasant(self):
        self.data['is_pleasant'] = True
        self.data['reward'] = 'Candy'
        serializer = HabitSerializer(data=self.data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())


class HabitAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Создаём приятную привычку для связи
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Pleasant Habit',
            place='Home',
            time='08:00',
            action='Relax',
            is_pleasant=True,
            frequency=1,
            frequency_unit='days',
            duration=0  # Добавлено для избежания NULL
        )
        self.habit_data = {
            'name': 'Test Habit',
            'place': 'Office',
            'time': '09:00',
            'action': 'Drink water',
            'is_pleasant': False,
            'frequency': 1,
            'frequency_unit': 'days',
            'reward': '',  # Пустая награда для API
            'related_habit': self.pleasant_habit.id,  # ID для API/сериализатора
            'duration': 0  # Добавлено
        }

    def test_get_habits(self):
        response = self.client.get('/api/habits/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_habit(self):
        response = self.client.post('/api/habits/', self.habit_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Habit.objects.count(), 2)

    def test_update_habit(self):
        habit = Habit.objects.create(
            user=self.user, **{**self.habit_data, 'related_habit': self.pleasant_habit})
        update_data = self.habit_data.copy()
        update_data['name'] = 'Updated Habit'
        response = self.client.put(f'/api/habits/{habit.id}/', update_data, format='json')
        self.assertEqual(response.status_code, 200)
        habit.refresh_from_db()
        self.assertEqual(habit.name, 'Updated Habit')

    def test_delete_habit(self):
        habit = Habit.objects.create(
            user=self.user, **{**self.habit_data, 'related_habit': self.pleasant_habit})
        response = self.client.delete(f'/api/habits/{habit.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Habit.objects.count(), 1)  # Обновлено: 1 pleasant remains

    def test_public_habits_unauthenticated(self):
        self.client.logout()  # Разлогиниваемся
        habit = Habit.objects.create(
            user=self.user, **{**self.habit_data, 'is_public': True,
                               'related_habit': self.pleasant_habit})
        print(habit)
        response = self.client.get('/api/public-habits/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)


class HabitLogAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        # Создаём приятную привычку для связи
        self.pleasant_habit = Habit.objects.create(
            user=self.user,
            name='Pleasant Habit',
            place='Home',
            time='08:00',
            action='Relax',
            is_pleasant=True,
            frequency=1,
            frequency_unit='days',
            duration=0  # Добавлено для избежания NULL
        )
        self.habit = Habit.objects.create(
            user=self.user,
            name='Test Habit',
            place='Office',
            time='09:00',
            action='Drink water',
            is_pleasant=False,
            frequency=1,
            frequency_unit='days',
            reward='',
            related_habit=self.pleasant_habit,  # Экземпляр
            duration=0  # Добавлено
        )

    def test_get_habit_logs(self):
        # Создаём лог с habit и notes (completed_at auto-set)
        HabitLog.objects.create(habit=self.habit, notes='Test log')
        response = self.client.get('/api/habit-logs/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_habit_log(self):
        # Постим данные с habit и notes
        data = {'habit': self.habit.id, 'notes': 'Completed today'}
        response = self.client.post('/api/habit-logs/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(HabitLog.objects.count(), 1)
