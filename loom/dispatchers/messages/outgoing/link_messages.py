from .outgoing_message import OutgoingMessage

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, link_id: ObjectId, story_id: ObjectId, section_id: ObjectId, paragraph_id: ObjectId,
                 name: str, page_id: ObjectId):
        self.event = event
        self.link_id = link_id
        self.story_id = story_id
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.name = name
        self.page_id = page_id

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, alias_id: ObjectId, new_name: str):
        self.event = event
        self.alias_id = alias_id
        self.new_name = new_name

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, link_id: ObjectId):
        self.event = event
        self.link_id = link_id
