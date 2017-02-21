from .incoming_message import IncomingMessage


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_user_preferences(self.message_id)


class GetUserStoriesIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_user_stories(self.message_id)


class GetUserWikisIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
    ]

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

    def dispatch(self):
        return self._dispatcher.set_user_name(self.message_id, self.name)


class SetUserEmailIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'email',
    ]

    def dispatch(self):
        return self._dispatcher.set_user_email(self.message_id, self.email)


class SetUserBioIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'bio',
    ]

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

    def dispatch(self):
        return self._dispatcher.user_login(self.message_id, self.username, self.password)
