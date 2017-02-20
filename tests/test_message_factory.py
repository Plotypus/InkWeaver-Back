from loom.dispatchers.messages.incoming import *
from loom.dispatchers.messages import IncomingMessageFactory

import pytest

from bson import ObjectId


class TestMessageFactory:
    @pytest.fixture(scope="module")
    def message_factory(self):
        message_factory = IncomingMessageFactory()
        yield message_factory

    @pytest.fixture(scope="module")
    def dispatcher(self):
        yield None

    @pytest.mark.parametrize('action', [
        '123abc'
    ])
    def test_invalid_action(self, message_factory, dispatcher, action):
        with pytest.raises(ValueError):
            message_factory.build_message(dispatcher, action, {})

    @pytest.mark.parametrize('action, msg_extra, msg_good, expected', [
        (
                'get_user_preferences',
                {'message_id': 1, 'extra': 123},
                {'message_id': 199},
                GetUserPreferencesIncomingMessage
        ),
        (
                'get_user_stories',
                {'message_id': 1, 'extra': 123},
                {'message_id': 502},
                GetUserStoriesIncomingMessage
        ),
        (
                'get_user_wikis',
                {'message_id': 1, 'extra': 123},
                {'message_id': 3},
                GetUserWikisIncomingMessage
        ),
        (
                'set_user_name',
                {'message_id': 1, 'name': 'john', 'extra': 123},
                {'message_id': 199, 'name': 'mary'},
                SetUserNameIncomingMessage
        ),
        (
                'set_user_email',
                {'message_id': 1, 'email': 'blah', 'extra': 123},
                {'message_id': 83, 'email': 'blah'},
                SetUserEmailIncomingMessage
        ),
        (
                'set_user_bio',
                {'message_id': 1, 'bio': 'blah', 'extra': 123},
                {'message_id': 123, 'bio': 'blah'},
                SetUserBioIncomingMessage
        ),
        (
                'user_login',
                {'message_id': 1, 'username': 'user', 'password': 'abc', 'extra': 123},
                {'message_id': 132, 'username': 'user', 'password': 'abc'},
                UserLoginIncomingMessage
        ),
        (
                'create_story',
                {'message_id': 1, 'title': 'park', 'wiki_id': ObjectId(), 'summary': 'meh', 'extra': 123},
                {'message_id': 143, 'title': 'bench', 'wiki_id': ObjectId(), 'summary': 'woo'},
                CreateStoryIncomingMessage
        ),
        (
                'add_preceding_subsection',
                {'message_id': 23, 'title': 'prologue', 'parent_id': ObjectId(), 'index': 0, 'extra': 123},
                {'message_id': 233, 'title': 'prologue', 'parent_id': ObjectId(), 'index': 3},
                AddPrecedingSubsectionIncomingMessage
        ),
        (
                'add_inner_subsection',
                {'message_id': 23, 'title': 'chapter 1', 'parent_id': ObjectId(), 'index': 0, 'extra': 123},
                {'message_id': 233, 'title': 'chapter 3', 'parent_id': ObjectId(), 'index': 3},
                AddInnerSubsectionIncomingMessage
        ),
        (
                'add_succeeding_subsection',
                {'message_id': 23, 'title': 'epilogue', 'parent_id': ObjectId(), 'index': 0, 'extra': 123},
                {'message_id': 233, 'title': 'epilogue', 'parent_id': ObjectId(), 'index': 3},
                AddSucceedingSubsectionIncomingMessage
        ),
        (
                'add_paragraph',
                {'message_id': 32, 'section_id': ObjectId(), 'text': '', 'succeeding_paragraph_id': ObjectId(), 'a': 1},
                {'message_id': 32, 'section_id': ObjectId(), 'text': 'blah.', 'succeeding_paragraph_id': ObjectId()},
                AddParagraphIncomingMessage
        ),
        (
                'edit_story',
                {'message_id': 1, 'story_id': ObjectId(), 'update': {'update_type': 'set_title', 'title': 'heroes'},
                 'extra': 'abc'},
                {'message_id': 13, 'story_id': ObjectId(),
                 'update': {'update_type': 'wrong but okay here', 'title': 'heroes'}},
                EditStoryIncomingMessage
        ),
        (
                'edit_paragraph',
                {'message_id': 1, 'section_id': ObjectId(), 'update': {'update_type': 'set_text', 'text': 'The castle'},
                 'paragraph_id': ObjectId(), 'extra': ObjectId()},
                {'message_id': 11, 'section_id': ObjectId(), 'update': {'update_type': 'set_text', 'text': 'heroes'},
                 'paragraph_id': ObjectId()},
                EditParagraphIncomingMessage
        ),
        (
                'edit_section_title',
                {'message_id': 12, 'section_id': ObjectId(), 'new_title': 'Lord of the Kings', 'extra': 123},
                {'message_id': 89, 'section_id': ObjectId(), 'new_title': 'Reign of the Cows!'},
                EditSectionTitleIncomingMessage
        ),
        (
                'get_story_information',
                {'message_id': 32, 'story_id': ObjectId(), 'extra': True},
                {'message_id': 12, 'story_id': ObjectId()},
                GetStoryInformationIncomingMessage
        ),
        (
                'get_story_hierarchy',
                {'message_id': 32, 'story_id': ObjectId(), 'extra': True},
                {'message_id': 12, 'story_id': ObjectId()},
                GetStoryHierarchyIncomingMessage
        ),
        (
                'get_section_hierarchy',
                {'message_id': 9, 'section_id': ObjectId(), 'story_id': 'this is extra'},
                {'message_id': 1, 'section_id': ObjectId()},
                GetSectionHierarchyIncomingMessage
        ),
        (
                'get_section_content',
                {'message_id': 123, 'section_id': ObjectId(), 'extra': False},
                {'message_id': 987, 'section_id': ObjectId()},
                GetSectionContentIncomingMessage
        ),
        (
                'delete_story',
                {'message_id': 1, 'story_id': ObjectId(), 'all': True},
                {'message_id': 2, 'story_id': ObjectId()},
                DeleteStoryIncomingMessage
        ),
        (
                'delete_section',
                {'message_id': 123, 'section_id': ObjectId(), 'extra': 2},
                {'message_id': 987, 'section_id': ObjectId()},
                DeleteSectionIncomingMessage
        ),
        (
                'delete_paragraph',
                {'message_id': 123, 'section_id': ObjectId(), 'paragraph_id': ObjectId(), 'extra': 1, 'dbl': 2},
                {'message_id': 987, 'section_id': ObjectId(), 'paragraph_id': ObjectId()},
                DeleteParagraphIncomingMessage
        ),
    ])
    def test_message_fields(self, message_factory, dispatcher, action, msg_extra, msg_good, expected):
        with pytest.raises(TypeError) as errinfo:
            message_factory.build_message(dispatcher, action, {})
        assert 'Missing fields' in str(errinfo.value)
        with pytest.raises(TypeError) as errinfo:
            message_factory.build_message(dispatcher, action, msg_extra)
        assert 'Unsupported fields' in str(errinfo.value)
        msg_object = message_factory.build_message(dispatcher, action, msg_good)
        assert isinstance(msg_object, expected)
        actual = vars(msg_object)
        actual.pop('_dispatcher')
        assert vars(msg_object) == msg_good

    @pytest.mark.parametrize('action, msg', [
        (
                'add_preceding_subsection',
                {'message_id': 23, 'title': 'prologue', 'parent_id': ObjectId()},
        ),
        (
                'add_inner_subsection',
                {'message_id': 23, 'title': 'chapter 1', 'parent_id': ObjectId()},
        ),
        (
                'add_succeeding_subsection',
                {'message_id': 23, 'title': 'epilogue', 'parent_id': ObjectId()}
        ),
        (
                'add_paragraph',
                {'message_id': 32, 'section_id': ObjectId(), 'text': ''},
        ),
    ])
    def test_optional_fields(self, message_factory, dispatcher, action, msg):
        msg_object = message_factory.build_message(dispatcher, action, msg)
        actual = vars(msg_object)
        for optional in msg_object._optional_fields:
            assert actual[optional] is None
