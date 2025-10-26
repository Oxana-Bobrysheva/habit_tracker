from django.urls import path

from .views import HabitListCreateView, HabitDetailView, PublicHabitsList

urlpatterns = [
    path('', HabitListCreateView.as_view(), name='habit-list-create'),
    path('<int:pk>/', HabitDetailView.as_view(), name='habit-detail'),
]
