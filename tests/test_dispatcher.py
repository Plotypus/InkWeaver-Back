from loom.database.interfaces import MongoDBAsyncioInterface
from loom.dispatchers import LAWProtocolDispatcher
from loom.dispatchers.messages.outgoing import *

import asyncio
import pytest

TEST_DB_NAME = 'test'
TEST_DB_HOST = 'localhost'
TEST_DB_PORT = 27017

TEST_USER = {
    'username': 'test-user',
    'password': 'test-password',
    'name':     'test-name',
    'email':    'test-email',
}


class TestLAWDispatcher:
    def setup(self):
        self.interface = MongoDBAsyncioInterface(TEST_DB_NAME, TEST_DB_HOST, TEST_DB_PORT)
        self.event_loop = asyncio.get_event_loop()
        self.user_id = self.event_loop.run_until_complete(self.interface.create_user(**TEST_USER))
        self.dispatcher = LAWProtocolDispatcher(self.interface, self.user_id)

    def teardown(self):
        self.event_loop.run_until_complete(self.interface.drop_database())
        self.event_loop.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_user_preferences', {'message_id': 83})
    ])
    async def test_get_user_preferences(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetUserPreferencesOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.username == TEST_USER['username']
        assert result.name == TEST_USER['name']
        assert result.email == TEST_USER['email']
        assert result.bio is None
        assert result.avatar is None
