from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet

from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitLogViewSet(ModelViewSet):
    queryset = HabitLog.objects.all()
    serializer_class = HabitLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter to user's own logs only, and order by completed_at descending (newest first)
        return self.queryset.filter(habit__user=self.request.user).order_by('-completed_at')

    def perform_create(self, serializer):
        habit_id = self.request.data.get('habit')
        if not Habit.objects.filter(id=habit_id, user=self.request.user).exists():
            raise serializers.ValidationError("You can only log habits you own.")
        serializer.save(habit_id=habit_id)


class PublicHabitsList(generics.ListAPIView):
    serializer_class = HabitSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).select_related('user')
