from calendar import TextCalendar, MONDAY
from datetime import datetime
from logging import getLogger

from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.validators import restricted, UserAccessLevel

logger = getLogger(__name__)


@restricted(UserAccessLevel.USER)
async def calendar_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Calendar"""
    mm = datetime.now().month
    yy = datetime.now().year
    dd = datetime.now().day
    mp = mm + 1 if mm < 12 else 1
    yp = yy + 1 if mm == 12 else yy
    msg = "<pre>"
    for x in [[yy, mm], [yp, mp]]:
        c = TextCalendar(MONDAY)
        heading, cal = c.formatmonth(*x).split('\n', 1)
        if x[1] == mm:
            cal = cal.replace('{:2d}'.format(dd), ' █', 1)
        for queue in ['active', 'inactive']:
            for i in context.bot_data['events'][queue]:
                if i['date'][:6] == f"{x[0]}{x[1]:02}":
                    v = '{:2d}'.format(int(f"{i['date'][6:]}"))
                    cal = cal.replace(v, '★', 1)
        msg += heading + "\n" + cal + "\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg + "</pre>")
