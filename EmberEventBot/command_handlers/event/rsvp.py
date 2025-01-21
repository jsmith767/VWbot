from logging import getLogger

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from EmberEventBot.exceptions import EventIdError
from EmberEventBot.helpers import event_idx, event_id_exists
from EmberEventBot.keyboards import event_kbd, rsvp_kbd, plus_one_kbd
from EmberEventBot.models.event import EventModel
from EmberEventBot.models.user import UserModel
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger(__name__)

SETTINGS = EmberEventBotSettings()

# Stages
CALLBACK_PREFIX = "rsvp"
SLICE = len(CALLBACK_PREFIX) + 1
# Callback data
EVENT, STATUS, PLUS = [CALLBACK_PREFIX + str(x) for x in range(3)]


def rsvp_conv_handler() -> ConversationHandler:
    """Builds a conversation handler for rsvp"""
    return ConversationHandler(
        entry_points=[CommandHandler("rsvp", rsvp)],
        states={
            EVENT: [CallbackQueryHandler(event, pattern=f"^{EVENT}.*")],
            STATUS: [CallbackQueryHandler(status, pattern=f"^{STATUS}.*")],
            PLUS: [CallbackQueryHandler(plusone, pattern=f"^{PLUS}.*")],
        },
        fallbacks=[CommandHandler("rsvp", rsvp)],
    )


@restricted(UserAccessLevel.USER)
async def rsvp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts rsvp action"""
    query = update.callback_query
    context.chat_data.clear()
    query_for = '<a href="tg://query_for/rsvp">\u200b</a>'
    if 'events' not in context.bot_data.keys():
        context.bot_data.update({'events': {'active': [], 'inactive': []}})
    kbd_markup = await event_kbd(context, callback_prefix=EVENT)
    msg = query_for + "Please select the event you want to rsvp to."
    if query is None:
        await update.message.reply_text(msg, reply_markup=kbd_markup)
    else:
        await query.edit_message_text(msg, reply_markup=kbd_markup)
    return EVENT


@restricted(UserAccessLevel.USER)
async def event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Catches the Event_ID and asks for Status"""
    query = update.callback_query
    await query.answer()
    event_id = query.data[SLICE:]
    if not event_id_exists(event_id=event_id, events=context.bot_data['events']['active']):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event {event_id}.")
        return EVENT
    context.chat_data['event_id'] = event_id
    kbd_markup = await rsvp_kbd(callback_prefix=STATUS)
    await query.edit_message_text(
        "Please select your desired event status.",
        reply_markup=kbd_markup
    )
    return STATUS


@restricted(UserAccessLevel.USER)
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Catches the Status and asks for Value"""
    query = update.callback_query
    user = update.effective_user
    event_id = context.chat_data['event_id']
    await query.answer()
    rsvp_status = query.data[SLICE:]
    try:  # Verify event_id
        idx = event_idx(event_id, context.bot_data['events']['active'])
    except EventIdError as e:
        logger.error(str(e))
        return EVENT
    event_model = EventModel(**context.bot_data['events']['active'][idx])
    if rsvp_status == "plusone":
        current_status = event_model.user_status(UserModel(id=user.id, name=user.full_name))
        if current_status is None:
            await query.edit_message_text(
                f"You need to rsvp before you can add a +1.",
                reply_markup=await rsvp_kbd(callback_prefix=STATUS)
            )
            return STATUS
        context.chat_data['status'] = rsvp_status
        kbd_markup = await plus_one_kbd(callback_prefix=PLUS)
        await query.edit_message_text(
            "How many total +1s, 0 for none.",
            reply_markup=kbd_markup
        )
        return PLUS
    msg = event_model.update_rsvp(
        user=UserModel(id=user.id, name=user.full_name),
        rsvp_status=rsvp_status
    )
    event_model.commit_event(context)
    await query.edit_message_text(
        msg,
        reply_markup=None
    )
    return ConversationHandler.END


@restricted(UserAccessLevel.USER)
async def plusone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Catches the Value and saves"""
    query = update.callback_query
    user = update.effective_user
    event_id = context.chat_data['event_id']
    await query.answer()
    plus = int(query.data[SLICE:])
    try:  # Verify event_id
        idx = event_idx(event_id, context.bot_data['events']['active'])
    except EventIdError as e:
        logger.error(str(e))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event: {event_id}.")
        return EVENT
    event_model = EventModel(**context.bot_data['events']['active'][idx])
    if plus > 0 and not event_model.has_room(plus):
        await query.edit_message_text(
            f"Event {event_id} doesn't have room for {plus} more.",
            reply_markup=None
        )
        return ConversationHandler.END
    current_status = event_model.user_status(UserModel(id=user.id, name=user.full_name))
    if current_status is None:
        await query.edit_message_text(
            f"You need to rsvp before you can add a +1.",
            reply_markup=await rsvp_kbd(callback_prefix=STATUS)
        )
        return STATUS
    for u in context.bot_data['events']['active'][idx][current_status]:
        if u['id'] == str(user.id):
            u['plus'] = plus
    await query.edit_message_text(
        f"You are marked as {current_status} for {event_id} and {str(plus)} plus ones.",
        reply_markup=None
    )
    return ConversationHandler.END
