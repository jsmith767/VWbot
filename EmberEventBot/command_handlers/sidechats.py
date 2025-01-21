#!/usr/bin/python3

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.helpers import bubble
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import UserAccessLevel, restricted

settings = EmberEventBotSettings()


@restricted(UserAccessLevel.USER)
async def sidechats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds with a list of side chats"""
    msg = bubble("Sidechats") + settings.sidechat
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode='HTML')
