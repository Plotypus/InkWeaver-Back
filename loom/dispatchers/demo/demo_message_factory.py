from .demo_messages import *

from loom.dispatchers.model import MessageFactory

DEMO_MESSAGES = {
    'add_heading_with_text': AddHeadingWithTextMessage,
    'add_text_to_section':   AddTextToSectionMessage,
}


class DemoMessageFactory(MessageFactory):
    def __init__(self):
        super().__init__()
        self.approved_messages.update(DEMO_MESSAGES.copy())
