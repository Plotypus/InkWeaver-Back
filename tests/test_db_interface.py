from loom.database.interfaces import MongoDBAsyncioInterface

import asyncio
import pytest


class TestDBInterface:
    def setup(self):
        self.interface = MongoDBAsyncioInterface('test', 'localhost', 27017)

    def teardown(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.interface.client.drop_database())
        event_loop.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user', [
        {
            'username': 'tmctest',
            'password': 'my gr3at p4ssw0rd',
            'name':     'Testy McTesterton',
            'email':    'tmctest@te.st',
        },
    ])
    async def test_user_creation(self, user):
        inserted_id = await self.interface.create_user(**user)
        assert await self.interface.password_is_valid_for_username(user['username'], user['password'])
        prefs = await self.interface.get_user_preferences(inserted_id)
        assert prefs['username'] == user['username']
        assert prefs['name'] == user['name']
        assert prefs['email'] == user['email']
        assert await self.interface.get_user_stories(inserted_id) == list()
        assert await self.interface.get_user_wikis(inserted_id) == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user', [
        {
            'username': 'tmctest',
            'password': 'my gr3at p4ssw0rd',
            'name':     'Testy McTesterton',
            'email':    'tmctest@te.st',
        },
    ])
    async def test_get_user_id_for_username(self, user):
        inserted_id = await self.interface.create_user(**user)
        assert await self.interface.get_user_id_for_username(user['username']) == inserted_id
