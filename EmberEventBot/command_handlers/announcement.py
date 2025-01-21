#!/usr/bin/python3

from logging import getLogger
from telegram import Update
from telegram.ext import ContextTypes
from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)
from EmberEventBot.helpers import bubble
from EmberEventBot.constants import ConfirmKBD, ChatGroups
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import UserAccessLevel, restricted
from EmberEventBot.keyboards import chat_groups_kbd, confirm_kbd

logger = getLogger(__name__)

SETTINGS = EmberEventBotSettings()

# Stages
START_ROUTES, END_ROUTES = range(2)
CALLBACK_PREFIX = "announcement"
SLICE = len(CALLBACK_PREFIX) + 1

# Callback data
HEADLINE, BODY, CHAT, CONFIRM = [CALLBACK_PREFIX + str(x) for x in range(4)]

def render_msg(chat_data) -> str:
    return bubble(chat_data.get('headline')) + '\n' + chat_data.get('body')

def announcement_conv_handler() -> ConversationHandler:
    """Builds a conversation handler for create event"""
    return ConversationHandler(
        entry_points=[CommandHandler("announcement", start)],
        states={
            HEADLINE: [MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=headline
            )],
            BODY: [MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=body
            )],
            CHAT: [CallbackQueryHandler(chat, pattern=f"^{CHAT}.*")],
            CONFIRM: [CallbackQueryHandler(confirm, pattern=f"^{CONFIRM}.*")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

@restricted(UserAccessLevel.ADMIN)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts announcement action and asks for headline"""
    context.chat_data.clear()
    await update.message.reply_text(
        "What would you like the headline of this announcement to be?",
    )
    return HEADLINE

@restricted(UserAccessLevel.ADMIN)
async def headline(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Catches the headline and asks for the body"""
    context.chat_data['headline'] = update.message.text
    await update.message.reply_text(
        "What is the body of this announcement?",
    )
    return BODY

@restricted(UserAccessLevel.ADMIN)
async def body(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Catches the body and asks for the chat group"""
    context.chat_data['body'] = update.message.text
    kbd_markup = await chat_groups_kbd(callback_prefix=CHAT)
    await update.message.reply_text(
        '<a href="tg://query_for/chat">\u200b</a>' +
        "Which group would you like to send this announcement to?",
        reply_markup=kbd_markup
    )
    return CHAT

@restricted(UserAccessLevel.ADMIN)
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Catches the chat group and asks for confirm"""
    query = update.callback_query
    context.chat_data['chat'] = query.data[SLICE:]
    kbd_markup = await confirm_kbd(callback_prefix=CONFIRM)
    await query.edit_message_text(
        '<a href="tg://query_for/confirm">\u200b</a>' +
        "Okay, please look over the below announcement and confirm that this is what you want.\n" +
        "Chat group: " + context.chat_data['chat'] + '\n' +
        render_msg(context.chat_data),
        reply_markup=kbd_markup
    )
    return CONFIRM

@restricted(UserAccessLevel.ADMIN)
async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Catches confirm and sends or re-starts"""
    query = update.callback_query
    resp = query.data[SLICE:]
    if ConfirmKBD[resp] == ConfirmKBD.CONFIRM:
        chat_id = ChatGroups[context.chat_data.get('chat')].value
        await context.bot.send_message(
            chat_id=int(chat_id),
            text=render_msg(context.chat_data)
        )
        return ConversationHandler.END
    await query.edit_message_text(
        "What would you like the headline of this announcement to be? \n(" +
        context.chat_data['headline'] + ")"
    )
    return HEADLINE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.name} canceled the conversation.")
    context.chat_data.clear()
    await update.message.reply_text("announcement canceled.")
    return ConversationHandler.END