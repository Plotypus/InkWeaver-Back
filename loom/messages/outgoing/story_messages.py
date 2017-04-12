from .outgoing_message import UnicastMessage, MulticastMessage, StoryBroadcastMessage

from bson import ObjectId
from uuid import UUID


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryOutgoingMessage(MulticastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, story_title: str, story_id: ObjectId, section_id: ObjectId,
                 wiki_id: ObjectId, users: list):
        super().__init__(uuid, message_id, 'story_created')
        self.story_title = story_title
        self.story_id = story_id
        self.section_id = section_id
        self.wiki_id = wiki_id
        self.users = users


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, title: str, parent_id: ObjectId,
                 index=None):
        super().__init__(uuid, message_id, 'preceding_subsection_added')
        self.section_id = section_id
        self.title = title
        self.parent_id = parent_id
        self.index = index


class AddInnerSubsectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, title: str, parent_id: ObjectId,
                 index=None):
        super().__init__(uuid, message_id, 'inner_subsection_added')
        self.section_id = section_id
        self.title = title
        self.parent_id = parent_id
        self.index = index


class AddSucceedingSubsectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, title: str, parent_id: ObjectId,
                 index=None):
        super().__init__(uuid, message_id, 'succeeding_subsection_added')
        self.section_id = section_id
        self.title = title
        self.parent_id = parent_id
        self.index = index


class AddParagraphOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, paragraph_id: ObjectId, section_id: ObjectId, text: str,
                 succeeding_paragraph_id=None):
        super().__init__(uuid, message_id, 'paragraph_added')
        self.paragraph_id = paragraph_id
        self.section_id = section_id
        self.text = text
        self.succeeding_paragraph_id = succeeding_paragraph_id


class AddBookmarkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, bookmark_id: ObjectId, story_id: ObjectId, section_id: ObjectId,
                 paragraph_id: ObjectId, name: str, index=None):
        super().__init__(uuid, message_id, 'bookmark_added')
        self.bookmark_id = bookmark_id
        self.story_id = story_id
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.name = name
        self.index = index


class AddStoryCollaboratorOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, user_id: ObjectId, name: str):
        super().__init__(uuid, message_id, 'story_collaborator_added')
        self.user_id = user_id
        self.name = name


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditStoryOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, story_id: ObjectId, update: dict):
        super().__init__(uuid, message_id, 'story_updated')
        self.story_id = story_id
        self.update = update


class EditParagraphOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, update: dict, paragraph_id: ObjectId):
        super().__init__(uuid, message_id, 'paragraph_updated')
        self.section_id = section_id
        self.update = update
        self.paragraph_id = paragraph_id


class EditSectionTitleOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, new_title: str):
        super().__init__(uuid, message_id, 'section_title_updated')
        self.section_id = section_id
        self.new_title = new_title


class EditBookmarkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, story_id: ObjectId, bookmark_id: ObjectId, update: dict):
        super().__init__(uuid, message_id, 'bookmark_updated')
        self.story_id = story_id
        self.bookmark_id = bookmark_id
        self.update = update


###########################################################################
#
# Set Messages
#
###########################################################################
class SetNoteOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, paragraph_id: ObjectId, note: str):
        super().__init__(uuid, message_id, 'note_updated')
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.note = note


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformationOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, story_title: str, section_id: ObjectId, wiki_id: ObjectId,
                 users: list):
        super().__init__(uuid, message_id, 'got_story_information')
        self.story_title = story_title
        self.section_id = section_id
        self.wiki_id = wiki_id
        self.users = users


class GetStoryBookmarksOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, bookmarks: list):
        super().__init__(uuid, message_id, 'got_story_bookmarks')
        self.bookmarks = bookmarks


class GetStoryHierarchyOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, hierarchy: dict):
        super().__init__(uuid, message_id, 'got_story_hierarchy')
        self.hierarchy = hierarchy


class GetSectionHierarchyOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, hierarchy: dict):
        super().__init__(uuid, message_id, 'got_section_hierarchy')
        self.hierarchy = hierarchy


class GetSectionContentOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, content: list):
        super().__init__(uuid, message_id, 'got_section_content')
        self.content = content


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, story_id: ObjectId):
        super().__init__(uuid, message_id, 'story_deleted')
        self.story_id = story_id


class DeleteSectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId):
        super().__init__(uuid, message_id, 'section_deleted')
        self.section_id = section_id


class DeleteParagraphOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, paragraph_id: ObjectId):
        super().__init__(uuid, message_id, 'paragraph_deleted')
        self.section_id = section_id
        self.paragraph_id = paragraph_id


class DeleteNoteOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, paragraph_id: ObjectId):
        super().__init__(uuid, message_id, 'note_deleted')
        self.section_id = section_id
        self.paragraph_id = paragraph_id


class DeleteBookmarkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, bookmark_id: ObjectId):
        super().__init__(uuid, message_id, 'bookmark_deleted')
        self.bookmark_id = bookmark_id


class RemoveStoryCollaboratorOutoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, user_id: ObjectId):
        super().__init__(uuid, message_id, 'story_collaborator_removed')
        self.user_id = user_id


###########################################################################
#
# Move Messages
#
###########################################################################
class MoveSubsectionAsPrecedingOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, to_parent_id: ObjectId, to_index: int):
        super().__init__(uuid, message_id, 'subsection_moved_as_preceding')
        self.section_id = section_id
        self.to_parent_id = to_parent_id
        self.to_index = to_index


class MoveSubsectionAsInnerOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, to_parent_id: ObjectId, to_index: int):
        super().__init__(uuid, message_id, 'subsection_moved_as_inner')
        self.section_id = section_id
        self.to_parent_id = to_parent_id
        self.to_index = to_index


class MoveSubsectionAsSucceedingOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, section_id: ObjectId, to_parent_id: ObjectId, to_index: int):
        super().__init__(uuid, message_id, 'subsection_moved_as_succeeding')
        self.section_id = section_id
        self.to_parent_id = to_parent_id
        self.to_index = to_index
