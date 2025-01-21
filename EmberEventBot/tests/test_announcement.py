import asyncio
import unittest
from typing import Any
from unittest.mock import Mock, patch, AsyncMock

from telegram.ext import CommandHandler

from EmberEventBot.command_handlers.announcement import announcement_conv_handler


class Testannouncement(unittest.TestCase):
    TEST_USER_MOCK = Mock()
    TEST_USER_MOCK.name = "Member McMemberson"
    loop: Any

    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.new_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    def reply_and_get_next(self, update_mock, context_mock, conversation_handler, callback):
        reply_text_future = asyncio.Future(loop=self.loop)
        reply_text_future.set_result(None)
        if update_mock.callback_query is not None:
            update_mock.callback_query.answer = AsyncMock()
        update_mock.message.reply_text.return_value = reply_text_future
        if update_mock.callback_query is not None:
            update_mock.callback_query.edit_message_text.return_value = reply_text_future
        update_mock.message.from_user = Testannouncement.TEST_USER_MOCK
        next_handler = self.loop.run_until_complete(callback(update_mock, context_mock))
        if next_handler == -1:
            return (None, update_mock.message.reply_text.call_args[0][0])
        if update_mock.callback_query is not None:
            call_args = update_mock.callback_query.edit_message_text.call_args
        else:
            call_args = update_mock.message.reply_text.call_args
        return (conversation_handler.states[next_handler][0].callback, call_args[0][0])

    @patch("EmberEventBot.validators.valid_admin")
    @patch("EmberEventBot.validators.valid_chat")
    def test_general(self, valid_admin, valid_chat):
        valid_admin.return_value = True
        valid_chat.return_value = True
        conversation_handler = announcement_conv_handler()

        # Assert that there is only one entry point
        self.assertEqual(len(conversation_handler._entry_points), 1)

        entry_point = conversation_handler._entry_points[0]

        self.assertIsInstance(entry_point, CommandHandler)
        # Assert that the entry point is "announcement"
        self.assertSetEqual(entry_point.commands, {"announcement"})
        current_handler = entry_point.callback

        context_mock = Mock()
        context_mock.chat_data = {}

        update_mock = Mock()
        update_mock.callback_query = None

        headline = "TEST announcement"
        body = "The body of the announcement"
        # Start announcement conversation
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)
        update_mock.message.text = headline
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)
        self.assertEqual(context_mock.chat_data['headline'], headline)
        update_mock.message.text = body
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)
        self.assertEqual(context_mock.chat_data['body'], body)
        update_mock = Mock()
        update_mock.callback_query.data = "announcement2BOTDEV"
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)
        self.assertEqual(context_mock.chat_data['chat'],"BOTDEV")
        update_mock = Mock()
        update_mock.callback_query.data = "announcement3CANCEL"
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)
        self.assertEqual(current_handler.__name__, 'headline')


