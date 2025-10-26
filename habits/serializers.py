from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from .models import Habit, HabitLog

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'completed_at', 'notes']
        read_only_fields = ['id']

class HabitSerializer(serializers.ModelSerializer):
    logs = HabitLogSerializer(many=True, read_only=True)  # Nested для просмотра прогресса (логов)
    current_streak = serializers.SerializerMethodField()  # Текущий стрик подряд дней
    total_completions = serializers.SerializerMethodField()  # Общее число логов

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'name', 'description',
            'place', 'time', 'action', 'is_pleasant',
            'related_habit', 'frequency', 'frequency_unit',
            'reward', 'duration', 'is_public',
            'created_at', 'is_active', 'logs',
            'current_streak', 'total_completions'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'current_streak', 'total_completions']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        # Валидация на уровне сериализатора (дублируем clean() из модели для API)
        instance = self.instance or Habit(user=self.context['request'].user)
        for key, value in data.items():
            setattr(instance, key, value)
        try:
            instance.full_clean()
        except serializers.ValidationError as e:
            raise e
        return data

    def get_current_streak(self, obj):
        today = timezone.now().date()
        logs = HabitLog.objects.filter(habit=obj).order_by('-completed_at')
        streak = 0
        for log in logs:
            if log.completed_at.date() == today - timedelta(days=streak):
                streak += 1
            else:
                break
        return streak

    def get_total_completions(self, obj):
        return HabitLog.objects.filter(habit=obj).count()
