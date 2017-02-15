from .outgoing_message import OutgoingMessage
from ..message import auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'link_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def link_id(self) -> ObjectId: pass

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass
