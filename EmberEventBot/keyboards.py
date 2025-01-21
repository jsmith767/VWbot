from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from EmberEventBot.settings import EmberEventBotSettings
from EmberEventBot.constants import ConfirmKBD, ChatGroups

SETTINGS = EmberEventBotSettings()

async def confirm_kbd(callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for rsvp plus one"""
    keyboard = [[
        InlineKeyboardButton("Confirm", callback_data=callback_prefix + ConfirmKBD.CONFIRM.name),
        InlineKeyboardButton("Cancel", callback_data=callback_prefix + ConfirmKBD.CANCEL.name),
    ]]
    return InlineKeyboardMarkup(keyboard)

async def chat_groups_kbd(callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for rsvp plus one"""
    keyboard = [[
        InlineKeyboardButton(
            cg.name,
            callback_data=callback_prefix + cg.name
        ) for cg in ChatGroups
    ]]
    return InlineKeyboardMarkup(keyboard)

async def rsvp_kbd(callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for rsvp status"""
    keyboard = [
        [
            InlineKeyboardButton("going", callback_data=callback_prefix + "going"),
            InlineKeyboardButton("maybe", callback_data=callback_prefix + "maybe"),
        ],
        [
            InlineKeyboardButton("+1", callback_data=callback_prefix + "plusone"),
            InlineKeyboardButton("waitlist", callback_data=callback_prefix + "waitlist"),
        ],
        [
            InlineKeyboardButton("fomo", callback_data=callback_prefix + "fomo"),
            InlineKeyboardButton("remove", callback_data=callback_prefix + "remove")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def field_kbd(callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Inline keyboard for event fields"""
    keyboard = [[InlineKeyboardButton(v, callback_data=callback_prefix + k)] for k, v in
                SETTINGS.editable_fields.items()]
    return InlineKeyboardMarkup(keyboard)


async def inactive_event_kbd(context: ContextTypes.DEFAULT_TYPE, callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for events"""
    buttons = []
    my_events = list(context.bot_data['events']['inactive'])
    my_events.sort(key=lambda x: x["date"])
    event_list = [x['id'] for x in reversed(my_events)]
    for e in event_list:
        buttons.append(InlineKeyboardButton(str(e)[0:30], callback_data=callback_prefix + e))
    buttons.append(InlineKeyboardButton("Cancel", callback_data=callback_prefix + "cancel"))
    chunked_list = []
    chunk_size = 2 if len(buttons) > 8 else 1
    for i in range(0, len(buttons), chunk_size):
        chunked_list.append(buttons[i:i + chunk_size])
    return InlineKeyboardMarkup(chunked_list)


async def event_kbd(context: ContextTypes.DEFAULT_TYPE, callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for events"""
    buttons = []
    event_list = [x['id'] for x in context.bot_data['events']['active']]
    for e in event_list:
        buttons.append(InlineKeyboardButton(str(e)[0:30], callback_data=callback_prefix + e))
    buttons.append(InlineKeyboardButton("Cancel", callback_data=callback_prefix + "cancel"))
    chunked_list = []
    chunk_size = 2 if len(buttons) > 8 else 1
    for i in range(0, len(buttons), chunk_size):
        chunked_list.append(buttons[i:i + chunk_size])
    return InlineKeyboardMarkup(chunked_list)


async def contact_kbd(callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for contact status"""
    keyboard = [
        [
            InlineKeyboardButton("remind 3d b4 event", callback_data=callback_prefix + "remind3d"),
            InlineKeyboardButton("remind 1d b4 event", callback_data=callback_prefix + "remind1d"),
        ],
        [
            InlineKeyboardButton("dm me new events", callback_data=callback_prefix + "newevent"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def plus_one_kbd(callback_prefix: str = "") -> InlineKeyboardMarkup:
    """Returns an inline keyboard for rsvp plus one"""
    keyboard = [[
        InlineKeyboardButton("+0", callback_data=callback_prefix + "0"),
        InlineKeyboardButton("+1", callback_data=callback_prefix + "1"),
        InlineKeyboardButton("+2", callback_data=callback_prefix + "2"),
    ]]
    return InlineKeyboardMarkup(keyboard)
