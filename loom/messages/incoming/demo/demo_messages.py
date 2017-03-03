from ..incoming_message import IncomingMessage, RequiredField


class AddHeadingWithTextIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.title = RequiredField()
        self.text = RequiredField()
        self.page_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.add_heading_with_text(self.uuid, self.message_id, self.title, self.text, self.page_id)


class AddTextToSectionIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.text = RequiredField()
        self.section_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.add_text_to_section(self.uuid, self.message_id, self.text, self.section_id)
