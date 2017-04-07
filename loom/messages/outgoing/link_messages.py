from .outgoing_message import StoryBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, link_id: ObjectId, section_id: ObjectId,
                 paragraph_id: ObjectId, name: str, page_id: ObjectId):
        super().__init__(uuid, message_id, 'link_created')
        self.link_id = link_id
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.name = name
        self.page_id = page_id


class CreatePassiveLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, passive_link_id: ObjectId, section_id: ObjectId,
                 paragraph_id: ObjectId, name: str, page_id: ObjectId):
        super().__init__(uuid, message_id, 'passive_link_created')
        self.passive_link_id = passive_link_id
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.name = name
        self.page_id = page_id

    
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

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, link_id: ObjectId):
        super().__init__(uuid, message_id, 'link_deleted')
        self.link_id = link_id


class DeletePassiveLinkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, passive_link_id: ObjectId):
        super().__init__(uuid, message_id, 'passive_link_deleted')
        self.passive_link_id = passive_link_id
