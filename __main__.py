from datetime import datetime
from logging import getLogger, StreamHandler, Formatter, WARNING
from logging.handlers import RotatingFileHandler
import pytz
import re
import sys

from telegram import Update
from telegram.constants import ParseMode, MessageEntityType
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    Defaults,
    filters,
    MessageHandler,
    PicklePersistence, 
    Application,
)

# Keep only the essential command handlers
from EmberEventBot.command_handlers.calendar_ import calendar_
from EmberEventBot.command_handlers.event.list import listevents
from EmberEventBot.command_handlers.event.show import show, update_show
from EmberEventBot.command_handlers.help import help_command
from EmberEventBot.settings import EmberEventBotSettings

SETTINGS = EmberEventBotSettings()
logFormater = Formatter(SETTINGS.log_format)
shandler = StreamHandler(sys.stdout)
shandler.setFormatter(logFormater)

# Basic logging setup
logger = getLogger()
logger.setLevel(SETTINGS.log_level)
logger.addHandler(shandler)

QUERY_FOR_REGEX: str = "^tg://query_for/(.*)$"
CMD_REGEX: str = "^tg://cmd/(.*)$"

async def inline_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Simplified callback query handler"""
    query = update.callback_query
    await query.answer()
    
    if cmd == 'show':
        await update_show(update, context)
    return None

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch all response"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def build_application() -> Application:
    persistence = PicklePersistence(filepath="events")
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone(SETTINGS.tz))
    return (ApplicationBuilder()
            .token(SETTINGS.embtoken)
            .persistence(persistence)
            .defaults(defaults)
            .build())

def add_command_handlers(application: Application) -> None:
    # Only keeping essential, non-admin commands
    application.add_handler(CallbackQueryHandler(inline_keyboard_handler))
    application.add_handler(CommandHandler('calendar', calendar_))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('list', listevents))
    application.add_handler(CommandHandler('show', show))
    application.add_handler(CommandHandler("start", show, filters.Regex(r"show_.*")))
    application.add_handler(CommandHandler('start', help_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

def main() -> None:
    application = build_application()
    add_command_handlers(application)
    httpxlogger = getLogger('httpx')
    httpxlogger.setLevel(WARNING)
    application.run_polling()

if __name__ == "__main__":
    main()