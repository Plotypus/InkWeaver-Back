from .outgoing_message import UnicastMessage


###########################################################################
#
# Story Messages
#
###########################################################################
class SubscribeToStoryOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class UnsubscribeFromStoryOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


###########################################################################
#
# Wiki Messages
#
###########################################################################
class SubscribeToWikiOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class UnsubscribeFromWikiOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
