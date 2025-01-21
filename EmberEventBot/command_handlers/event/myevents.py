from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.models.event import EventList
from EmberEventBot.models.user import UserModel
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger()


@restricted(UserAccessLevel.USER)
async def myevents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the show my events command"""
    resp = EventList(__root__=context.bot_data['events']['active']).get_user_status(
        user=UserModel(id=update.effective_user.id, name=update.effective_user.full_name))
    msg = "These are the active events that you've rsvpd for.\n"
    msg += '\n'.join([f"{k}: {', '.join(v)}" for k, v in resp.items() if k is not None])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg)
