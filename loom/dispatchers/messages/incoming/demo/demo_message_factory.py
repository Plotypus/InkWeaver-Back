from .demo_messages import *

from loom.dispatchers.messages import IncomingMessageFactory

DEMO_MESSAGES = {
    'add_heading_with_text': AddHeadingWithTextIncomingMessage,
    'add_text_to_section':   AddTextToSectionIncomingMessage,
}


class DemoIncomingMessageFactory(IncomingMessageFactory):
    def __init__(self):
        super().__init__()
        self.approved_messages.update(DEMO_MESSAGES.copy())
