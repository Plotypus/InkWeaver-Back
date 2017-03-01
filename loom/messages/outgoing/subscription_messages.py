from .outgoing_message import OutgoingMessage


###########################################################################
#
# Story Messages
#
###########################################################################
class SubscribeToStoryOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class UnsubscribeFromStoryOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


###########################################################################
#
# Wiki Messages
#
###########################################################################
class SubscribeToWikiOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class UnsubscribeFromWikiOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
