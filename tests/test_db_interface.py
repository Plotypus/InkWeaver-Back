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

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-story',
             'summary': 'This is a story for testing',
             'wiki_id': 'placeholder for wiki id',
         })
    ])
    async def test_story_creation(self, user, story):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story_ids = await self.interface.get_user_stories(user_id)
        story_summary = {
            'story_id': story_id,
            'title': story['title'],
            'access_level': 'owner',
        }
        assert story_summary in story_ids
        db_story = await self.interface.get_story(story_id)
        assert db_story['title'] == story['title']
        assert db_story['summary'] == story['summary']
        assert db_story['wiki_id'] == story['wiki_id']
        user_description = {
            'user_id': user_id,
            'name': user['name'],
            'access_level': 'owner',
        }
        assert user_description in db_story['users']
        assert db_story['section_id'] is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('title', [
        'Introduction'
    ])
    async def test_create_section(self, title):
        section_id = await self.interface.create_section(title)
        hierarchy = await self.interface.get_section_hierarchy(section_id)
        assert hierarchy['title'] == title
        assert hierarchy['section_id'] == section_id
        assert hierarchy['preceding_subsections'] == list()
        assert hierarchy['inner_subsections'] == list()
        assert hierarchy['succeeding_subsections'] == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-story',
             'summary': 'This is a story for testing',
             'wiki_id': 'placeholder for wiki id',
         })
    ])
    async def test_get_story_hierarchy(self, user, story):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        section_id = story['section_id']
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        section_hierarchy = await self.interface.get_section_hierarchy(section_id)
        assert story_hierarchy == section_hierarchy
        assert story_hierarchy['title'] == story['title']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,section_title', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-story',
             'summary': 'This is a story for testing',
             'wiki_id': 'placeholder for wiki id',
         },
        'Prologue')
    ])
    async def test_append_preceding_section(self, user, story, section_title):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        await self.interface.append_preceding_subsection(section_title, story_section_id)
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        assert len(story_hierarchy['preceding_subsections']) == 1
        section_hierarchy = story_hierarchy['preceding_subsections'][0]
        assert section_hierarchy['title'] == section_title

    
