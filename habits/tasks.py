import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings
import telebot
from .models import Habit

logger = logging.getLogger(__name__)

@shared_task
def send_habit_reminders():
    """Периодическая задача для отправки напоминаний о привычках."""
    bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute,
    ).exclude(user__telegram_chat_id__isnull=True)

    for habit in habits:
        message = f"🔔 Напоминание о привычке:\n📍 {habit.place}\n🕒 {habit.time}\n⚡ {habit.action}"
        if habit.reward:
            message += f"\n🎁 Вознаграждение: {habit.reward}"
        try:
            bot.send_message(habit.user.telegram_chat_id, message)
            habit.last_reminded = now
            habit.save(update_fields=['last_reminded'])
            logger.info(f"Напоминание отправлено пользователю {habit.user.username}")
        except Exception as e:
            logger.error(f"Ошибка отправки для {habit.user.username}: {e}")
