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

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,title_one,title_two,title_three', [
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
         'Prologue II', 'Prologue I', 'Prologue III')
    ])
    async def test_insert_preceding_section(self, user, story, title_one, title_two, title_three):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        await self.interface.append_preceding_subsection(title_one, story_section_id)
        await self.interface.insert_preceding_subsection(title_two, story_section_id, 0)
        await self.interface.insert_preceding_subsection(title_three, story_section_id, 2)
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        assert len(story_hierarchy['preceding_subsections']) == 3
        expected_title_order = [title_two, title_one, title_three]
        titles = [section['title'] for section in story_hierarchy['preceding_subsections']]
        assert titles == expected_title_order

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
         'Chapter One')
    ])
    async def test_append_inner_section(self, user, story, section_title):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        await self.interface.append_inner_subsection(section_title, story_section_id)
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        assert len(story_hierarchy['inner_subsections']) == 1
        section_hierarchy = story_hierarchy['inner_subsections'][0]
        assert section_hierarchy['title'] == section_title

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,title_one,title_two,title_three', [
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
         'Chapter II', 'Chapter I', 'Chapter III')
    ])
    async def test_insert_inner_section(self, user, story, title_one, title_two, title_three):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        await self.interface.append_inner_subsection(title_one, story_section_id)
        await self.interface.insert_inner_subsection(title_two, story_section_id, 0)
        await self.interface.insert_inner_subsection(title_three, story_section_id, 2)
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        assert len(story_hierarchy['inner_subsections']) == 3
        expected_title_order = [title_two, title_one, title_three]
        titles = [section['title'] for section in story_hierarchy['inner_subsections']]
        assert titles == expected_title_order

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
         'EpilogueEpilogue One')
    ])
    async def test_append_succeeding_section(self, user, story, section_title):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        await self.interface.append_succeeding_subsection(section_title, story_section_id)
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        assert len(story_hierarchy['succeeding_subsections']) == 1
        section_hierarchy = story_hierarchy['succeeding_subsections'][0]
        assert section_hierarchy['title'] == section_title

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,title_one,title_two,title_three', [
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
         'Epilogue II', 'Epilogue I', 'Epilogue III')
    ])
    async def test_insert_succeeding_section(self, user, story, title_one, title_two, title_three):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        await self.interface.append_succeeding_subsection(title_one, story_section_id)
        await self.interface.insert_succeeding_subsection(title_two, story_section_id, 0)
        await self.interface.insert_succeeding_subsection(title_three, story_section_id, 2)
        story_hierarchy = await self.interface.get_story_hierarchy(story_id)
        assert len(story_hierarchy['succeeding_subsections']) == 3
        expected_title_order = [title_two, title_one, title_three]
        titles = [section['title'] for section in story_hierarchy['succeeding_subsections']]
        assert titles == expected_title_order

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,section_title,first_paragraph,second_paragraph', [
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
         'Chapter One', 'Once upon a time, there was a little test.', 'The end.')
    ])
    async def test_append_paragraph_to_section(self, user, story, section_title, first_paragraph, second_paragraph):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        section_id = await self.interface.append_inner_subsection(section_title, story_section_id)
        await self.interface.append_paragraph_to_section(section_id, first_paragraph)
        await self.interface.append_paragraph_to_section(section_id, second_paragraph)
        content = await self.interface.get_section_content(section_id)
        assert len(content) == 2
        expected_text_order = [first_paragraph, second_paragraph]
        text = [paragraph['text'] for paragraph in content]
        assert text == expected_text_order

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,section_title,first_text,second_text,third_text', [
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
         'Chapter One', 'The beginning.', 'The middle.', 'The end.')
    ])
    async def test_insert_paragraph_to_section(self, user, story, section_title, first_text, second_text, third_text):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        section_id = await self.interface.append_inner_subsection(section_title, story_section_id)
        await self.interface.append_paragraph_to_section(section_id, second_text)
        await self.interface.insert_paragraph_into_section_at_index(section_id, 0, first_text)
        await self.interface.insert_paragraph_into_section_at_index(section_id, 2, third_text)
        content = await self.interface.get_section_content(section_id)
        assert len(content) == 3
        expected_text_order = [first_text, second_text, third_text]
        text = [paragraph['text'] for paragraph in content]
        assert text == expected_text_order
