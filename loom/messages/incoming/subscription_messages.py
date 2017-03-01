from .incoming_message import SubscriptionIncomingMessage
from .field_types import RequiredField


###########################################################################
#
# Story Messages
#
###########################################################################
class SubscribeToStoryIncomingMessage(SubscriptionIncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()


class UnsubscribeFromStoryIncomingMessage(SubscriptionIncomingMessage):
    def __init__(self):
        super().__init__()


###########################################################################
#
# Wiki Messages
#
###########################################################################
class SubscribeToWikiIncomingMessage(SubscriptionIncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()


class UnsubscribeFromWikiIncomingMessage(SubscriptionIncomingMessage):
    def __init__(self):
        super().__init__()
