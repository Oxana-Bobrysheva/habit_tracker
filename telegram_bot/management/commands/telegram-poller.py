import os
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import Application, CommandHandler
from telegram_bot.views import start  # Import your async start handler from views.py


class Command(BaseCommand):
    help = 'Run Telegram bot in polling mode'

    def handle(self, *args, **options):
        # Get token from settings or env
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', os.getenv('TELEGRAM_BOT_TOKEN'))
        if not token:
            self.stdout.write(self.style.ERROR("TELEGRAM_BOT_TOKEN not set in settings or env."))
            return

        # Build application and add handlers (reusing your setup)
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler("start", start))  # Add your /start handler

        self.stdout.write("Starting Telegram poller... Press Ctrl+C to stop.")
        try:
            # Run polling (blocking call; handles getUpdates internally)
            application.run_polling()
        except KeyboardInterrupt:
            self.stdout.write("Poller stopped.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Polling error: {e}"))
