from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreference(Message):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        self._dispatcher.get_user_preferences(self.message_id)


class GetUserStories(Message):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        self._dispatcher.get_user_stories(self.message_id)


class GetUserWikis(Message):
    _required_fields = [
        'message_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    def dispatch(self):
        self._dispatcher.get_user_wikis(self.message_id)
