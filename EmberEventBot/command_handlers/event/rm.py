from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.exceptions import EventIdError
from EmberEventBot.helpers import event_idx
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger(__name__)


@restricted(UserAccessLevel.ADMIN)
async def rm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Removes an event

    Args:
        update
        context
    """
    user = update.message.from_user
    event_id = " ".join(context.args).upper()
    try:
        idx = event_idx(event_id=event_id, events=context.bot_data['events']['active'])
    except EventIdError as _:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Unknown event {event_id}.")
        return
    context.bot_data['events']['active'].pop(idx)
    logger.info("RM of %s: %s", user.name, event_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event_id} removed.")
