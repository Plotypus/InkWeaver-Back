from .incoming_message import IncomingMessage
from .field_types import RequiredField, OptionalField


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStoryIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.user_id = RequiredField()
        self.title = RequiredField()
        self.wiki_id = RequiredField()
        self.summary = RequiredField()

    def dispatch(self):
        return self._dispatcher.create_story(self.uuid, self.message_id, self.user_id, self.title, self.wiki_id,
                                             self.summary)


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsectionIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.title = RequiredField()
        self.parent_id = RequiredField()
        self.index = OptionalField()

    def dispatch(self):
        return self._dispatcher.add_preceding_subsection(self.uuid, self.message_id, self.title, self.parent_id,
                                                         self.index)


class AddInnerSubsectionIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.title = RequiredField()
        self.parent_id = RequiredField()
        self.index = OptionalField()

    def dispatch(self):
        return self._dispatcher.add_inner_subsection(self.uuid, self.message_id, self.title, self.parent_id, self.index)


class AddSucceedingSubsectionIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.title = RequiredField()
        self.parent_id = RequiredField()
        self.index = OptionalField()

    def dispatch(self):
        return self._dispatcher.add_succeeding_subsection(self.uuid, self.message_id, self.title, self.parent_id,
                                                          self.index)


class AddParagraphIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.wiki_id = RequiredField()
        self.section_id = RequiredField()
        self.text = RequiredField()
        self.succeeding_paragraph_id = OptionalField()

    def dispatch(self):
        return self._dispatcher.add_paragraph(self.uuid, self.message_id, self.wiki_id, self.section_id, self.text,
                                              self.succeeding_paragraph_id)


class AddBookmarkIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.name = RequiredField()
        self.story_id = RequiredField()
        self.section_id = RequiredField()
        self.paragraph_id = RequiredField()
        self.index = OptionalField()

    def dispatch(self):
        return self._dispatcher.add_bookmark(self.uuid, self.message_id, self.name, self.story_id, self.section_id,
                                             self.paragraph_id, self.index)


class AddCollaboratorIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()
        self.username = RequiredField()

    def dispatch(self):
        return self._dispatcher.add_collaborator(self.uuid, self.message_id, self.story_id, self.username)


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditStoryIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()
        self.update = RequiredField()

    def dispatch(self):
        return self._dispatcher.edit_story(self.uuid, self.message_id, self.story_id, self.update)


class EditParagraphIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.wiki_id = RequiredField()
        self.section_id = RequiredField()
        self.update = RequiredField()
        self.paragraph_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.edit_paragraph(self.uuid, self.message_id, self.wiki_id, self.section_id, self.update,
                                               self.paragraph_id)


class EditSectionTitleIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.new_title = RequiredField()

    def dispatch(self):
        return self._dispatcher.edit_section_title(self.uuid, self.message_id, self.section_id, self.new_title)


class EditBookmarkIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()
        self.bookmark_id = RequiredField()
        self.update = RequiredField()

    def dispatch(self):
        return self._dispatcher.edit_bookmark(self.uuid, self.message_id, self.story_id, self.bookmark_id, self.update)


###########################################################################
#
# Set Messages
#
###########################################################################
class SetNoteIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.paragraph_id = RequiredField()
        self.note = RequiredField()

    def dispatch(self):
        return self._dispatcher.set_note(self.uuid, self.message_id, self.section_id, self.paragraph_id, self.note)


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryInformationIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_story_information(self.uuid, self.message_id, self.story_id)


class GetStoryBookmarksIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_story_bookmarks(self.uuid, self.message_id, self.story_id)


class GetStoryHierarchyIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_story_hierarchy(self.uuid, self.message_id, self.story_id)


class GetSectionHierarchyIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_section_hierarchy(self.uuid, self.message_id, self.section_id)


class GetSectionContentIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.get_section_content(self.uuid, self.message_id, self.section_id)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteStoryIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_story(self.uuid, self.message_id, self.story_id)


class DeleteSectionIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()
        self.section_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_section(self.uuid, self.message_id, self.section_id)


class DeleteParagraphIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.paragraph_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_paragraph(self.uuid, self.message_id, self.section_id, self.paragraph_id)


class DeleteNoteIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.paragraph_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_note(self.uuid, self.message_id, self.section_id, self.paragraph_id)


class DeleteBookmarkIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.bookmark_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_bookmark(self.uuid, self.message_id, self.bookmark_id)


class RemoveCollaboratorIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.story_id = RequiredField()
        self.user_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.remove_collaborator(self.uuid, self.message_id, self.story_id, self.user_id)


###########################################################################
#
# Move Messages
#
###########################################################################
class MoveSubsectionAsPrecedingIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.to_parent_id = RequiredField()
        self.to_index = RequiredField()

    def dispatch(self):
        return self._dispatcher.move_subsection_as_preceding(self.uuid, self.message_id, self.section_id,
                                                             self.to_parent_id, self.to_index)


class MoveSubsectionAsInnerIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.to_parent_id = RequiredField()
        self.to_index = RequiredField()

    def dispatch(self):
        return self._dispatcher.move_subsection_as_inner(self.uuid, self.message_id, self.section_id, self.to_parent_id,
                                                         self.to_index)


class MoveSubsectionAsSucceedingIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.section_id = RequiredField()
        self.to_parent_id = RequiredField()
        self.to_index = RequiredField()

    def dispatch(self):
        return self._dispatcher.move_subsection_as_succeeding(self.uuid, self.message_id, self.section_id,
                                                              self.to_parent_id, self.to_index)
