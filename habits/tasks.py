from celery import shared_task
from django.utils import timezone
from datetime import time


@shared_task
def send_daily_habits_reminders():
    """
    Sends daily habit reminders to users via Telegram at 8:00 AM.
    Queries active habits and notifies users.
    """
    from .models import Habit
    from django.contrib.auth.models import User

    now = timezone.now()
    reminder_time = time(16, 0)  # 8:00 AM
    if now.time() != reminder_time:
        return "Not reminder time yet"

    try:
        active_habits = Habit.objects.filter(is_active=True)  # Or: .filter(public=True)
    except Exception as e:
        return f"Error querying habits: {e}"

    sent_count = 0
    for habit in active_habits:
        try:
            # Assuming habits link to users (e.g., via ForeignKey to User)
            user = habit.user  # Replace with your actual relation, e.g., habit.owner
            if hasattr(user, 'telegram_chat_id'):  # Or check your User profile model
                message = f"Reminder: Time to do your habit '{habit.name}'! 📅"
                # Send via Telegram (replace with your actual bot code)
                # send_telegram_message(user.telegram_chat_id, message)
                print(f"Sent reminder to user {user.id} for habit '{habit.name}'")  # For testing/logging
                sent_count += 1
        except Exception as e:
            print(f"Error sending reminder for habit {habit.id}: {e}")
            continue  # Skip this habit and move on

    return f"Sent {sent_count} reminders today"
