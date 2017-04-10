from .outgoing_message import StoryBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, alias_id: ObjectId, new_name: str):
        super().__init__(uuid, message_id, 'alias_updated')
        self.alias_id = alias_id
        self.new_name = new_name
