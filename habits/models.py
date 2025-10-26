from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    place = models.CharField(max_length=255, help_text="Место выполнения привычки (например, 'дом')")
    time = models.TimeField(help_text="Время выполнения (например, 07:00)")
    action = models.CharField(max_length=255, help_text="Действие привычки (например, 'выпить стакан воды')")
    is_pleasant = models.BooleanField(default=False, help_text="Приятная привычка (без вознаграждения)")

    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_from',
        limit_choices_to={'is_pleasant': True},  # Только приятные привычки
        help_text="Связанная приятная привычка (альтернатива вознаграждению)"
    )

    frequency = models.PositiveIntegerField(default=1, help_text="Частота выполнения")
    frequency_unit = models.CharField(
        max_length=10,
        choices=[('days', 'Дни'), ('weeks', 'Недели'), ('months', 'Месяцы')],
        default='days',
        help_text="Единица измерения частоты"
    )

    reward = models.CharField(max_length=255, null=True, blank=True, help_text="Вознаграждение после выполнения")
    duration = models.PositiveIntegerField(help_text="Время на выполнение в секундах (<=120)")
    is_public = models.BooleanField(default=False, help_text="Публичная привычка (другие могут видеть)")

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def clean(self):
        super().clean()

        # Валидация frequency в зависимости от unit
        if self.frequency_unit == 'days' and not (1 <= self.frequency <= 7):
            raise ValidationError("Для дней периодичность должна быть от 1 до 7.")
        elif self.frequency_unit == 'weeks' and not (1 <= self.frequency <= 4):
            raise ValidationError("Для недель периодичность должна быть от 1 до 4.")
        elif self.frequency_unit == 'months' and not (1 <= self.frequency <= 12):
            raise ValidationError("Для месяцев периодичность должна быть от 1 до 12.")

        # Валидация duration (<=120 сек)
        if self.duration > 120:
            raise ValidationError("Время на выполнение не может превышать 120 секунд.")

        # Исключить одновременный выбор related_habit и reward
        if self.related_habit and self.reward:
            raise ValidationError("Нельзя выбрать и связанную привычку, и вознаграждение одновременно.")

        # Приятная привычка не может иметь reward или related_habit
        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError("Приятная привычка не может иметь вознаграждение или связанную привычку.")

        # related_habit должен ссылаться на приятную привычку
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной.")

    def __str__(self):
        return f"{self.user.username}: {self.name}"


class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.habit.name} - {self.completed_at.date()}"


class TelegramChat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Telegram Chat"
