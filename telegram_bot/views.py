import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from asgiref.sync import sync_to_async  # <-- Add this import

# Initialize bot and application globally
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TELEGRAM_BOT_TOKEN)
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Define async handlers (e.g., for /start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id_str = context.args[0] if context.args else None
    if not user_id_str:
        await update.message.reply_text("Please use /start <user_id> to link your account.")
        return
    try:
        user_id = int(user_id_str)
        chat_id = update.effective_chat.id
        from habits.models import TelegramChat, User  # <-- Add User to import
        # Fetch the user first (will raise DoesNotExist if invalid)
        user = await sync_to_async(User.objects.get)(id=user_id)
        # Now get_or_create with the user object
        telegram_chat, created = await sync_to_async(TelegramChat.objects.get_or_create)(user=user, chat_id=chat_id)
        await update.message.reply_text("✅ Your Telegram chat is linked to Habit Tracker! You'll get reminders here. 💪")
    except User.DoesNotExist:  # <-- Handle missing user
        await update.message.reply_text("User not found. Please register on the website first and get your user ID.")
    except ValueError:
        await update.message.reply_text("Invalid user ID. Please provide a number.")

# Add handlers to application (do this once, outside views)
application.add_handler(CommandHandler("start", start))

@csrf_exempt
@require_http_methods(["POST"])
async def telegram_webhook(request):
    try:
        await bot.initialize()  # Initialize the global bot
        update_data = json.loads(request.body)
        update = Update.de_json(update_data, bot)
        await application.initialize()  # Initialize the application
        await application.process_update(update)
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as e:
        print(f"Webhook error: {e}")
        return JsonResponse({"error": str(e)}, status=400)
