from datetime import datetime, timedelta
from logging import getLogger
from time import sleep
from typing import List
from telegram.ext import ContextTypes

from EmberEventBot.models.event import EventModel, EventList
from EmberEventBot.helpers import bubble

logger = getLogger(__name__)

def job_data_get(data,key,default):
    try:
        return data[key]
    except:
        logger.debug(f'No {key} in data')
    return default

async def user_event_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends reminders to users who have opted in about events"""
    job = context.job
    spam_delay = job_data_get(job.data,'spam_delay',3)
    reminders = {
        "remind3d": datetime.today() + timedelta(days=3),
        "remind1d": datetime.today() + timedelta(days=1),
    }
    for event in context.bot_data['events']['active']:
        event_model = EventModel(**event)
        e = event_model.get_date()
        for k, v in reminders.items():
            if e.year == v.year and e.month == v.month and e.day == v.day:
                for u in event_model.going:
                    try:
                        if context.bot_data['user_data'][u.id]['contact'][k]:
                            msg = (f"Reminder: {event_model.id} is in " +
                                   f"{abs((datetime.today() - event_model.get_date()).days)} " +
                                   "day(s) and you are listed as going. " +
                                   "If that has changed please update your RSVP status.")
                            await context.bot.send_message(chat_id=int(u.id), text=msg)
                            sleep(spam_delay)  # Try not to be marked as bot spam
                    except KeyError as _:
                        pass
                    except Exception as e:
                        logger.error(str(e))

async def new_event_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends newevents to users who have opted in about events"""
    if len(context.bot_data['alerts'].get('newevent', [])) == 0:
        return
    job = context.job
    spam_delay = job_data_get(job.data,'spam_delay',3)
    msg = bubble("New events") + '\n'
    while context.bot_data['alerts']['newevent']:
        msg += context.bot_data['alerts']['newevent'].pop() + "\n\n"

    new_event_users = [v for v in context.bot_data['user_data'].values() if v['contact'].get('newevent', False)]
    for u in new_event_users:
        try:
            await context.bot.send_message(chat_id=u.get('id'), text=msg)
        except Exception as e:
            logger.error(f"Failed to send message to {str(u)}")
            logger.error(str(e))
        sleep(spam_delay)  # Try not to be marked as bot spam
    targets = job.data.get("targets",[])
    for chat_id in targets:
        logger.info(f"Trying chat {chat_id}")
        try:
            await context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logger.error(str(e))
        sleep(spam_delay)  # Try not to be marked as bot spam


async def event_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends event advert to info and main chat"""
    reminders = {
        "7DAY": datetime.today() + timedelta(days=7),
        "3DAY": datetime.today() + timedelta(days=3),
        "TODAY": datetime.today(),
    }
    job = context.job
    spam_delay: int = job.data.get('spam_delay',3)
    targets: List[str] = job.data.get('targets',[])
    for event in context.bot_data['events']['active']:
        event_model = EventModel(**event)
        e = event_model.get_date()
        for k, v in reminders.items():
            if e.year == v.year and e.month == v.month and e.day == v.day:
                msg = bubble(f"{k} EVENT REMINDER")
                msg += str(event_model)
                for chat_id in targets:
                    try:
                        await context.bot.send_message(chat_id=int(chat_id), text=msg)
                    except KeyError as _:
                        pass
                    except Exception as e:
                        logger.error(str(e))
                    sleep(spam_delay)  # Try not to be marked as bot spam

async def event_summary_alert(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends event advert to info and main chat"""
    job = context.job
    spam_delay: int = job.data.get('spam_delay',3)
    targets: List[str] = job.data.get('targets',[])
    msg = bubble("Current Events")
    msg += str(EventList.parse_obj(context.bot_data['events']['active']))
    for chat_id in targets:
        try:
            await context.bot.send_message(chat_id=int(chat_id), text=msg)
        except Exception as e:
            logger.error(str(e))
        sleep(spam_delay)