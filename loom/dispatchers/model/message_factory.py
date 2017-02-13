from ..LAWProtocolDispatcher import LAWProtocolDispatcher

from .story_messages import AddSucceedingSubsection


class MessageFactory:
    @staticmethod
    def build_message(dispatcher: LAWProtocolDispatcher, action: str, message: dict):
        if action == 'add_succeeding_subsection':
            return AddSucceedingSubsection(dispatcher, message)
