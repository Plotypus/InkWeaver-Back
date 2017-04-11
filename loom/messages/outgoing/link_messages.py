from .outgoing_message import StoryBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, link_id: ObjectId, alias_id: ObjectId):
        super().__init__(uuid, message_id, 'link_created')
        self.link_id = link_id
        self.alias_id = alias_id

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, link_id: ObjectId):
        super().__init__(uuid, message_id, 'link_deleted')
        self.link_id = link_id
