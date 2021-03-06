from .outgoing_message import WikiBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateAliasOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, alias_id: ObjectId, page_id: ObjectId, alias_name: str):
        super().__init__(uuid, message_id, 'alias_created')
        self.alias_id = alias_id
        self.page_id = page_id
        self.alias_name = alias_name


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteAliasOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, alias_id: ObjectId):
        super().__init__(uuid, message_id, 'alias_deleted')
        self.alias_id = alias_id


###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, alias_id: ObjectId, new_name: str):
        super().__init__(uuid, message_id, 'alias_updated')
        self.alias_id = alias_id
        self.new_name = new_name
