from .outgoing_message import OutgoingMessage

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryOutgoingMessage(OutgoingMessage):
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
class AddPrecedingSubsectionOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, section_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.section_id = section_id


class AddInnerSubsectionOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, section_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.section_id = section_id


class AddSucceedingSubsectionOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, section_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.section_id = section_id


class AddParagraphOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, paragraph_id: ObjectId):
        self.reply_to_id = reply_to_id
        self.paragraph_id = paragraph_id


class AddBookmarkOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditStoryOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


class EditParagraphOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


class EditSectionTitleOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


###########################################################################
#
# Set Messages
#
###########################################################################
class SetNoteOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformationOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, story_title: str, section_id: ObjectId, wiki_id: ObjectId, users: list):
        self.reply_to_id = reply_to_id
        self.story_title = story_title
        self.section_id = section_id
        self.wiki_id = wiki_id
        self.users = users


class GetStoryBookmarksOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, bookmarks: list):
        self.reply_to_id = reply_to_id
        self.bookmarks = bookmarks


class GetStoryHierarchyOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, hierarchy: dict):
        self.reply_to_id = reply_to_id
        self.hierarchy = hierarchy


class GetSectionHierarchyOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, hierarchy: dict):
        self.reply_to_id = reply_to_id
        self.hierarchy = hierarchy


class GetSectionContentOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, content: list):
        self.reply_to_id = reply_to_id
        self.content = content


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class DeleteSectionOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class DeleteParagraphOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event


class DeleteNoteOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
