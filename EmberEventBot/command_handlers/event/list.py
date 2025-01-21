from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.helpers import bubble
from EmberEventBot.models.event import EventList
from EmberEventBot.validators import UserAccessLevel, restricted

logger = getLogger(__name__)


@restricted(UserAccessLevel.USER)
async def listevents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds with a list of active events"""
    msg = bubble("Current Events")
    msg += str(EventList.parse_obj(context.bot_data['events']['active']))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
