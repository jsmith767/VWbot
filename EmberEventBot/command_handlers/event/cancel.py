from logging import getLogger
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


logger = getLogger(__name__)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.name} canceled the conversation.")
    context.chat_data.clear()
    await update.message.reply_text("Canceled.")
    return ConversationHandler.END
