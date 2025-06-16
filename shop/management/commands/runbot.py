from django.core.management.base import BaseCommand
from bot.bot import start_bot  # Adjust the import if needed

class Command(BaseCommand):
    help = "Run the Telegram bot (aiogram) using Django context"

    def handle(self, *args, **options):
        start_bot()