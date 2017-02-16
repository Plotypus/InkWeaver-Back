from loom.dispatchers.messages.message import auto_getattr
from loom.dispatchers.messages.incoming.incoming_message import IncomingMessage

from bson import ObjectId


class AddHeadingWithTextIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'title',
        'text',
        'page_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def text(self) -> str: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.add_heading_with_text(self.message_id, self.title, self.text, self.page_id)


class AddTextToSectionIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'text',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def text(self) -> str: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.add_text_to_section(self.message_id, self.text, self.section_id)
