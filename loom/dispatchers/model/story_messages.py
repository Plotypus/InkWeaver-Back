from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStory(Message):
    _required_fields = [
        'message_id',
        'title',
        'wiki_id',
        'summary',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    @auto_getattr
    def summary(self) -> str: pass


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsection(Message):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def parent_id(self) -> ObjectId: pass

    @auto_getattr
    def index(self) -> int: pass


class AddInnerSubsection(Message):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def parent_id(self) -> ObjectId: pass

    @auto_getattr
    def index(self) -> int: pass


class AddSucceedingSubsection(Message):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def parent_id(self) -> ObjectId: pass

    @auto_getattr
    def index(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.add_succeeding_subsection(self.message_id, self.title, self.parent_id, self.index)


class AddParagraph(Message):
    _required_fields = [
        'message_id',
        'section_id'
        'text',
    ]
    _optional_fields = [
        'succeeding_paragraph_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def text(self) -> str: pass

    @auto_getattr
    def succeeding_paragraph_id(self) -> ObjectId: pass


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditParagraph(Message):
    _required_fields = [
        'message_id',
        'section_id',
        'update',
        'paragraph_id'
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def update(self) -> dict: pass

    @auto_getattr
    def paragraph_id(self) -> ObjectId: pass


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformation(Message):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass


class GetStoryHierarchy(Message):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass


class GetSectionHierarchy(Message):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass


class GetSectionContent(Message):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStory(Message):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass


class DeleteSection(Message):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass


class DeleteParagraph(Message):
    _required_fields = [
        'message_id',
        'paragraph_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def paragraph_id(self) -> ObjectId: pass
