from .incoming_message import IncomingMessage
from .field_types import RequiredField


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()

    def dispatch(self):
        return self._dispatcher.get_user_preferences(self.message_id)


class GetUserStoriesIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()

    def dispatch(self):
        return self._dispatcher.get_user_stories(self.message_id)


class GetUserWikisIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()

    def dispatch(self):
        return self._dispatcher.get_user_wikis(self.message_id)


###########################################################################
#
# Set Messages
#
###########################################################################
class SetUserNameIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.name = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_name(self.message_id, self.name)


class SetUserEmailIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.email = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_email(self.message_id, self.email)


class SetUserBioIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.bio = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_bio(self.message_id, self.bio)


class SetUserStoryPositionContextIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()
        self.position_context = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_story_position_context(self.story_id, self.position_context)


###########################################################################
#
# Login Messages
#
###########################################################################
class UserLoginIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.username = RequiredField()
        self.password = RequiredField()

    def dispatch(self):
        return self._dispatcher.user_login(self.message_id, self.username, self.password)
