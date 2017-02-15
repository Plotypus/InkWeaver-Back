from .outgoing_message import OutgoingMessage
from ..message import auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWikiOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'wiki_title',
        'wiki_id',
        'segment_id',
        'users',
        'summary',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def wiki_title(self) -> str: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    @auto_getattr
    def users(self) -> list: pass

    @auto_getattr
    def summary(self) -> str: pass

    
###########################################################################
#
# Add Messages
#
###########################################################################
class AddSegmentOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'segment_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    
class AddTemplateHeadingOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
class AddPageOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'page_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    
class AddHeadingOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class EditSegmentOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
class EditTemplateHeadingOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
class EditPageOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
class EditHeadingOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    
###########################################################################
#
# Get Messages
#
###########################################################################
class GetWikiInformationOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'wiki_title',
        'segment_id',
        'users',
        'summary',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def wiki_title(self) -> str: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    @auto_getattr
    def users(self) -> list: pass

    @auto_getattr
    def summary(self) -> str: pass

    
class GetWikiHierarchyOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'hierarchy',
        'link_table',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def hierarchy(self) -> dict: pass

    @auto_getattr
    def link_table(self) -> list: pass

    
class GetWikiSegmentHierarchyOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'hierarchy',
        'link_table',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def hierarchy(self) -> dict: pass

    @auto_getattr
    def link_table(self) -> list: pass

    
class GetWikiSegmentOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'title',
        'segments',
        'pages',
        'template_headings',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def segments(self) -> list: pass

    @auto_getattr
    def pages(self) -> list: pass

    @auto_getattr
    def template_headings(self) -> list: pass

    
class GetWikiPageOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'title',
        'aliases',
        'references',
        'headings',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def aliases(self) -> dict: pass

    @auto_getattr
    def references(self) -> list: pass

    @auto_getattr
    def headings(self) -> list: pass

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteWikiOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass

    
class DeleteSegmentOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass

    
class DeleteTemplateHeadingOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass

    
class DeletePageOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass

    
class DeleteHeadingOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass

    
class DeleteAliasOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass
