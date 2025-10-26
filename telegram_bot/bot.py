from telegram import Bot
from django.conf import settings


bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)


def send_telegram_message(chat_id, message):
    """
    Sends a message to a Telegram chat via the bot.
    :param chat_id: The user's Telegram chat ID (stored in User model, e.g., telegram_chat_id field).
    :param message: The text to send.
    """
    try:
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False
