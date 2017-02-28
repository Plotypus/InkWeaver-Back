from .outgoing_message import UnicastMessage, StoryBroadcastMessage

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, story_title: str, story_id: ObjectId, section_id: ObjectId, wiki_id: ObjectId,
                 users: list):
        self.reply_to_id = reply_to_id
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
    def __init__(self, event: str, section_id: ObjectId, title: str, parent_id: ObjectId, index=None):
        self.event = event
        self.section_id = section_id
        self.title = title
        self.parent_id = parent_id
        self.index = index


class AddInnerSubsectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, title: str, parent_id: ObjectId, index=None):
        self.event = event
        self.section_id = section_id
        self.title = title
        self.parent_id = parent_id
        self.index = index


class AddSucceedingSubsectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, title: str, parent_id: ObjectId, index=None):
        self.event = event
        self.section_id = section_id
        self.title = title
        self.parent_id = parent_id
        self.index = index


class AddParagraphOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, paragraph_id: ObjectId, section_id: ObjectId, text: str,
                 succeeding_paragraph_id=None):
        self.event = event
        self.paragraph_id = paragraph_id
        self.section_id = section_id
        self.text = text
        self.succeeding_paragraph_id = succeeding_paragraph_id


class AddBookmarkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, bookmark_id: ObjectId, story_id: ObjectId, section_id: ObjectId,
                 paragraph_id: ObjectId, index=None):
        self.event = event
        self.bookmark_id = bookmark_id
        self.story_id = story_id
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.index = index


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditStoryOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, story_id: ObjectId, update: dict):
        self.event = event
        self.story_id = story_id
        self.update = update


class EditParagraphOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, update: dict, paragraph_id: ObjectId):
        self.event = event
        self.section_id = section_id
        self.update = update
        self.paragraph_id = paragraph_id


class EditSectionTitleOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, new_title: str):
        self.event = event
        self.section_id = section_id
        self.new_title = new_title


class EditBookmarkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, story_id: ObjectId, bookmark_id: ObjectId, update: dict):
        self.event = event
        self.story_id = story_id
        self.bookmark_id = bookmark_id
        self.update = update


###########################################################################
#
# Set Messages
#
###########################################################################
class SetNoteOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, paragraph_id: ObjectId, note: str):
        self.event = event
        self.section_id = section_id
        self.paragraph_id = paragraph_id
        self.note = note


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformationOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, story_title: str, section_id: ObjectId, wiki_id: ObjectId, users: list):
        self.reply_to_id = reply_to_id
        self.story_title = story_title
        self.section_id = section_id
        self.wiki_id = wiki_id
        self.users = users


class GetStoryBookmarksOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, bookmarks: list):
        self.reply_to_id = reply_to_id
        self.bookmarks = bookmarks


class GetStoryHierarchyOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, hierarchy: dict):
        self.reply_to_id = reply_to_id
        self.hierarchy = hierarchy


class GetSectionHierarchyOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, hierarchy: dict):
        self.reply_to_id = reply_to_id
        self.hierarchy = hierarchy


class GetSectionContentOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, content: list):
        self.reply_to_id = reply_to_id
        self.content = content


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, story_id: ObjectId):
        self.event = event
        self.story_id = story_id


class DeleteSectionOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId):
        self.event = event
        self.section_id = section_id


class DeleteParagraphOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, paragraph_id: ObjectId):
        self.event = event
        self.section_id = section_id
        self.paragraph_id = paragraph_id


class DeleteNoteOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, section_id: ObjectId, paragraph_id: ObjectId):
        self.event = event
        self.section_id = section_id
        self.paragraph_id = paragraph_id


class DeleteBookmarkOutgoingMessage(StoryBroadcastMessage):
    def __init__(self, event: str, bookmark_id: ObjectId):
        self.event = event
        self.bookmark_id = bookmark_id
