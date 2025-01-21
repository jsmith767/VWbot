from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.keyboards import contact_kbd
from EmberEventBot.models.user import UserData, ContactEntry
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger(__name__)


@restricted(UserAccessLevel.USER)
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_name = str(update.message.from_user.name)
    full_name = str(update.message.from_user.full_name)

    context.chat_data.clear()
    args = update.message.text.split(" ")

    if 'user_data' not in context.bot_data.keys():
        context.bot_data['user_data'] = {}
    if user_id not in context.bot_data['user_data'].keys():
        ud = UserData(
            id=user_id,
            user_name=user_name,
            full_name=full_name)
        context.bot_data['user_data'][user_id] = ud.dict()
    query_for = '<a href="tg://query_for/contact_field">\u200b</a>'
    # Gets the slash command, without the slash or following params.
    cmd = f'<a href="tg://cmd/{args.pop(0)[1:]}">\u200b</a>'
    kbd_markup = await contact_kbd()
    await update.message.reply_text(
        query_for + cmd + "Update which contact setting?",
        reply_markup=kbd_markup
    )


@restricted(UserAccessLevel.USER)
async def update_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    cf = context.chat_data['contact_field']
    value = not context.bot_data['user_data'][user_id]['contact'].get(cf, False)
    context.bot_data['user_data'][user_id]['contact'][cf] = value
    msg = f'Your contact settings are now:\n{ContactEntry(**context.bot_data["user_data"][user_id]["contact"])}'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
