from .incoming_message import IncomingMessage
from ..message import auto_getattr


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.get_user_preferences(self.message_id)


class GetUserStoriesIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.get_user_stories(self.message_id)


class GetUserWikisIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.get_user_wikis(self.message_id)


###########################################################################
#
# Set Messages
#
###########################################################################
class SetUserNameIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'name',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def name(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.set_user_name(self.message_id, self.name)


class SetUserEmailIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'email',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def email(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.set_user_email(self.message_id, self.email)


class SetUserBioIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'bio',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def bio(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.set_user_bio(self.message_id, self.bio)


###########################################################################
#
# Login Messages
#
###########################################################################
class UserLoginIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'username',
        'password',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def username(self) -> str: pass

    @auto_getattr
    def password(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.user_login(self.message_id, self.username, self.password)
