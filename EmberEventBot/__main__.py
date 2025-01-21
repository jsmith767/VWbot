#!/usr/bin/python3
from datetime import datetime
from logging import basicConfig, getLogger, StreamHandler, Formatter, WARNING
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import pytz
import re
import sys
from datetime import datetime
from logging import getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

import pytz
from telegram import Update
from telegram.constants import ParseMode, MessageEntityType
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    Defaults,
    filters,
    MessageHandler,
    PicklePersistence, Application,
)

from EmberEventBot.command_handlers.calendar_ import calendar_
from EmberEventBot.command_handlers.announcement import announcement_conv_handler
from EmberEventBot.command_handlers.event.cancel import cancel
from EmberEventBot.command_handlers.event.create import create_conv_handler
from EmberEventBot.command_handlers.event.deactivate import deactivate, reactivate, update_deactivate, update_reactivate
from EmberEventBot.command_handlers.event.edit import edit_conv_handler
from EmberEventBot.command_handlers.event.list import listevents
from EmberEventBot.command_handlers.event.myevents import myevents
from EmberEventBot.command_handlers.event.rm import rm
from EmberEventBot.command_handlers.event.rsvp import rsvp_conv_handler
from EmberEventBot.command_handlers.event.show import show, update_show
from EmberEventBot.command_handlers.help import help_command
from EmberEventBot.command_handlers.sidechats import sidechats
from EmberEventBot.command_handlers.user.contact import contact, update_contact
from EmberEventBot.scheduled_jobs.alerts import (
    user_event_alert,
    new_event_alert,
    event_alert,
    event_summary_alert,
)
from EmberEventBot.scheduled_jobs.sweep import sweep
from EmberEventBot.settings import EmberEventBotSettings, EmberJobSettings
from EmberEventBot.validators import restricted
from EmberEventBot.constants import UserAccessLevel

SETTINGS = EmberEventBotSettings()
logFormater = Formatter(SETTINGS.log_format)
accessFormater = Formatter(SETTINGS.access_log_format)
shandler = StreamHandler(sys.stdout)
shandler.setFormatter(logFormater)
rhandler = RotatingFileHandler(
    filename=SETTINGS.log_path,
    maxBytes=SETTINGS.log_max_bytes,
    backupCount=SETTINGS.log_backup_count)
rhandler.setFormatter(logFormater)
accesshandler = TimedRotatingFileHandler(
    filename=SETTINGS.access_log_path,
    when=SETTINGS.access_log_when)
accesshandler.setFormatter(accessFormater)

logger = getLogger()

logger.setLevel(SETTINGS.log_level)
logger.addHandler(shandler)
logger.addHandler(rhandler)

access = getLogger("access")
access.setLevel(SETTINGS.access_log_level)
access.addHandler(accesshandler)

QUERY_FOR_REGEX: str = "^tg://query_for/(.*)$"
CMD_REGEX: str = "^tg://cmd/(.*)$"


@restricted(UserAccessLevel.USER)
async def inline_keyboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback Query Handler that handles telegram keyboard responses"""
    query = update.callback_query
    await query.answer()
    for entity in query.message.entities:
        if entity.type == MessageEntityType.TEXT_LINK:
            query_for_search = re.search(QUERY_FOR_REGEX, entity.url)
            if query_for_search:
                query_for = query_for_search.group(1)
                break
    else:
        logger.error("inline_keyboard_handler expects query_for anchor link metadata in the message.")
        query_for = 'unknown'
    context.chat_data[query_for] = query.data

    for entity in query.message.entities:
        if entity.type == MessageEntityType.TEXT_LINK:
            cmd_search = re.search(CMD_REGEX, entity.url)
            if cmd_search:
                cmd = cmd_search.group(1)
                break
    else:
        logger.error("inline_keyboard_handler expects cmd anchor link metadata in the message.")
        return

    if cmd == 'show':
        await update_show(update, context)
    elif cmd == 'deactivate':
        await update_deactivate(update, context)
    elif cmd == 'reactivate':
        await update_reactivate(update, context)
    elif cmd == 'contact':
        await update_contact(update, context)

    return None


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Catch all response"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def build_application() -> Application:
    persistence = PicklePersistence(filepath="events")
    defaults = Defaults(parse_mode=ParseMode.HTML, tzinfo=pytz.timezone(SETTINGS.tz))
    return (ApplicationBuilder()
            .token(SETTINGS.embtoken)
            .persistence(persistence)
            .defaults(defaults)
            .build())


def add_job_queues(application: Application) -> None:
    JOBSET = EmberJobSettings()
    data = dict(spam_delay=SETTINGS.spam_delay)
    application.job_queue.run_daily(sweep, datetime.time(datetime.strptime(JOBSET.sweep_time, "%H:%M")))
    application.job_queue.run_daily(
        user_event_alert,
        datetime.time(datetime.strptime(JOBSET.user_event_alert_time, "%H:%M")),
        data=data,
        name="user_event_alert",
    )
    application.job_queue.run_repeating(
        new_event_alert,
        JOBSET.new_event_alert_interval,
        data={**data, 'targets': JOBSET.new_event_alert_targets},
        name="new_event_alert"
    )
    if JOBSET.event_alert_enabled:
        application.job_queue.run_daily(
            callback=event_alert,
            time=datetime.time(datetime.strptime(JOBSET.event_alert_time, "%H:%M")),
            data={**data, 'targets': JOBSET.event_alert_targets},
            name="event_alert"
        )
    if JOBSET.summary_alert_enabled:
        application.job_queue.run_daily(
            callback=event_summary_alert,
            time=datetime.time(datetime.strptime(JOBSET.summary_alert_time, "%H:%M")),
            days=JOBSET.summary_alert_days,
            data={**data, 'targets': JOBSET.summary_alert_targets},
            name="event_summary_alert"
        )


def add_command_handlers(application: Application) -> None:
    application.add_handler(create_conv_handler())
    application.add_handler(edit_conv_handler())
    application.add_handler(rsvp_conv_handler())
    application.add_handler(announcement_conv_handler())
    application.add_handler(CallbackQueryHandler(inline_keyboard_handler))
    application.add_handler(CommandHandler('calendar', calendar_))
    application.add_handler(CommandHandler('cancel', cancel))
    application.add_handler(CommandHandler('contact', contact))
    application.add_handler(CommandHandler('deactivate', deactivate))
    application.add_handler(CommandHandler('reactivate', reactivate))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('list', listevents))
    application.add_handler(CommandHandler('myevents', myevents))
    application.add_handler(CommandHandler('rm', rm))
    application.add_handler(CommandHandler('show', show))
    application.add_handler(CommandHandler('sidechat', sidechats))
    application.add_handler(CommandHandler("start", show, filters.Regex(r"show_.*")))
    application.add_handler(CommandHandler('start', help_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))


def main() -> None:
    application = build_application()
    add_job_queues(application)
    add_command_handlers(application)
    httpxlogger = getLogger('httpx')
    httpxlogger.setLevel(WARNING)
    apsexelogger = getLogger('apscheduler.executors.default')
    apsexelogger.setLevel(WARNING)
    application.run_polling()


if __name__ == "__main__":
    main()
