from loom.dispatchers.messages.incoming import *
from loom.dispatchers.messages import IncomingMessageFactory

import pytest


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

    @pytest.mark.parametrize('action, msg_missing, msg_extra, msg_good, expected', [
        (
                'get_user_preferences',
                {},
                {'message_id': 1, 'extra': 123},
                {'message_id': 199},
                GetUserPreferencesIncomingMessage
        ),
        (
                'get_user_stories',
                {},
                {'message_id': 1, 'extra': 123},
                {'message_id': 502},
                GetUserStoriesIncomingMessage
        ),
        (
                'get_user_wikis',
                {},
                {'message_id': 1, 'extra': 123},
                {'message_id': 3},
                GetUserWikisIncomingMessage
        ),
        (
                'set_user_name',
                {},
                {'message_id': 1, 'name': 'john', 'extra': 123},
                {'message_id': 199, 'name': 'mary'},
                SetUserNameIncomingMessage
        ),
        (
                'set_user_email',
                {},
                {'message_id': 1, 'email': 'blah', 'extra': 123},
                {'message_id': 83, 'email': 'blah'},
                SetUserEmailIncomingMessage
        ),
        (
                'set_user_bio',
                {},
                {'message_id': 1, 'bio': 'blah', 'extra': 123},
                {'message_id': 123, 'bio': 'blah'},
                SetUserBioIncomingMessage
        ),
        (
                'user_login',
                {},
                {'message_id': 1, 'username': 'user', 'password': 'abc', 'extra': 123},
                {'message_id': 132, 'username': 'user', 'password': 'abc'},
                UserLoginIncomingMessage
        ),

    ])
    def test_message_fields(self, message_factory, dispatcher, action, msg_missing, msg_extra, msg_good, expected):
        with pytest.raises(TypeError) as errinfo:
            message_factory.build_message(dispatcher, action, msg_missing)
        assert 'Missing fields' in str(errinfo.value)
        with pytest.raises(TypeError) as errinfo:
            message_factory.build_message(dispatcher, action, msg_extra)
        assert 'Unsupported fields' in str(errinfo.value)
        msg_object = message_factory.build_message(dispatcher, action, msg_good)
        assert isinstance(msg_object, expected)
        actual = vars(msg_object)
        actual.pop('_dispatcher')
        assert vars(msg_object) == msg_good
