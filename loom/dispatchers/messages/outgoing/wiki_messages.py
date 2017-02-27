from .outgoing_message import OutgoingMessage

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
    def __init__(self, event: str, segment_id: ObjectId, title: str, parent_id: ObjectId):
        self.event = event
        self.segment_id = segment_id
        self.title = title
        self.parent_id = parent_id

    
class AddTemplateHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, title: str, segment_id: ObjectId):
        self.event = event
        self.title = title
        self.segment_id = segment_id

    
class AddPageOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, page_id: ObjectId, title: str, parent_id: ObjectId):
        self.event = event
        self.page_id = page_id
        self.title = title
        self.parent_id = parent_id

    
class AddHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, title: str, page_id: ObjectId, index=None):
        self.event = event
        self.title = title
        self.page_id = page_id
        self.index = index

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class EditWikiOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, wiki_id: ObjectId, update: dict):
        self.event = event
        self.wiki_id = wiki_id
        self.update = update


class EditSegmentOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, segment_id: ObjectId, update: dict):
        self.event = event
        self.segment_id = segment_id
        self.update = update

    
class EditTemplateHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, segment_id: ObjectId, template_heading_title: str, update: dict):
        self.event = event
        self.segment_id = segment_id
        self.template_heading_title = template_heading_title
        self.update = update

    
class EditPageOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, page_id: ObjectId, update: dict):
        self.event = event
        self.page_id = page_id
        self.update = update

    
class EditHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, page_id: ObjectId, heading_title: str, update: dict):
        self.event = event
        self.page_id = page_id
        self.heading_title = heading_title
        self.update = update

    
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
    def __init__(self, event: str, wiki_id: ObjectId):
        self.event = event
        self.wiki_id = wiki_id

    
class DeleteSegmentOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, segment_id: ObjectId):
        self.event = event
        self.segment_id = segment_id
    
    
class DeleteTemplateHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, segment_id: ObjectId, template_heading_title: str):
        self.event = event
        self.segment_id = segment_id
        self.template_heading_title = template_heading_title

    
class DeletePageOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, page_id: ObjectId):
        self.event = event
        self.page_id = page_id

    
class DeleteHeadingOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, page_id: ObjectId, heading_title: str):
        self.event = event
        self.page_id = page_id
        self.heading_title = heading_title

    
class DeleteAliasOutgoingMessage(OutgoingMessage):
    def __init__(self, event: str, alias_id: ObjectId):
        self.event = event
        self.alias_id = alias_id
