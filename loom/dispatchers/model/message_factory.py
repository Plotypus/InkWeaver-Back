from .story_messages import AddSucceedingSubsection


class MessageFactory:
    @staticmethod
    def build_message(action: str, message: dict):
        if action == 'add_succeeding_subsection':
            return AddSucceedingSubsection(message)
