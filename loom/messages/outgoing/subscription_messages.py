from .outgoing_message import UnicastMessage

from uuid import UUID


###########################################################################
#
# Story Messages
#
###########################################################################
class SubscribeToStoryOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'subscribed_to_story')


class UnsubscribeFromStoryOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'unsubscribed_from_story')


###########################################################################
#
# Wiki Messages
#
###########################################################################
class SubscribeToWikiOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'subscribed_to_wiki')


class UnsubscribeFromWikiOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'unsubscribed_from_wiki')
