from .outgoing_message import OutgoingMessage
from ..message import auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'story_title',
        'story_id',
        'section_id',
        'wiki_id',
        'users',
        'summary',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def story_title(self) -> str: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    @auto_getattr
    def users(self) -> list: pass

    @auto_getattr
    def summary(self) -> str: pass


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsectionOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'section_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass


class AddInnerSubsectionOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'section_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass


class AddSucceedingSubsectionOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'section_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass


class AddParagraphOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'paragraph_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def paragraph_id(self) -> ObjectId: pass


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditParagraphOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass


class EditSectionTitleOutgoingMessage(OutgoingMessage):
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
class GetStoryInformationOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'story_title',
        'section_id',
        'wiki_id',
        'users',
        'summary',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def story_title(self) -> str: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    @auto_getattr
    def users(self) -> list: pass

    @auto_getattr
    def summary(self) -> str: pass


class GetStoryHierarchyOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'hierarchy',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def hierarchy(self) -> dict: pass


class GetSectionHierarchyOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'hierarchy',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def hierarchy(self) -> dict: pass


class GetSectionContentOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'content',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def content(self) -> list: pass


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass


class DeleteSectionOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass


class DeleteParagraphOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass

