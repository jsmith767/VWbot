import asyncio
import unittest
from typing import Any
from unittest.mock import Mock, patch, AsyncMock

from telegram.ext import CommandHandler

from EmberEventBot.command_handlers.event.edit import edit_conv_handler


class TestEdit(unittest.TestCase):
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
        update_mock.message.from_user = TestEdit.TEST_USER_MOCK
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
    @patch("EmberEventBot.command_handlers.event.edit.EventModel")
    def test_general(self, event_model_patch, valid_admin, valid_chat):
        valid_admin.return_value = True
        valid_chat.return_value = True
        event_model_obj = Mock()
        event_model_patch.return_value = event_model_obj
        conversation_handler = edit_conv_handler()

        # Assert that there is only one entry point
        self.assertEqual(len(conversation_handler._entry_points), 1)

        entry_point = conversation_handler._entry_points[0]

        self.assertIsInstance(entry_point, CommandHandler)
        # Assert that the entry point is "edit"
        self.assertSetEqual(entry_point.commands, {"edit"})
        current_handler = entry_point.callback

        context_mock = Mock()
        context_mock.chat_data = {}
        context_mock.bot_data = {
            "events": {
                "active": [
                    {
                        "id": "TEST EVENT",
                        "summary": "Summary",
                        "date": "19940302",
                        "maxhead": 0,
                        "description": "TEST DESCRIPTION",
                    }
                ]
            }
        }

        update_mock = Mock()
        update_mock.callback_query = None

        # Start edit conversation
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)

        update_mock = Mock()
        update_mock.callback_query.data = "event0TEST EVENT"

        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)

        update_mock = Mock()
        update_mock.callback_query.data = "event1summary"
        (current_handler, reply_text) = self.reply_and_get_next(update_mock, context_mock, conversation_handler,
                                                                current_handler)
        update_mock = Mock()
        update_mock.message.text = "Summary Updated"
        self.reply_and_get_next(update_mock, context_mock, conversation_handler, current_handler)
        event_model_patch.assert_called_with(id='TEST EVENT', date='19940302', summary='Summary', maxhead=0,
                                             description='TEST DESCRIPTION')
        event_model_obj.commit.assert_called()
        self.assertEqual(event_model_obj.summary, "Summary Updated")
        self.assertEqual(context_mock.chat_data, {'event_id': 'TEST EVENT', 'field': 'summary'})
