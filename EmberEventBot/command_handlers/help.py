from telegram import Update
from telegram.ext import ContextTypes
from EmberEventBot.helpers import bubble
from EmberEventBot.settings import EmberEventBotSettings

settings = EmberEventBotSettings()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds with help text from settings.hlp"""
    msg = bubble("Help") + settings.hlp
    # Adding admin help text for everyone since we're removing validation
    msg += settings.hlp_admin
    await update.message.reply_text(msg)
