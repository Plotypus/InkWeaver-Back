from .outgoing_message import UnicastMessage, MulticastMessage, WikiBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWikiOutgoingMessage(MulticastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, wiki_title: str, wiki_id: ObjectId, segment_id: ObjectId,
                 users: list, summary: str):
        super().__init__(uuid, message_id, 'wiki_created')
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
class AddSegmentOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, segment_id: ObjectId, title: str, parent_id: ObjectId):
        super().__init__(uuid, message_id, 'segment_added')
        self.segment_id = segment_id
        self.title = title
        self.parent_id = parent_id

    
class AddTemplateHeadingOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, title: str, segment_id: ObjectId):
        super().__init__(uuid, message_id, 'template_heading_added')
        self.title = title
        self.segment_id = segment_id

    
class AddPageOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, page_id: ObjectId, title: str, parent_id: ObjectId):
        super().__init__(uuid, message_id, 'page_added')
        self.page_id = page_id
        self.title = title
        self.parent_id = parent_id

    
class AddHeadingOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, title: str, page_id: ObjectId, index=None):
        super().__init__(uuid, message_id, 'heading_added')
        self.title = title
        self.page_id = page_id
        self.index = index

    
###########################################################################
#
# Edit Messages
#
###########################################################################
class EditWikiOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, wiki_id: ObjectId, update: dict):
        super().__init__(uuid, message_id, 'wiki_updated')
        self.wiki_id = wiki_id
        self.update = update


class EditSegmentOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, segment_id: ObjectId, update: dict):
        super().__init__(uuid, message_id, 'segment_updated')
        self.segment_id = segment_id
        self.update = update

    
class EditTemplateHeadingOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, segment_id: ObjectId, template_heading_title: str, update: dict):
        super().__init__(uuid, message_id, 'template_heading_updated')
        self.segment_id = segment_id
        self.template_heading_title = template_heading_title
        self.update = update

    
class EditPageOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, page_id: ObjectId, update: dict):
        super().__init__(uuid, message_id, 'page_updated')
        self.page_id = page_id
        self.update = update

    
class EditHeadingOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, page_id: ObjectId, heading_title: str, update: dict):
        super().__init__(uuid, message_id, 'heading_updated')
        self.page_id = page_id
        self.heading_title = heading_title
        self.update = update

    
###########################################################################
#
# Get Messages
#
###########################################################################
class GetWikiInformationOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, wiki_title: str, segment_id: ObjectId, users: list,
                 summary: str):
        super().__init__(uuid, message_id, 'got_wiki_information')
        self.wiki_title = wiki_title
        self.segment_id = segment_id
        self.users = users
        self.summary = summary


class GetWikiAliasListOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, alias_list: list):
        super().__init__(uuid, message_id, 'got_wiki_alias_list')
        self.alias_list = alias_list

    
class GetWikiHierarchyOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, hierarchy: dict):
        super().__init__(uuid, message_id, 'got_wiki_hierarchy')
        self.hierarchy = hierarchy

    
class GetWikiSegmentHierarchyOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, hierarchy: dict):
        super().__init__(uuid, message_id, 'got_wiki_segment_hierarchy')
        self.hierarchy = hierarchy
    
    
class GetWikiSegmentOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, title: str, segments: list, pages: list,
                 template_headings: list):
        super().__init__(uuid, message_id, 'got_wiki_segment')
        self.title = title
        self.segments = segments
        self.pages = pages
        self.template_headings = template_headings

    
class GetWikiPageOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, title: str, aliases: dict, references: list, headings: list):
        super().__init__(uuid, message_id, 'got_wiki_page')
        self.title = title
        self.aliases = aliases
        self.references = references
        self.headings = headings

    
###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteWikiOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, wiki_id: ObjectId):
        super().__init__(uuid, message_id, 'wiki_deleted')
        self.wiki_id = wiki_id

    
class DeleteSegmentOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, segment_id: ObjectId):
        super().__init__(uuid, message_id, 'segment_deleted')
        self.segment_id = segment_id
    
    
class DeleteTemplateHeadingOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, segment_id: ObjectId, template_heading_title: str):
        super().__init__(uuid, message_id, 'template_heading_deleted')
        self.segment_id = segment_id
        self.template_heading_title = template_heading_title

    
class DeletePageOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, page_id: ObjectId):
        super().__init__(uuid, message_id, 'page_deleted')
        self.page_id = page_id

    
class DeleteHeadingOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, page_id: ObjectId, heading_title: str):
        super().__init__(uuid, message_id, 'heading_deleted')
        self.page_id = page_id
        self.heading_title = heading_title

    
class DeleteAliasOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, alias_id: ObjectId):
        super().__init__(uuid, message_id, 'alias_deleted')
        self.alias_id = alias_id


###########################################################################
#
# Move Messages
#
###########################################################################
class MoveSegmentOutGoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, segment_id: ObjectId, to_parent_id: ObjectId, to_index: int):
        super().__init__(uuid, message_id, 'segment_moved')
        self.segment_id = segment_id
        self.to_parent_id = to_parent_id
        self.to_index = to_index


class MovePageOutgoingMessage(WikiBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, page_id: ObjectId, to_parent_id: ObjectId, to_index: int):
        super().__init__(uuid, message_id, 'page_moved')
        self.page_id = page_id
        self.to_parent_id = to_parent_id
        self.to_index = to_index
