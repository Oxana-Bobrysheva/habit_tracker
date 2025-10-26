"""
URL configuration for habit_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

from habits.views import HabitLogViewSet, PublicHabitsList

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/habits/', include('habits.urls')),
    path('api/public-habits/', PublicHabitsList.as_view(), name='public-habits'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/habit-logs/', HabitLogViewSet.as_view({
        'get': 'list', 'post': 'create'}), name='habit-log-list'),
    path('api/habit-logs/<int:pk>/', HabitLogViewSet.as_view({
        'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='habit-log-detail'),
    path('', lambda request: redirect('/api/habits/')),
]
