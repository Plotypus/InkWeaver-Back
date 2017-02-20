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

TEST_STORY = {
    'title':   'test-title',
    'wiki_id': ObjectId(),
    'summary': 'test-summary'
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

    async def create_test_story(self):
        story_id = await self.interface.create_story(self.user_id, **TEST_STORY)
        story = await self.interface.get_story(story_id)
        return story_id, story['section_id']

    async def create_test_paragraph(self, section_id):
        paragraph_id = await self.interface.add_paragraph(section_id, 'test-text', None)
        return paragraph_id

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
        ('add_preceding_subsection', {'message_id': 9, 'title': 'test-pre', 'parent_id': None, 'index': 0})
    ])
    async def test_add_preceding_subsection(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['parent_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, AddPrecedingSubsectionOutgoingMessage)
        assert result.section_id is not None
        assert isinstance(result.section_id, ObjectId)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('add_inner_subsection', {'message_id': 9, 'title': 'test-inner', 'parent_id': None, 'index': 0})
    ])
    async def test_add_inner_subsection(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['parent_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, AddInnerSubsectionOutgoingMessage)
        assert result.section_id is not None
        assert isinstance(result.section_id, ObjectId)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('add_succeeding_subsection', {'message_id': 9, 'title': 'test-suc', 'parent_id': None, 'index': 0})
    ])
    async def test_add_succeeding_subsection(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['parent_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, AddSucceedingSubsectionOutgoingMessage)
        assert result.section_id is not None
        assert isinstance(result.section_id, ObjectId)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('add_paragraph', {'message_id': 21, 'section_id': None, 'text': 'test-text', 'succeeding_paragraph_id': None})
    ])
    async def test_add_paragraph(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['section_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, AddParagraphOutgoingMessage)
        assert result.paragraph_id is not None
        assert isinstance(result.paragraph_id, ObjectId)
        # Try again with succeeding_paragraph_id set
        msg['succeeding_paragraph_id'] = result.paragraph_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, AddParagraphOutgoingMessage)
        assert result.paragraph_id is not None
        assert isinstance(result.paragraph_id, ObjectId)

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg, wrong_type, wrong_key, correct', [
        (
                'edit_story',
                {'message_id': 32, 'story_id': None, 'update': None},
                {'update_type': 'test-wrong-type'},
                {'update_type': 'set_title', 'test-wrong-key': ''},
                {'update_type': 'set_title', 'title': 'test-title-change'}
        )
    ])
    async def test_edit_story(self, action, msg, wrong_type, wrong_key, correct):
        story_id, _ = await self.create_test_story()
        msg['story_id'] = story_id
        # Test response to using the wrong `update_type`
        msg['update'] = wrong_type
        error_json = await self.dispatcher.dispatch(msg, action)
        assert f'invalid `update_type`: {wrong_type["update_type"]}' in error_json['reason']
        # Test response to wrong key in `update`
        msg['update'] = wrong_key
        error_json = await self.dispatcher.dispatch(msg, action)
        assert 'KeyError' in error_json['reason']
        # Test valid case
        msg['update'] = correct
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, EditStoryOutgoingMessage)
        assert result.reply_to_id == msg['message_id']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg, wrong_type, wrong_key, correct', [
        (
                'edit_paragraph',
                {'message_id': 32, 'section_id': None, 'paragraph_id': None, 'update': None},
                {'update_type': 'test-wrong-type'},
                {'update_type': 'set_text', 'test-wrong-key': ''},
                {'update_type': 'set_text', 'text': 'test-text-change'}
        )
    ])
    async def test_edit_paragraph(self, action, msg, wrong_type, wrong_key, correct):
        _, section_id = await self.create_test_story()
        paragraph_id = await self.create_test_paragraph(section_id)
        msg['section_id'] = section_id
        msg['paragraph_id'] = paragraph_id
        # Test response to using the wrong `update_type`
        msg['update'] = wrong_type
        error_json = await self.dispatcher.dispatch(msg, action)
        assert f'invalid `update_type`: {wrong_type["update_type"]}' in error_json['reason']
        # Test response to wrong key in `update`
        msg['update'] = wrong_key
        error_json = await self.dispatcher.dispatch(msg, action)
        assert 'KeyError' in error_json['reason']
        # Test valid case
        msg['update'] = correct
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, EditParagraphOutgoingMessage)
        assert result.reply_to_id == msg['message_id']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('edit_section_title', {'message_id': 32, 'section_id': None, 'new_title': 'test-title-change'})
    ])
    async def test_edit_section_title(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['section_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, EditSectionTitleOutgoingMessage)
        assert result.reply_to_id == msg['message_id']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_story_information', {'message_id': 65, 'story_id': None})
    ])
    async def test_get_story_information(self, action, msg):
        story_id, section_id =  await self.create_test_story()
        msg['story_id'] = story_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetStoryInformationOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.story_title == TEST_STORY['title']
        assert result.section_id == section_id
        assert result.wiki_id == TEST_STORY['wiki_id']
        user_info = {
            'user_id':       self.user_id,
            'name': TEST_USER['name'],
            'access_level':  'owner',
        }
        assert user_info in result.users
        assert result.summary == TEST_STORY['summary']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_story_hierarchy', {'message_id': 44, 'story_id': None})
    ])
    async def test_get_story_hierarchy(self, action, msg):
        story_id, section_id = await self.create_test_story()
        msg['story_id'] = story_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetStoryHierarchyOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.hierarchy['title'] == TEST_STORY['title']
        assert result.hierarchy['section_id'] == section_id
        assert result.hierarchy['preceding_subsections'] == list()
        assert result.hierarchy['inner_subsections'] == list()
        assert result.hierarchy['succeeding_subsections'] == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_section_hierarchy', {'message_id': 72, 'section_id': None})
    ])
    async def test_get_section_hierarchy(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['section_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetSectionHierarchyOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.hierarchy['title'] == TEST_STORY['title']
        assert result.hierarchy['section_id'] == section_id
        assert result.hierarchy['preceding_subsections'] == list()
        assert result.hierarchy['inner_subsections'] == list()
        assert result.hierarchy['succeeding_subsections'] == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('get_section_content', {'message_id': 1, 'section_id': None})
    ])
    async def test_get_section_content(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['section_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, GetSectionContentOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.content == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('delete_story', {'message_id': 2, 'story_id': None})
    ])
    async def test_delete_story(self, action, msg):
        story_id, _ = await self.create_test_story()
        msg['story_id'] = story_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, DeleteStoryOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.event == "story_deleted"

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('delete_section', {'message_id': 2, 'section_id': None})
    ])
    async def test_delete_section(self, action, msg):
        _, section_id = await self.create_test_story()
        msg['section_id'] = section_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, DeleteSectionOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.event == 'section_deleted'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('action, msg', [
        ('delete_paragraph', {'message_id': 2, 'section_id': None, 'paragraph_id': None})
    ])
    async def test_delete_paragraph(self, action, msg):
        _, section_id = await self.create_test_story()
        paragraph_id = await self.create_test_paragraph(section_id)
        msg['section_id'] = section_id
        msg['paragraph_id'] = paragraph_id
        result = await self.dispatcher.dispatch(msg, action)
        assert isinstance(result, DeleteParagraphOutgoingMessage)
        assert result.reply_to_id == msg['message_id']
        assert result.event == "paragraph_deleted"

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
