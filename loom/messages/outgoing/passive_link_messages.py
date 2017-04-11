from .outgoing_message import StoryBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Create Messages
#
###########################################################################
class CreatePassiveLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, passive_link_id: ObjectId, alias_id: ObjectId):
        super().__init__(uuid, message_id, 'passive_link_created')
        self.passive_link_id = passive_link_id
        self.alias_id = alias_id


###########################################################################
#
# Edit Messages
#
###########################################################################
class RejectPassiveLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, passive_link_id: ObjectId):
        super().__init__(uuid, message_id, 'passive_link_rejected')
        self.passive_link_id = passive_link_id


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeletePassiveLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, passive_link_id: ObjectId):
        super().__init__(uuid, message_id, 'passive_link_deleted')
        self.passive_link_id = passive_link_id
