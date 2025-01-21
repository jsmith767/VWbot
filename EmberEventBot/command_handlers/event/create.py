from datetime import datetime, date
from logging import getLogger

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

from EmberEventBot.helpers import event_id_exists, munge_date
from EmberEventBot.models.event import EventModel
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import restricted, UserAccessLevel

settings = EmberEventBotSettings()

yr = date.today().year

years = [str(x) for x in [yr, yr + 1, yr % 100, (yr + 1) % 100]]

date_regex = f"^(0[1-9]|1[012])[ -/.](0[1-9]|[12][0-9]|3[01])[- /.]({'|'.join(years)})$"

logger = getLogger(__name__)

EVENT, DATE, SUMMARY, MAXHEAD, DESCRIPTION = range(5)


def create_conv_handler() -> ConversationHandler:
    """Builds a conversation handler for create event"""

    return ConversationHandler(
        entry_points=[CommandHandler("create", create)],
        states={
            EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, event)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, summary)],
            MAXHEAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, maxhead)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


@restricted(UserAccessLevel.ADMIN)
async def create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'event' not in context.chat_data.keys():
        context.chat_data['event'] = {}
    if 'events' not in context.bot_data.keys():
        context.bot_data.update({
            'events': {
                'active': [],
                'inactive': []
            }
        })
    await update.message.reply_text(
        "Hi! Let's build an event. Send /cancel to abandon event.\n\n"
        "What would you like the event name to be? "
        "Keep it short and unique, people have to type it in commands.",
    )
    return EVENT


@restricted(UserAccessLevel.ADMIN)
async def event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    event_id = update.message.text.upper()
    logger.info("EventID of %s: %s", user.name, event_id)
    if event_id_exists(event_id, context.bot_data['events']['active']):
        await update.message.reply_text(f"{event_id} is already an active event. Try another name.")
        return EVENT
    context.chat_data['event']['id'] = event_id
    await update.message.reply_text(
        "When is this event? (mm/dd/yy)"
    )
    return DATE


@restricted(UserAccessLevel.ADMIN)
async def date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("Date of %s: %s", user.name, text)
    date_val = munge_date(text)
    if date_val is not None:
        text = date_val.strftime(settings.date_ymd)
    else:
        # Try again
        await update.message.reply_text("Invalid date format. Try mm/dd/yy")
        return DATE
    context.chat_data['event']['date'] = text
    await update.message.reply_text(
        "Now we need a summary. Keep it to a sentence, Hemingway.",
    )
    return SUMMARY


@restricted(UserAccessLevel.ADMIN)
async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    text = update.message.text
    logger.info("Summary of %s: %s", user.name, text)
    context.chat_data['event']['summary'] = text
    await update.message.reply_text(
        "How many people is the hard limit for this event? (0 for unlimited)"
    )
    return MAXHEAD


@restricted(UserAccessLevel.ADMIN)
async def maxhead(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Maxhead of %s: %s", user.name, update.message.text)
    context.chat_data['event']['maxhead'] = int(update.message.text)
    await update.message.reply_text(
        "Okay, nows your chance to go ham on this event description"
        " or ya know, put 'TBD' or some shit, what do I care.",
    )
    return DESCRIPTION


@restricted(UserAccessLevel.ADMIN)
async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.chat_data['event']['description'] = update.message.text
    event_model = EventModel(**context.chat_data['event'])
    event_model.commit(context)
    d = datetime.strptime(context.chat_data['event']['date'], settings.date_ymd).strftime(settings.date_long)
    await update.message.reply_text(
        "Sounds like a rager, maybe you could invite me.\n"
        "Or <i>whatever</i>... Here's what we created:\n"
        f"name: {context.chat_data['event']['id']}\n"
        f"date: {d}\n"
        f"summary: {context.chat_data['event']['summary']}\n"
        f"head count: {context.chat_data['event']['maxhead']}\n"
        f"description: {context.chat_data['event']['description']}\n"
    )
    try:
        context.bot_data['events']['active'].sort(key=lambda x: x["date"])
    except Exception as e:
        logger.error(str(e))

    msg = event_model.get_desc()
    try:
        context.bot_data['alerts']['newevent'].append(msg)
    except KeyError as _:
        if context.bot_data.get('alerts', False):
            context.bot_data['alerts']['newevent'] = [msg]
        else:
            context.bot_data['alerts'] = {'newevent': [msg]}
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.name} canceled the conversation.")
    context.chat_data.pop('event', None)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.",
    )
    return ConversationHandler.END
