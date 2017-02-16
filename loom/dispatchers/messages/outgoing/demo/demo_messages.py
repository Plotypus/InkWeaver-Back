from .. import OutgoingMessage


class AddTextToSectionOutgoingMessage(OutgoingMessage):
    def __init__(self, paragraph_ids: dict):
        self.paragraph_ids = paragraph_ids
