from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from telegram import Bot
from django.conf import settings
from .models import Habit


@shared_task
def send_habit_reminders():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    now = timezone.now()
    habits = Habit.objects.filter(next_reminder__lte=now,
                                  user__telegram_chat_id__isnull=False)
    for habit in habits:
        chat_id = habit.user.telegram_chat_id
        message = f"Reminder: {habit.action} at {habit.place or 'your place'}."
        try:
            bot.send_message(chat_id=chat_id, text=message)
            habit.next_reminder = now + timedelta(days=habit.periodicity)
            habit.save()
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
