from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from EmberEventBot.helpers import bubble
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import valid, restricted, UserAccessLevel

settings = EmberEventBotSettings()


# noinspection PyUnusedLocal
@restricted(UserAccessLevel.USER)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds with help text from settings.hlp"""
    msg = bubble("Help") + settings.hlp
    if valid(
            user_id=update.effective_user.id,
            chat_id=settings.admin_group,
            status=['administrator', 'creator']
    ):
        msg += settings.hlp_admin
    await update.message.reply_text(msg)
