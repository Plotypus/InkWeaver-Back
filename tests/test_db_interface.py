from loom.database.interfaces import MongoDBAsyncioInterface
from loom.serialize import decode_bson_to_string

import asyncio
import pytest

TEST_DB_NAME = 'test'
TEST_DB_HOST = 'localhost'
TEST_DB_PORT = 27017


class TestDBInterface:
    def setup(self):
        self.interface = MongoDBAsyncioInterface(TEST_DB_NAME, TEST_DB_HOST, TEST_DB_PORT)

    def teardown(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.interface.drop_database())
        event_loop.close()

    @pytest.mark.asyncio
    async def test_interface_meta(self):
        assert self.interface.host == TEST_DB_HOST
        assert self.interface.port == TEST_DB_PORT

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
    @pytest.mark.parametrize('user,new_password,new_user_name,new_email,new_bio,new_avatar', [
        (
            {
                'username': 'tmctest',
                'password': 'my gr3at p4ssw0rd',
                'name':     'Testy McTesterton',
                'email':    'tmctest@te.st',
            },
            'my n3w p4ssw0rd!',
            'Testesson T McTesterton',
            'tmctest123@te.st',
            'I like writing stories. Writing is fun.',
            'avatar placeholder',
        )
    ])
    async def test_user_updates(self, user, new_password, new_user_name, new_email, new_bio, new_avatar):
        user_id = await self.interface.create_user(**user)
        # Set new password.
        await self.interface.set_user_password(user_id, new_password)
        assert await self.interface.password_is_valid_for_username(user['username'], new_password)
        # Set new preferences.
        await self.interface.set_user_name(user_id, new_user_name)
        await self.interface.set_user_email(user_id, new_email)
        await self.interface.set_user_bio(user_id, new_bio)
        await self.interface.set_user_avatar(user_id, new_avatar)
        preferences = await self.interface.get_user_preferences(user_id)
        assert preferences['email'] == new_email
        assert preferences['bio'] == new_bio
        assert preferences['avatar'] == new_avatar

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
        await self.interface.add_preceding_subsection(section_title, story_section_id)
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
        await self.interface.add_preceding_subsection(title_one, story_section_id)
        await self.interface.add_preceding_subsection(title_two, story_section_id, 0)
        await self.interface.add_preceding_subsection(title_three, story_section_id, 2)
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
        await self.interface.add_inner_subsection(section_title, story_section_id)
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
        await self.interface.add_inner_subsection(title_one, story_section_id)
        await self.interface.add_inner_subsection(title_two, story_section_id, 0)
        await self.interface.add_inner_subsection(title_three, story_section_id, 2)
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
        await self.interface.add_succeeding_subsection(section_title, story_section_id)
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
        await self.interface.add_succeeding_subsection(title_one, story_section_id)
        await self.interface.add_succeeding_subsection(title_two, story_section_id, 0)
        await self.interface.add_succeeding_subsection(title_three, story_section_id, 2)
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
    async def test_add_paragraph(self, user, story, section_title, first_paragraph, second_paragraph):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        section_id = await self.interface.add_inner_subsection(section_title, story_section_id)
        await self.interface.add_paragraph(section_id, first_paragraph)
        await self.interface.add_paragraph(section_id, second_paragraph)
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
        section_id = await self.interface.add_inner_subsection(section_title, story_section_id)
        second_id = await self.interface.add_paragraph(section_id, second_text)
        await self.interface.add_paragraph(section_id, first_text, second_id)
        await self.interface.add_paragraph(section_id, third_text, None)
        content = await self.interface.get_section_content(section_id)
        assert len(content) == 3
        expected_text_order = [first_text, second_text, third_text]
        text = [paragraph['text'] for paragraph in content]
        assert text == expected_text_order

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
    async def test_edit_paragraph_in_section(self, user, story, section_title, first_paragraph, second_paragraph):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        story = await self.interface.get_story(story_id)
        story_section_id = story['section_id']
        section_id = await self.interface.add_inner_subsection(section_title, story_section_id)
        first_paragraph_id = await self.interface.add_paragraph(section_id, first_paragraph)
        second_paragraph_id = await self.interface.add_paragraph(section_id, second_paragraph)
        replacement_texts = ['Text 1', 'Text 2']
        await self.interface.set_paragraph_text(section_id, replacement_texts[0], first_paragraph_id)
        await self.interface.set_paragraph_text(section_id, replacement_texts[1], second_paragraph_id)
        content = await self.interface.get_section_content(section_id)
        text = [paragraph['text'] for paragraph in content]
        assert text == replacement_texts

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,wiki', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-wiki',
             'summary': 'This is a wiki for testing',
         })
    ])
    async def test_wiki_creation(self, user, wiki):
        user_id = await self.interface.create_user(**user)
        wiki_id = await self.interface.create_wiki(user_id, **wiki)
        assert wiki_id is not None
        user_wikis = await self.interface.get_user_wikis(user_id)
        wiki_summary = {
            'wiki_id': wiki_id,
            'title': wiki['title'],
            'access_level': 'owner',
        }
        assert wiki_summary in user_wikis
        db_wiki = await self.interface.get_wiki(wiki_id)
        assert db_wiki['title'] == wiki['title']
        assert db_wiki['summary'] == wiki['summary']
        assert db_wiki['segment_id'] is not None
        user_description = {
            'user_id': user_id,
            'name': user['name'],
            'access_level': 'owner',
        }
        assert user_description in db_wiki['users']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('title', [
        'Character'
    ])
    async def test_create_segment(self, title):
        segment_id = await self.interface.create_segment(title)
        hierarchy = await self.interface.get_segment_hierarchy(segment_id)
        assert hierarchy['title'] == title
        assert hierarchy['segment_id'] == segment_id
        assert hierarchy['segments'] == list()
        assert hierarchy['pages'] == list()
        assert hierarchy['links'] == dict()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,wiki', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-wiki',
             'summary': 'This is a wiki for testing',
         })
    ])
    async def test_get_wiki_hierarchy(self, user, wiki):
        user_id = await self.interface.create_user(**user)
        wiki_id = await self.interface.create_wiki(user_id, **wiki)
        db_wiki = await self.interface.get_wiki(wiki_id)
        segment_id = db_wiki['segment_id']
        wiki_hierarchy = await self.interface.get_wiki_hierarchy(wiki_id)
        segment_hierarchy = await self.interface.get_segment_hierarchy(segment_id)
        assert wiki_hierarchy == segment_hierarchy
        assert wiki_hierarchy['title'] == db_wiki['title']
        assert wiki_hierarchy['links'] == dict()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,wiki,segment_title', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-wiki',
             'summary': 'This is a wiki for testing',
         },
         'Character')
    ])
    async def test_add_child_segment(self, user, wiki, segment_title):
        user_id = await self.interface.create_user(**user)
        wiki_id = await self.interface.create_wiki(user_id, **wiki)
        db_wiki = await self.interface.get_wiki(wiki_id)
        wiki_segment_id = db_wiki['segment_id']
        segment_id = await self.interface.add_child_segment(segment_title, wiki_segment_id)
        assert segment_id is not None
        wiki_hierarchy = await self.interface.get_wiki_hierarchy(wiki_id)
        assert len(wiki_hierarchy['segments']) == 1
        segment_hierarchy = wiki_hierarchy['segments'][0]
        assert segment_hierarchy['title'] == segment_title
        assert segment_hierarchy['segment_id'] == segment_id
        assert segment_hierarchy['segments'] == list()
        assert segment_hierarchy['pages'] == list()

    @pytest.mark.asyncio
    @pytest.mark.parametrize('segment_title,heading_title', [
        ('Character', 'Background')
    ])
    async def test_add_template_heading(self, segment_title, heading_title):
        segment_id = await self.interface.create_segment(segment_title)
        await self.interface.add_template_heading(heading_title, segment_id)
        segment = await self.interface.get_segment(segment_id)
        assert len(segment['template_headings']) == 1
        template_heading = segment['template_headings'][0]
        assert template_heading['title'] == heading_title
        assert template_heading['text'] == ''

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,wiki,template_title,page_title', [
        ({
             'username': 'tmctest',
             'password': 'my gr3at p4ssw0rd',
             'name':     'Testy McTesterton',
             'email':    'tmctest@te.st',
         },
         {
             'title':   'test-wiki',
             'summary': 'This is a wiki for testing',
         },
         'History', 'Mars')
    ])
    async def test_create_page(self, user, wiki, template_title, page_title):
        user_id = await self.interface.create_user(**user)
        wiki_id = await self.interface.create_wiki(user_id, **wiki)
        db_wiki = await self.interface.get_wiki(wiki_id)
        segment_id = db_wiki['segment_id']
        await self.interface.add_template_heading(template_title, segment_id)
        page_id = await self.interface.create_page(page_title, segment_id)
        assert page_id is not None
        page = await self.interface.get_page(page_id)
        assert page['title'] == page_title
        assert len(page['headings']) == 1
        heading = page['headings'][0]
        assert heading['title'] == template_title
        assert heading['text'] == ''
        wiki_hierarchy = await self.interface.get_wiki_hierarchy(wiki_id)
        assert len(wiki_hierarchy['pages']) == 1
        hierarchy_page = wiki_hierarchy['pages'][0]
        assert hierarchy_page['title'] == page_title
        assert hierarchy_page['page_id'] == page_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize('segment_title,page_title,first_heading,second_heading,third_heading', [
        ('Character', 'John', 'Background', 'Motives', 'Family')
    ])
    async def test_add_heading(self, segment_title, page_title, first_heading, second_heading, third_heading):
        segment_id = await self.interface.create_segment(segment_title)
        page_id = await self.interface.create_page(page_title, segment_id)
        await self.interface.add_heading(second_heading, page_id)
        await self.interface.add_heading(first_heading, page_id, 0)
        await self.interface.add_heading(third_heading, page_id, 2)
        page = await self.interface.get_page(page_id)
        assert len(page['headings']) == 3
        expected_title_order = [first_heading, second_heading, third_heading]
        headings = page['headings']
        titles = [heading['title'] for heading in headings]
        contents = [heading['text'] for heading in headings]
        assert titles == expected_title_order
        assert contents == ['', '', '']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('old_title,new_title', [
        ('Character', 'Characters')
    ])
    async def test_set_segment_title(self, old_title, new_title):
        segment_id = await self.interface.create_segment(old_title)
        segment = await self.interface.get_segment(segment_id)
        assert segment['title'] == old_title
        await self.interface.set_segment_title(new_title, segment_id)
        segment = await self.interface.get_segment(segment_id)
        assert segment['title'] == new_title

    @pytest.mark.asyncio
    @pytest.mark.parametrize('segment_title,page_title,heading_titles', [
        ('Character', 'John', [
            'Background', 'Motives'
        ])
    ])
    async def test_set_heading_title(self, segment_title, page_title, heading_titles):
        segment_id = await self.interface.create_segment(segment_title)
        page_id = await self.interface.create_page(page_title, segment_id)
        for title in heading_titles:
            await self.interface.add_heading(title, page_id)
        new_titles = ['Family', 'Relationships']
        await self.interface.set_heading_title(heading_titles[0], new_titles[0], page_id)
        page = await self.interface.get_page(page_id)
        headings = page['headings']
        assert headings[0]['title'] == new_titles[0]
        assert headings[1]['title'] == heading_titles[1]
        await self.interface.set_heading_title(heading_titles[1], new_titles[1], page_id)
        page = await self.interface.get_page(page_id)
        headings = page['headings']
        assert headings[0]['title'] == new_titles[0]
        assert headings[1]['title'] == new_titles[1]

    @pytest.mark.asyncio
    @pytest.mark.parametrize('segment_title,page_title,headings', [
        ('Character', 'John', [
            {'title': 'Background', 'text': 'John is old.'},
            {'title': 'Motives', 'text': 'John likes food.'}
        ])
    ])
    async def test_set_heading_text(self, segment_title, page_title, headings):
        segment_id = await self.interface.create_segment(segment_title)
        page_id = await self.interface.create_page(page_title, segment_id)
        for heading in headings:
            title = heading['title']
            text = heading['text']
            await self.interface.add_heading(title, page_id)
            await self.interface.set_heading_text(title, text, page_id)
        page = await self.interface.get_page(page_id)
        db_headings = page['headings']
        assert db_headings == headings

    @pytest.mark.asyncio
    @pytest.mark.parametrize('user,story,section_title,paragraph,wiki,segment_name,page_name,link_name,new_link_name', [
        (
            {
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
            'Chapter One', 'Once upon a time, there was a little test.',
            {
                'title':   'test-wiki',
                'summary': 'This is a wiki for testing',
            },
            'Character', 'John Smith', 'Johnny Boy', 'Smithy'
        )
    ])
    async def test_links(self, user, story, section_title, paragraph, wiki, segment_name, page_name, link_name,
                         new_link_name):
        user_id = await self.interface.create_user(**user)
        story_id = await self.interface.create_story(user_id, **story)
        db_story = await self.interface.get_story(story_id)
        story_section_id = db_story['section_id']
        section_id = await self.interface.add_inner_subsection(section_title, story_section_id, index=None)
        paragraph_id = await self.interface.add_paragraph(section_id, paragraph, succeeding_paragraph_id=None)

        wiki_id = await self.interface.create_wiki(user_id, **wiki)
        db_wiki = await self.interface.get_wiki(wiki_id)
        wiki_segment_id = db_wiki['segment_id']
        segment_id = await self.interface.add_child_segment(segment_name, wiki_segment_id)
        page_id = await self.interface.create_page(page_name, segment_id)

        context = {
            'story_id': story_id,
            'section_id': section_id,
            'paragraph_id': paragraph_id,
            'text': None,
        }
        link_id = await self.interface.create_link(story_id, section_id, paragraph_id, link_name, page_id)
        assert link_id is not None
        link = await self.interface.get_link(link_id)
        assert link['context'] == context
        assert link['alias_id'] is not None
        assert link['page_id'] == page_id
        alias_id = link['alias_id']
        alias = await self.interface.get_alias(alias_id)
        assert alias['name'] == link_name
        assert alias['page_id'] == page_id
        assert len(alias['links']) == 1
        assert link_id in alias['links']

        page = await self.interface.get_page(page_id)
        assert len(page['aliases']) == 1
        assert page['aliases'][link_name] == alias_id
        hierarchy = await self.interface.get_wiki_hierarchy(wiki_id)
        assert len(hierarchy['links']) == 1
        link_info = {
            'name': link_name,
            'page_id': page_id,
        }
        assert hierarchy['links'][link_id] == link_info

        # Test alias name change.
        await self.interface.change_alias_name(alias_id, new_link_name)
        alias = await self.interface.get_alias(alias_id)
        assert alias['name'] == new_link_name

        # Insert link into paragraph text.
        text = "Four score and seven {} ago...".format(decode_bson_to_string(link_id))
        paragraph_id = await self.interface.add_paragraph(section_id, text, succeeding_paragraph_id=None)
        page = await self.interface.get_page(page_id)
        reference = {
            'link_id':      link_id,
            'story_id':     story_id,
            'section_id':   section_id,
            'paragraph_id': paragraph_id,
            'text':         text,
        }
        assert reference in page['references']

        # Remove link
        await self.interface.delete_link(link_id)
        page = await self.interface.get_page(page_id)
        assert reference not in page['references']
        alias = await self.interface.get_alias(alias_id)
        assert link_id not in alias['links']
        link = await self.interface.get_link(link_id)
        assert link is None
        hierarchy = await self.interface.get_wiki_hierarchy(wiki_id)
        assert hierarchy['links'] == {}
