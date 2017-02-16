from .outgoing_message import OutgoingMessage
from ..message import auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, link_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.link_id = link_id

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
