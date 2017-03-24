from .incoming_message import IncomingMessage
from .field_types import RequiredField


class UserSignOutIncomingMessage(IncomingMessage):
    def dispatch(self):
        # This dispatch function should never be called.
        raise NotImplementedError


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_user_preferences(self.uuid, self.message_id, self.user_id)


class GetUserStoriesAndWikisIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_user_stories_and_wikis(self.uuid, self.message_id, self.user_id)


###########################################################################
#
# Set Messages
#
###########################################################################
class SetUserNameIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()
        self.name = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_name(self.uuid, self.message_id, self.user_id, self.name)


class SetUserEmailIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()
        self.email = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_email(self.uuid, self.message_id, self.user_id, self.email)


class SetUserBioIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()
        self.bio = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_bio(self.uuid, self.message_id, self.user_id, self.bio)


class SetUserStoryPositionContextIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()
        self.story_id = RequiredField()
        self.position_context = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_user_story_position_context(self.uuid, self.message_id, self.user_id, self.story_id,
                                                                self.position_context)
