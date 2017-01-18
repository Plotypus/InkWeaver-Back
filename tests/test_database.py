from loom import database

import asyncio
import pytest

from bson.objectid import ObjectId


class TestDatabase:
    def setup(self):
        self.client = database.MongoDBMotorAsyncioClient('test')

    def teardown(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.client.drop_database())
        event_loop.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user', [
        {
            'username':      'tmctest',
            'password_hash': 'hashedpass',
            'name':          'Testy McTesterton',
            'email':         'tmctest@te.st',
            'bio':           'Someone who likes to test things.',
            'avatar':        None,
        },
        {
            'username':      'tetester3',
            'password_hash': 'passthatishashed',
            'name':          'Testington Tester III',
            'email':         'tetester3@te.st',
            'bio':           'Testedness is next to godliness.',
            'avatar':        None,
            '_id':           ObjectId('000000000000000000000000')
        },
    ])
    async def test_user_creation(self, user):
        hashless_user = {k: v for k, v in user.items() if k not in ('password_hash', '_id')}
        inserted_id = await self.client.create_user(**user)
        assert inserted_id is not None
        assert await self.client.get_password_hash_for_username(user['username']) == user['password_hash']
        assert await self.client.get_user_preferences(inserted_id) == hashless_user

    @pytest.mark.asyncio
    async def test_get_user_story_ids(self):
        pass

    @pytest.mark.asyncio
    async def test_get_user_wiki_ids(self):
        pass

    @pytest.mark.asyncio
    async def test_get_user_story_and_wiki_ids(self):
        pass

    @pytest.mark.asyncio
    async def test_get_story(self):
        pass

    @pytest.mark.asyncio
    async def test_get_section(self):
        pass

    @pytest.mark.asyncio
    async def test_get_wiki(self):
        pass

    @pytest.mark.asyncio
    async def test_get_segment(self):
        pass

    @pytest.mark.asyncio
    async def test_get_page(self):
        pass

    @pytest.mark.asyncio
    async def test_get_heading(self):
        pass

    @pytest.mark.asyncio
    async def test_get_content(self):
        pass

    @pytest.mark.asyncio
    async def test_get_paragraph(self):
        pass

    @pytest.mark.asyncio
    async def test_create_user(self):
        pass

    @pytest.mark.asyncio
    async def test_create_story(self):
        pass

    @pytest.mark.asyncio
    async def test_create_section(self):
        pass

    @pytest.mark.asyncio
    async def test_create_wiki(self):
        pass

    @pytest.mark.asyncio
    async def test_create_segment(self):
        pass

    @pytest.mark.asyncio
    async def test_create_page(self):
        pass

    @pytest.mark.asyncio
    async def test_create_heading(self):
        pass

    @pytest.mark.asyncio
    async def test_create_content(self):
        pass

    @pytest.mark.asyncio
    async def test_create_paragraph(self):
        pass
