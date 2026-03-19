from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from django.conf import settings
from habit_tracker.models import CustomUser


async def start(update, context):

    await update.message.reply_text(
        "Welcome! To connect this, use /connect <your_email>"
    )

async def connect(update, context):
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "Usage: /connect your_email@example.com")
        return
    email = context.args[0]
    try:
        user = CustomUser.objects.get(email=email)
        user.telegram_chat_id = update.effective_chat.id
        user.save()
        await update.message.reply_text("Connected!")
    except CustomUser.DoesNotExist:
        await update.message.reply_text("No user with that email found.")


async def echo(update, context):
    await update.message.reply_text(update.message.text)


class Command(BaseCommand):
    help = 'Starts the Telegram bot in polling mode'

    def handle(self, *args, **options):
        application = Application.builder().token(
            settings.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('connect', connect))
        application.add_handler(MessageHandler(filters.TEXT &
                                               ~filters.COMMAND, echo))
        self.stdout.write(self.style.SUCCESS('Bot started polling'))
        application.run_polling()
