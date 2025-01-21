import asyncio
import unittest
from typing import Any
from unittest.mock import Mock, patch

from telegram.ext import CommandHandler

from EmberEventBot.command_handlers.event.create import create_conv_handler


class TestCreate(unittest.TestCase):
    TEST_USER_MOCK = Mock()
    TEST_USER_MOCK.name = "Member McMemberson"
    loop: Any

    @classmethod
    def setUpClass(cls):
        cls.loop = asyncio.new_event_loop()

    @classmethod
    def tearDownClass(cls):
        cls.loop.close()

    def reply_and_get_next(self, text, context_mock, conversation_handler, callback):
        reply_text_future = asyncio.Future(loop=self.loop)
        reply_text_future.set_result(None)
        update_mock = Mock()
        update_mock.message.reply_text.return_value = reply_text_future
        update_mock.message.from_user = TestCreate.TEST_USER_MOCK
        update_mock.message.text = text
        next_handler = self.loop.run_until_complete(callback(update_mock, context_mock))
        if next_handler == -1:
            return (None, update_mock.message.reply_text.call_args[0][0])
        return (conversation_handler.states[next_handler][0].callback, update_mock.message.reply_text.call_args[0][0])

    @patch("EmberEventBot.validators.valid_admin")
    @patch("EmberEventBot.validators.valid_chat")
    @patch("EmberEventBot.command_handlers.event.create.EventModel")
    def test_general(self, event_model_patch, valid_admin, valid_chat):
        valid_admin.return_value = True
        valid_chat.return_value = True
        event_model_obj = Mock()
        event_model_patch.return_value = event_model_obj
        conversation_handler = create_conv_handler()

        # Assert that there is only one entry point
        self.assertEqual(len(conversation_handler._entry_points), 1)

        entry_point = conversation_handler._entry_points[0]

        self.assertIsInstance(entry_point, CommandHandler)
        # Assert that the entry point is "create"
        self.assertSetEqual(entry_point.commands, {"create"})
        current_handler = entry_point.callback

        context_mock = Mock()
        context_mock.chat_data = {}
        context_mock.bot_data = {}

        # Start create conversation
        (current_handler, reply_text) = self.reply_and_get_next("/create", context_mock, conversation_handler,
                                                                current_handler)
        (current_handler, reply_text) = self.reply_and_get_next("TEST EVENT", context_mock, conversation_handler,
                                                                current_handler)
        (current_handler, reply_text) = self.reply_and_get_next("03 02 1994", context_mock, conversation_handler,
                                                                current_handler)
        (current_handler, reply_text) = self.reply_and_get_next("TEST SUMMARY", context_mock, conversation_handler,
                                                                current_handler)
        (current_handler, reply_text) = self.reply_and_get_next("0", context_mock, conversation_handler,
                                                                current_handler)
        self.reply_and_get_next("TEST DESCRIPTION", context_mock, conversation_handler,
                                current_handler)

        event_model_patch.assert_called_with(id='TEST EVENT', date='19940302', summary='TEST SUMMARY', maxhead=0,
                                             description='TEST DESCRIPTION')
        event_model_obj.commit.assert_called()
        self.assertEqual(context_mock.chat_data, {
            'event': {'id': 'TEST EVENT', 'date': '19940302', 'summary': 'TEST SUMMARY', 'maxhead': 0,
                      'description': 'TEST DESCRIPTION'}})
        # self.assertEqual(context_mock.bot_data, {'events': {'active': [], 'inactive': []}})

    @patch("EmberEventBot.validators.valid_admin")
    @patch("EmberEventBot.validators.valid_chat")
    @patch("EmberEventBot.command_handlers.event.create.EventModel")
    def test_string_date(self, event_model_patch, valid_admin, valid_chat):
        valid_admin.return_value = True
        valid_chat.return_value = True
        event_model_obj = Mock()
        event_model_patch.return_value = event_model_obj
        conversation_handler = create_conv_handler()

        # Assert that there is only one entry point
        self.assertEqual(len(conversation_handler._entry_points), 1)

        entry_point = conversation_handler._entry_points[0]

        self.assertIsInstance(entry_point, CommandHandler)
        # Assert that the entry point is "create"
        self.assertSetEqual(entry_point.commands, {"create"})
        current_handler = entry_point.callback

        context_mock = Mock()
        context_mock.chat_data = {}
        context_mock.bot_data = {}

        # Start create conversation
        (current_handler, reply_text) = self.reply_and_get_next("/create", context_mock, conversation_handler,
                                                                current_handler)
        (current_handler, reply_text) = self.reply_and_get_next("TEST EVENT", context_mock, conversation_handler,
                                                                current_handler)

        # Bad Date
        (current_handler, reply_text) = self.reply_and_get_next("The fiftieth of Octember", context_mock,
                                                                conversation_handler,
                                                                current_handler)
        # Bad Date
        (current_handler, reply_text) = self.reply_and_get_next("Gadzooks", context_mock,
                                                                conversation_handler,
                                                                current_handler)
        # Bad Date. February never has 30 days.
        (current_handler, reply_text) = self.reply_and_get_next("02 30 1994", context_mock,
                                                                conversation_handler,
                                                                current_handler)
        # Good Date
        (current_handler, reply_text) = self.reply_and_get_next("03 02 1994", context_mock,
                                                                conversation_handler,
                                                                current_handler)

        (current_handler, reply_text) = self.reply_and_get_next("TEST SUMMARY", context_mock, conversation_handler,
                                                                current_handler)
        (current_handler, reply_text) = self.reply_and_get_next("0", context_mock, conversation_handler,
                                                                current_handler)
        self.reply_and_get_next("TEST DESCRIPTION", context_mock,
                                conversation_handler,
                                current_handler)

        event_model_patch.assert_called_with(id='TEST EVENT', date='19940302', summary='TEST SUMMARY', maxhead=0,
                                             description='TEST DESCRIPTION')
        event_model_obj.commit.assert_called()
        self.assertEqual(context_mock.chat_data, {
            'event': {'id': 'TEST EVENT', 'date': '19940302', 'summary': 'TEST SUMMARY', 'maxhead': 0,
                      'description': 'TEST DESCRIPTION'}})
        # self.assertEqual(context_mock.bot_data, {'events': {'active': [], 'inactive': []}})


if __name__ == "__main__":
    unittest.main()
