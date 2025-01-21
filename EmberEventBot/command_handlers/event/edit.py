from logging import getLogger

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)

from EmberEventBot.exceptions import EventIdError
from EmberEventBot.helpers import event_idx, event_id_exists, munge_date
from EmberEventBot.keyboards import event_kbd, field_kbd
from EmberEventBot.models.event import EventModel
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger(__name__)

SETTINGS = EmberEventBotSettings()

# Stages
START_ROUTES, END_ROUTES = range(2)
CALLBACK_PREFIX = "event"
# Callback data
EVENT, FIELD, VALUE, AGAIN = [CALLBACK_PREFIX + str(x) for x in range(4)]


def edit_conv_handler() -> ConversationHandler:
    """Builds a conversation handler for create event"""

    return ConversationHandler(
        entry_points=[CommandHandler("edit", edit)],
        states={
            EVENT: [CallbackQueryHandler(event, pattern=f"^{EVENT}.*")],
            FIELD: [CallbackQueryHandler(field, pattern=f"^{FIELD}.*")],
            VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, value)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


@restricted(UserAccessLevel.ADMIN)
async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts edit action"""
    query = update.callback_query
    context.chat_data.clear()
    if 'events' not in context.bot_data.keys():
        context.bot_data.update({'events': {'active': [], 'inactive': []}})
    kbd_markup = await event_kbd(context, callback_prefix=EVENT)
    if query is None:
        await update.message.reply_text(
            "Please select the event you want to edit.",
            reply_markup=kbd_markup
        )
    else:
        await query.edit_message_text(
            "Please select the event you want to edit.",
            reply_markup=kbd_markup
        )
    return EVENT


@restricted(UserAccessLevel.ADMIN)
async def event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Catches the Event_ID and asks for Field"""
    query = update.callback_query
    await query.answer()
    event_id = query.data[6:]
    if not event_id_exists(event_id=event_id, events=context.bot_data['events']['active']):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event {event_id}.")
        return EVENT
    context.chat_data['event_id'] = event_id
    kbd_markup = await field_kbd(callback_prefix=FIELD)
    await query.edit_message_text(
        "Please select the field you want to edit.",
        reply_markup=kbd_markup
    )

    return FIELD


@restricted(UserAccessLevel.ADMIN)
async def field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Catches the Field and asks for Value"""
    query = update.callback_query
    event_id = context.chat_data['event_id']
    await query.answer()
    data_field = query.data[6:]
    if data_field not in SETTINGS.editable_fields.keys():  # Verify field
        return EVENT
    context.chat_data['field'] = data_field

    try:  # Verify event_id
        idx = event_idx(event_id, context.bot_data['events']['active'])
    except EventIdError as e:
        logger.error(str(e))
        return EVENT

    msg = f"What value would you like?"
    current: str = context.bot_data['events']['active'][idx].get(data_field, None)
    if current is not None:
        msg += f" Current {data_field} is:\n<code>{current}</code>"
    await query.edit_message_text(msg)
    return VALUE


@restricted(UserAccessLevel.ADMIN)
async def value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Catches the Value and saves"""
    event_id = context.chat_data['event_id']
    data_field = context.chat_data['field']
    text = update.message.text
    # Validate input
    if data_field == 'date':
        date_val = munge_date(text)
        if date_val is not None:
            text = date_val.strftime(SETTINGS.date_ymd)
        else:
            # Try again
            await update.message.reply_text("Invalid date format. Try mm/dd/yy")
            return VALUE

    try:  # Verify event_id
        idx = event_idx(event_id, context.bot_data['events']['active'])
    except EventIdError as e:
        logger.error(str(e))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event: {event_id}.")
        return EVENT
    event_model = EventModel(**context.bot_data['events']['active'][idx])
    setattr(event_model, data_field, text)
    event_model.commit(context)

    await update.message.reply_text(f"{data_field} set to: {text}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.name} canceled the conversation.")
    context.chat_data.clear()
    await update.message.reply_text("Edit canceled.")
    return ConversationHandler.END
