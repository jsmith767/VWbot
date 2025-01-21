from datetime import datetime, timedelta
from logging import getLogger

from telegram.ext import ContextTypes

from EmberEventBot.settings import EmberEventBotSettings

settings = EmberEventBotSettings()
logger = getLogger(__name__)


async def sweep(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Moves all old events to the inactive que
    """
    sweep_date = datetime.today() - timedelta(days=2)
    for idx, event in enumerate(context.bot_data['events']['active']):
        if datetime.strptime(event['date'], settings.date_ymd) < sweep_date:
            context.bot_data['events']['inactive'].append(context.bot_data['events']['active'].pop(idx))
            logger.info(f"Sweep deactivated {event['id']}")
