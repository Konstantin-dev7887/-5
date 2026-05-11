import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import telebot
from users.models import User

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Обработчик вебхука от Telegram."""
    try:
        json_str = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])

        # Обработка команды /start
        if update.message and update.message.text == '/start':
            chat_id = update.message.chat.id
            username = update.message.from_user.username

            try:
                user = User.objects.get(username=username)
                user.telegram_chat_id = chat_id
                user.save()
                bot.send_message(
                    chat_id,
                    f"Привет, {username}! Твой Chat ID сохранён. Я буду присылать тебе напоминания о привычках.")
                logger.info(
                    f"Chat ID {chat_id} сохранён для пользователя {username}")
            except User.DoesNotExist:
                bot.send_message(
                    chat_id,
                    "Привет! Я бот трекера привычек. Похоже, у тебя ещё нет аккаунта. Зарегистрируйся, пожалуйста, и укажи свой username.")
                logger.warning(
                    f"Пользователь с username {username} не найден.")

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Ошибка обработки вебхука: {e}")
        return JsonResponse({'status': 'error'}, status=500)
