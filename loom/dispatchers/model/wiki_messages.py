from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWiki(Message):
    _required_fields = [
        'message_id',
        'title',
        'summary',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def summary(self) -> str: pass

    def dispatch(self):
        self._dispatcher.create_wiki(self.message_id, self.title, self.summary)
