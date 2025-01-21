from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.keyboards import event_kbd
from EmberEventBot.models.event import EventModel, EventList, UserModel
from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger()
settings = EmberEventBotSettings()


@restricted(UserAccessLevel.USER)
async def show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Responds with details of an event"""
    context.chat_data.clear()
    args = update.message.text.split(" ")
    # Gets the slash command, without the slash or following params.
    cmd = args.pop(0)[1:]
    if len(context.args):
        if cmd == 'start':
            context.chat_data['event_id'] = args[0][5:]
        else:
            context.chat_data['event_id'] = " ".join(context.args).upper()
        await update_show(update, context)
    else:
        kbd_markup = await event_kbd(context)
        query_for = '<a href="tg://query_for/event_id">\u200b</a>'
        cmd = '<a href="tg://cmd/show">\u200b</a>'
        await update.message.reply_text(query_for + cmd + "Please choose an event:", reply_markup=kbd_markup)


@restricted(UserAccessLevel.USER)
async def update_show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Finishes show after user input"""
    user = UserModel(id=update.effective_user.id, name=update.effective_user.full_name)
    event_id = context.chat_data['event_id']
    idx = EventList.parse_obj(context.bot_data['events']['active']).index(event_id=event_id)
    if idx is not None:
        msg = f"{settings.hr}\n"
        e = EventModel(**context.bot_data['events']['active'][idx])
        msg += str(e)
        if e.user_status(user) == 'going' and e.chat is not None:
            msg += f"Event Side Chat: {e.chat}\n"
        msg += f"{settings.hr}"
    elif event_id == 'cancel':
        return
    else:
        msg = f"{event_id} doesn't appear to be an active event."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
