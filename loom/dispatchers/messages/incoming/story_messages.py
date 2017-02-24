from .incoming_message import IncomingMessage

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'title',
        'wiki_id',
        'summary',
    ]

    def dispatch(self):
        return self._dispatcher.create_story(self.message_id, self.title, self.wiki_id, self.summary)


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsectionIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    def dispatch(self):
        return self._dispatcher.add_preceding_subsection(self.message_id, self.title, self.parent_id, self.index)


class AddInnerSubsectionIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    def dispatch(self):
        return self._dispatcher.add_inner_subsection(self.message_id, self.title, self.parent_id, self.index)


class AddSucceedingSubsectionIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    def dispatch(self):
        return self._dispatcher.add_succeeding_subsection(self.message_id, self.title, self.parent_id, self.index)


class AddParagraphIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'text',
    ]
    _optional_fields = [
        'succeeding_paragraph_id',
    ]

    def dispatch(self):
        return self._dispatcher.add_paragraph(self.message_id, self.section_id, self.text, self.succeeding_paragraph_id)


class AddBookmarkIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'name',
        'story_id',
        'section_id',
        'paragraph_id',
    ]
    _optional_fields = [
        'index'
    ]

    def dispatch(self):
        return self._dispatcher.add_bookmark(self.message_id, self.name, self.story_id, self.section_id,
                                             self.paragraph_id, self.index)


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditStoryIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
        'update',
    ]

    def dispatch(self):
        return self._dispatcher.edit_story(self.message_id, self.story_id, self.update)


class EditParagraphIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'update',
        'paragraph_id'
    ]

    def dispatch(self):
        return self._dispatcher.edit_paragraph(self.message_id, self.section_id, self.update, self.paragraph_id)


class EditSectionTitleIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'new_title',
    ]

    def dispatch(self):
        return self._dispatcher.edit_section_title(self.message_id, self.section_id, self.new_title)


###########################################################################
#
# Set Messages
#
###########################################################################
class SetNoteIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'paragraph_id',
        'note',
    ]

    def dispatch(self):
        return self._dispatcher.set_note(self.message_id, self.section_id, self.paragraph_id, self.note)


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformationIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_story_information(self.message_id, self.story_id)


class GetStoryBookmarksIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_story_bookmarks(self.message_id, self.story_id)


class GetStoryHierarchyIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_story_hierarchy(self.message_id, self.story_id)


class GetSectionHierarchyIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_section_hierarchy(self.message_id, self.section_id)


class GetSectionContentIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_section_content(self.message_id, self.section_id)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    def dispatch(self):
        return self._dispatcher.delete_story(self.message_id, self.story_id)


class DeleteSectionIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    def dispatch(self):
        return self._dispatcher.delete_section(self.message_id, self.section_id)


class DeleteParagraphIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'paragraph_id',
    ]

    def dispatch(self):
        return self._dispatcher.delete_paragraph(self.message_id, self.section_id, self.paragraph_id)


class DeleteNoteIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'paragraph_id',
    ]

    def dispatch(self):
        return self._dispatcher.delete_note(self.message_id, self.section_id, self.paragraph_id)
