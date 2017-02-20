from .outgoing_message import OutgoingMessage
from ..message import auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWikiOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, wiki_title: str, wiki_id: ObjectId, segment_id: ObjectId, users: list,
                 summary: str):
        self.reply_to_id = reply_to_id
        self.wiki_title = wiki_title
        self.wiki_id = wiki_id
        self.segment_id = segment_id
        self.users = users
        self.summary = summary

    
###########################################################################
#
# Add Messages
#
###########################################################################
class AddSegmentOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, segment_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.segment_id = segment_id

    
class AddTemplateHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
class AddPageOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, page_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.page_id = page_id

    
class AddHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class EditWikiOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


class EditSegmentOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
class EditTemplateHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
class EditPageOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
class EditHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id

    
###########################################################################
#
# Get Messages
#
###########################################################################
class GetWikiInformationOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, wiki_title: str, segment_id: ObjectId, users: list,
                 summary: str):
        self.reply_to_id = reply_to_id
        self.wiki_title = wiki_title
        self.segment_id = segment_id
        self.users = users
        self.summary = summary

    
class GetWikiHierarchyOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, hierarchy: dict, link_table: list):
        self.reply_to_id = reply_to_id
        self.hierarchy = hierarchy
        self.link_table = link_table

    
class GetWikiSegmentHierarchyOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, hierarchy: dict, link_table: list):
        self.reply_to_id = reply_to_id
        self.hierarchy = hierarchy
        self.link_table = link_table
    
    
class GetWikiSegmentOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, title: str, segments: list, pages: list, template_headings: list):
        self.reply_to_id = reply_to_id
        self.title = title
        self.segments = segments
        self.pages = pages
        self.template_headings = template_headings

    
class GetWikiPageOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, title: str, aliases: dict, references: list, headings: list):
        self.reply_to_id = reply_to_id
        self.title = title
        self.aliases = aliases
        self.references = references
        self.headings = headings

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteWikiOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event

    
class DeleteSegmentOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
    
    
class DeleteTemplateHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event

    
class DeletePageOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event

    
class DeleteHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event

    
class DeleteAliasOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
