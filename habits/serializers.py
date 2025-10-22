from rest_framework import serializers
from .models import Habit, HabitLog

class HabitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = HabitLog
        fields = ['id', 'habit', 'completed_at', 'notes']
        read_only_fields = ['id']

class HabitSerializer(serializers.ModelSerializer):
    logs = HabitLogSerializer(many=True, read_only=True)  # Nested for progress view

    class Meta:
        model = Habit
        fields = ['id', 'name', 'description', 'frequency', 'frequency_unit', 'created_at', 'is_active', 'logs']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
