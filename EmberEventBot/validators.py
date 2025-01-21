from collections.abc import Coroutine
from functools import wraps
from logging import getLogger
from typing import List, Any, Callable
import requests
from telegram import Update
from telegram.ext import ContextTypes

from EmberEventBot.constants import UserAccessLevel
from EmberEventBot.exceptions import EmberAccessException
from EmberEventBot.settings import EmberEventBotSettings

logger = getLogger(__name__)

settings = EmberEventBotSettings()

def get_chat_administrators(chat_id) -> List[Any]:
    """Fetches a list of admins for a channel or group"""
    url = f"https://api.telegram.org/bot{settings.embtoken}/getChatAdministrators?chat_id={str(chat_id)}"
    response = requests.get(url=url)
    data = response.json()
    if data['ok']:
        return data['result']
    return []

def member_status(user_id, chat_id) -> str:
    """Fetches member status in a group or channel, bot must be a member"""
    url = f"https://api.telegram.org/bot{settings.embtoken}/getChatMember?chat_id={chat_id}&user_id={user_id}"
    response = requests.get(url=url)
    if response.ok:
        data = response.json()
        if data['ok']:
            return data['result']['status']
    else:
        logger.error(response.raw)
    return 'unknown'

def valid(user_id: int, chat_id: str, status: List[str]) -> bool:
    """Look up a member status in chat_id and check it against a list
    of status."""
    ms = member_status(user_id=user_id, chat_id=chat_id)
    logger.info(f'User {user_id} is {ms} of {chat_id}')
    if ms in status or user_id in settings.dev_ids:
        return True
    return False

def valid_user(user_id: int):
    return valid(user_id=user_id, chat_id=settings.user_group, status=settings.user_status)

def valid_admin(user_id: int):
    return valid(user_id=user_id, chat_id=settings.admin_group, status=settings.admin_status)

def valid_chat(chat_id: int = 0) -> bool:
    """Returns True if the chat_id is apropriate else False"""
    if chat_id >= 0 or str(chat_id) in settings.valid_group:
        return True ## command is from private chat or group in the valid list
    return False    ## command is from group not in the valid list

def restricted(access_level: UserAccessLevel) -> Callable[
    [Callable[[Update, Any], Coroutine[Any, Any, None]]], Callable[[Update, Any], Coroutine[Any, Any, None]]]:
    def restricted_inner(func: Callable[[Update, Any], Coroutine[Any, Any, None]]) -> (
            Callable)[[Update, Any], Coroutine[Any, Any, None]]:
        @return_none_for_bad_access
        @access_log(access_level)
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            mapaccess = {
                UserAccessLevel.ADMIN: valid_admin,
                UserAccessLevel.USER: valid_user,
                UserAccessLevel.NONE: lambda user_id: True
            }
            valid_access = mapaccess[access_level](user_id=update.effective_user.id)
            valid_cid = valid_chat(chat_id=update.effective_chat.id)
            if valid_access and valid_cid:
                return await func(update, context)
            raise EmberAccessException(
                valid_access=access_level,
                requested_access=UserAccessLevel.USER
                if valid_user(user_id=update.effective_user.id) else UserAccessLevel.NONE
            )
        return wrapped

    return restricted_inner


def return_none_for_bad_access(func: Callable[[Update, Any], Coroutine[Any, Any, None]]) -> (
        Callable)[[Update, Any], Coroutine[Any, Any, None]]:
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            return await func(update, context)
        except EmberAccessException:
            return None

    return wrapped


def access_log(access_level: UserAccessLevel) -> Callable[
    [Callable[[Update, Any], Coroutine[Any, Any, None]]], Callable[[Update, Any], Coroutine[Any, Any, None]]]:
    def access_log_inner(func: Callable[[Update, Any], Coroutine[Any, Any, None]]) -> (
            Callable)[[Update, Any], Coroutine[Any, Any, None]]:
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            try:
                valid_access = True
                return await func(update, context)
            except EmberAccessException:
                valid_access = False
                raise
            finally:
                try:
                    getLogger("access").info(
                        msg=update.message.text if hasattr(update.message, "text") else "no_text",
                        extra={
                            "user_id": update.effective_user.id,
                            "func_name": func.__name__,
                            "access_type": access_level,
                            "access": "GRANTED" if valid_access else "DENIED",
                        })
                except Exception as e:
                    logger.error(str(e))

        return wrapped

    return access_log_inner
