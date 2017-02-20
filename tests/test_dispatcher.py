from loom.database.interfaces import MongoDBAsyncioInterface
from loom.dispatchers.LAWProtocolDispatcher import LAWProtocolDispatcher, LAWNotLoggedInError
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
    async def test_requires_login(self):
        self.dispatcher.set_user_id(None)
        assert self.dispatcher.user_id is None
        with pytest.raises(LAWNotLoggedInError):
            await self.dispatcher.get_user_wikis(0)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('message, action', [
        ({'message_id': 83}, '123')
    ])
    async def test_bad_action(self, message, action):
        error_json = await self.dispatcher.dispatch(message, action, message['message_id'])
        assert error_json['reply_to_id'] == message['message_id']
        assert not error_json['success']
        assert f"'{action}' not supported" in error_json['reason']

        error_json = await self.dispatcher.dispatch(message, action, None)
        assert error_json.get('reply_to_id') is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('msg_missing, msg_extra, action', [
        ({}, {'message_id': 1, 'extra': 24}, 'get_user_preferences')
    ])
    async def test_bad_message(self, msg_missing, msg_extra, action):
        missing = await self.dispatcher.dispatch(msg_missing, action, None)
        assert "Missing fields" in missing['reason']
        extra = await self.dispatcher.dispatch(msg_extra, action, None)
        assert "Unsupported fields" in extra['reason']

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

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_user_stories', {'message_id': 12})
    ])
    async def test_get_user_stories(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetUserStoriesOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.stories == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_user_wikis', {'message_id': 12})
    ])
    async def test_get_user_wikis(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetUserWikisOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.wikis == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('set_user_name', {'message_id': 87, 'name': 'name-test'})
    ])
    async def test_set_user_name(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('set_user_email', {'message_id': 23, 'email': 'abc@def.ghi'})
    ])
    async def test_set_user_email(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('set_user_bio', {'message_id': 23, 'bio': 'test-bio'})
    ])
    async def test_set_user_bio(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert result is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('user_login', {'message_id': 182, 'username': TEST_USER['username'], 'password': 'bad-pass'})
    ])
    async def test_user_login(self, action, msg):
        error_json = await self.dispatcher.dispatch(msg, action)
        assert error_json['reason'] == "Already logged in."
        # Reset user_id
        self.dispatcher.set_user_id(None)
        # Use bad password
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, UserLoginOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.event == 'denied'
        # Right password
        msg['password'] = TEST_USER['password']
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, UserLoginOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.event == 'logged_in'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('create_story', {'message_id': 8, 'title': 'test-story', 'wiki_id': ObjectId(), 'summary': 'test-summary'})
    ])
    async def test_create_story(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, CreateStoryOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.story_id is not None
        assert isinstance(result.story_id, ObjectId)
        assert result.section_id is not None
        assert isinstance(result.section_id, ObjectId)
        assert result.wiki_id == msg['wiki_id']
        user_info = {
            'user_id':      self.user_id,
            'name':         TEST_USER['name'],
            'access_level': 'owner',
        }
        assert user_info in result.users
        assert result.summary == msg['summary']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('create_wiki', {'message_id': 9, 'title': 'test-wiki', 'summary': 'Blah blah test-wiki'})
    ])
    async def test_create_wiki(self, action, msg):
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, CreateWikiOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.wiki_title == msg['title']
        assert result.wiki_id is not None
        assert isinstance(result.wiki_id, ObjectId)
        assert result.segment_id is not None
        assert isinstance(result.segment_id, ObjectId)
        user_info = {
            'user_id':      self.user_id,
            'name':         TEST_USER['name'],
            'access_level': 'owner',
        }
        assert user_info in result.users
        assert result.summary == msg['summary']
