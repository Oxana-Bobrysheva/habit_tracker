from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    frequency = models.PositiveIntegerField(default=1, help_text="Times per day/week (e.g., 1 for daily)")
    frequency_unit = models.CharField(max_length=10, choices=[('day', 'Day'), ('week', 'Week')], default='day')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.frequency < 1:
            raise ValidationError("Frequency must be at least 1.")
        super().clean()

    def __str__(self):
        return f"{self.user.username}: {self.name}"

class HabitLog(models.Model):  # For tracking completions/progress
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name='logs')
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.habit.name} - {self.completed_at.date()}"
