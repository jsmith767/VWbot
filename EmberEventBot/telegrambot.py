from datetime import datetime
from logging import basicConfig, getLogger, StreamHandler, Formatter, WARNING
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import pytz
import re
import sys
from datetime import datetime
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
    PicklePersistence, Application,
)

# from EmberEventBot.command_handlers.calendar_ import calendar_
# from EmberEventBot.command_handlers.announcement import announcement_conv_handler
# from EmberEventBot.command_handlers.event.cancel import cancel
# from EmberEventBot.command_handlers.event.create import create_conv_handler
# from EmberEventBot.command_handlers.event.deactivate import deactivate, reactivate, update_deactivate, update_reactivate
# from EmberEventBot.command_handlers.event.edit import edit_conv_handler
# from EmberEventBot.command_handlers.event.list import listevents
# from EmberEventBot.command_handlers.event.myevents import myevents
# from EmberEventBot.command_handlers.event.rm import rm
# from EmberEventBot.command_handlers.event.rsvp import rsvp_conv_handler
# from EmberEventBot.command_handlers.event.show import show, update_show
# from EmberEventBot.command_handlers.help import help_command
# from EmberEventBot.command_handlers.sidechats import sidechats
# from EmberEventBot.command_handlers.user.contact import contact, update_contact
# from EmberEventBot.scheduled_jobs.alerts import (
#     user_event_alert,
#     new_event_alert,
#     event_alert,
#     event_summary_alert,
# )
# from EmberEventBot.scheduled_jobs.sweep import sweep
# from EmberEventBot.settings import EmberEventBotSettings, EmberJobSettings
# from EmberEventBot.validators import restricted
# from EmberEventBot.constants import UserAccessLevel

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am your bot. How can I assist you today? Type /help to see what I can do!")

# Command: /help
# async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     help_text = (
#         "Here are the commands you can use:\n"
#         "/start - Start the bot and see a welcome message\n"
#         "/help - Get a list of available commands\n"
#         "/about - Learn more about this bot\n"
#     )
#     await update.message.reply_text(help_text)

# Command: /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "I am a simple Telegram bot created using Python. "
        "I can reply to your messages and provide helpful commands. "
        "Feel free to try out the features!"
    )
    await update.message.reply_text(about_text)

# Function to handle regular text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text(f'You said: "{user_message}"')

# Main function to run the bot
def main():
    # Replace 'YOUR_API_TOKEN' with your actual BotFather API token
    # print(API_TOKEN)
    api_token = API_TOKEN

    # Create the application instance
    app = ApplicationBuilder().token(api_token).build()

    # Add handlers for commands
    app.add_handler(CommandHandler("start", start))  # /start command
    app.add_handler(CommandHandler("help", help))    # /help command
    app.add_handler(CommandHandler("about", about))  # /about command

    # Add a handler for regular text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
