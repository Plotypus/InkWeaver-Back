from ..incoming_message import IncomingMessage

from bson import ObjectId


class AddHeadingWithTextIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'title',
        'text',
        'page_id',
    ]

    def dispatch(self):
        return self._dispatcher.add_heading_with_text(self.message_id, self.title, self.text, self.page_id)


class AddTextToSectionIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'text',
        'section_id',
    ]

    def dispatch(self):
        return self._dispatcher.add_text_to_section(self.message_id, self.text, self.section_id)
