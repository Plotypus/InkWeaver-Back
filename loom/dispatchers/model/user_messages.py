from .message import Message, auto_getattr


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferences(Message):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.get_user_preferences(self.message_id)


class GetUserStories(Message):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.get_user_stories(self.message_id)


class GetUserWikis(Message):
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
class SetUserName(Message):
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


class SetUserEmail(Message):
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


class SetUserBio(Message):
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
class UserLogin(Message):
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
