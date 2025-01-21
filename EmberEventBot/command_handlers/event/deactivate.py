from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.exceptions import EventIdError
from EmberEventBot.helpers import event_idx
from EmberEventBot.keyboards import event_kbd, inactive_event_kbd
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger(__name__)


@restricted(UserAccessLevel.ADMIN)
async def deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Moves an event to the inactive que"""
    context.chat_data.pop('event_id', None)
    if len(context.args):
        context.chat_data['event_id'] = " ".join(context.args).upper()
        await update_deactivate(update, context)
    else:
        query_for = '<a href="tg://query_for/event_id">\u200b</a>'
        cmd = '<a href="tg://cmd/deactivate">\u200b</a>'
        kbd_markup = await event_kbd(context)
        await update.message.reply_text(query_for + cmd + "Deactivate which event?", reply_markup=kbd_markup)


@restricted(UserAccessLevel.ADMIN)
async def update_deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finishes deactivate after user input"""
    user = update.callback_query.from_user
    event_id = context.chat_data['event_id']
    try:
        idx = event_idx(event_id=event_id, events=context.bot_data['events']['active'])
    except EventIdError as _:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event {event_id}.")
        return
    context.bot_data['events']['inactive'].append(context.bot_data['events']['active'].pop(idx))
    logger.info(f"User {user.name} deactivated {event_id}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event_id} moved to inactive.")


@restricted(UserAccessLevel.ADMIN)
async def reactivate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Moves an event to the inactive que"""
    context.chat_data.pop('event_id', None)
    if len(context.args):
        context.chat_data['event_id'] = " ".join(context.args).upper()
        await update_reactivate(update, context)
    else:
        query_for = '<a href="tg://query_for/event_id">\u200b</a>'
        cmd = '<a href="tg://cmd/reactivate">\u200b</a>'
        kbd_markup = await inactive_event_kbd(context)
        await update.message.reply_text(query_for + cmd + "Reactivate which event?", reply_markup=kbd_markup)


@restricted(UserAccessLevel.ADMIN)
async def update_reactivate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finishes reactivate after user input"""
    user = update.callback_query.from_user
    event_id = context.chat_data['event_id']
    try:
        idx = event_idx(event_id=event_id, events=context.bot_data['events']['inactive'])
    except EventIdError as _:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event {event_id}.")
        return
    context.bot_data['events']['active'].append(context.bot_data['events']['inactive'].pop(idx))
    logger.info(f"User {user.name} reactivated {event_id}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event_id} moved to active.")
