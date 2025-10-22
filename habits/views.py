from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet

from .models import Habit, HabitLog
from .serializers import HabitSerializer, HabitLogSerializer


class HabitListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class HabitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HabitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

class HabitLogViewSet(ModelViewSet):
    queryset = HabitLog.objects.all()
    serializer_class = HabitLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter to user's own logs only, and order by completed_at descending (newest first)
        return self.queryset.filter(habit__user=self.request.user).order_by('-completed_at')

    def perform_create(self, serializer):
        # Auto-set habit to one owned by user (from URL or request)
        serializer.save(habit_id=self.request.data.get('habit'))