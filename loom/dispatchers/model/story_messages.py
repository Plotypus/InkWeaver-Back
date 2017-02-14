from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryMessage(Message):
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

    def dispatch(self):
        return self._dispatcher.create_story(self.message_id, self.title, self.wiki_id, self.summary)


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsectionMessage(Message):
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
        return self._dispatcher.add_preceding_subsection(self.message_id, self.title, self.parent_id, self.index)


class AddInnerSubsectionMessage(Message):
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
        return self._dispatcher.add_inner_subsection(self.message_id, self.title, self.parent_id, self.index)


class AddSucceedingSubsectionMessage(Message):
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


class AddParagraphMessage(Message):
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

    def dispatch(self):
        return self._dispatcher.add_paragraph(self.message_id, self.section_id, self.text, self.succeeding_paragraph_id)


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditParagraphMessage(Message):
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

    def dispatch(self):
        return self._dispatcher.edit_paragraph(self.message_id, self.section_id, self.update, self.paragraph_id)


class EditSectionTitleMessage(Message):
    _required_fields = [
        'message_id',
        'section_id',
        'new_title',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def new_title(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.edit_section_title(self.message_id, self.section_id, self.new_title)

###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformationMessage(Message):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_story_information(self.message_id, self.story_id)


class GetStoryHierarchyMessage(Message):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_story_hierarchy(self.message_id, self.story_id)


class GetSectionHierarchyMessage(Message):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_section_hierarchy(self.message_id, self.section_id)


class GetSectionContentMessage(Message):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_section_content(self.message_id, self.section_id)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryMessage(Message):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_story(self.message_id, self.story_id)


class DeleteSectionMessage(Message):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_section(self.message_id, self.section_id)


class DeleteParagraphMessage(Message):
    _required_fields = [
        'message_id',
        'section_id',
        'paragraph_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def paragraph_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_paragraph(self.message_id, self.section_id, self.paragraph_id)
