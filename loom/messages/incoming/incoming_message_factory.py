from .link_messages import *
from .alias_messages import *
from .statistics_messages import *
from .story_messages import *
from .subscription_messages import *
from .user_messages import *
from .wiki_messages import *

import re

APPROVED_MESSAGES = {
    # Sign out
    'sign_out':                        UserSignOutIncomingMessage,
    
    # User Information
    'get_user_preferences':            GetUserPreferencesIncomingMessage,
    'get_user_stories_and_wikis':      GetUserStoriesAndWikisIncomingMessage,
    'set_user_name':                   SetUserNameIncomingMessage,
    'set_user_email':                  SetUserEmailIncomingMessage,
    'set_user_bio':                    SetUserBioIncomingMessage,
    'set_user_story_position_context': SetUserStoryPositionContextIncomingMessage,

    # Stories
    'create_story':                    CreateStoryIncomingMessage,
    'add_preceding_subsection':        AddPrecedingSubsectionIncomingMessage,
    'add_inner_subsection':            AddInnerSubsectionIncomingMessage,
    'add_succeeding_subsection':       AddSucceedingSubsectionIncomingMessage,
    'add_paragraph':                   AddParagraphIncomingMessage,
    'add_bookmark':                    AddBookmarkIncomingMessage,
    'edit_story':                      EditStoryIncomingMessage,
    'edit_paragraph':                  EditParagraphIncomingMessage,
    'edit_section_title':              EditSectionTitleIncomingMessage,
    'edit_bookmark':                   EditBookmarkIncomingMessage,
    'set_note':                        SetNoteIncomingMessage,
    'get_story_information':           GetStoryInformationIncomingMessage,
    'get_story_bookmarks':             GetStoryBookmarksIncomingMessage,
    'get_story_hierarchy':             GetStoryHierarchyIncomingMessage,
    'get_section_hierarchy':           GetSectionHierarchyIncomingMessage,
    'get_section_content':             GetSectionContentIncomingMessage,
    'delete_story':                    DeleteStoryIncomingMessage,
    'delete_section':                  DeleteSectionIncomingMessage,
    'delete_paragraph':                DeleteParagraphIncomingMessage,
    'delete_note':                     DeleteNoteIncomingMessage,
    'delete_bookmark':                 DeleteBookmarkIncomingMessage,
    'move_subsection_as_preceding':    MoveSubsectionAsPrecedingIncomingMessage,
    'move_subsection_as_inner':        MoveSubsectionAsInnerIncomingMessage,
    'move_subsection_as_succeeding':   MoveSubsectionAsSucceedingIncomingMessage,

    # Wikis
    'create_wiki':                     CreateWikiIncomingMessage,
    'add_segment':                     AddSegmentIncomingMessage,
    'add_template_heading':            AddTemplateHeadingIncomingMessage,
    'add_page':                        AddPageIncomingMessage,
    'add_heading':                     AddHeadingIncomingMessage,
    'edit_wiki':                       EditWikiIncomingMessage,
    'edit_segment':                    EditSegmentIncomingMessage,
    'edit_template_heading':           EditTemplateHeadingIncomingMessage,
    'edit_page':                       EditPageIncomingMessage,
    'edit_heading':                    EditHeadingIncomingMessage,
    'get_wiki_information':            GetWikiInformationIncomingMessage,
    'get_wiki_alias_list':             GetWikiAliasListIncomingMessage,
    'get_wiki_hierarchy':              GetWikiHierarchyIncomingMessage,
    'get_wiki_segment_hierarchy':      GetWikiSegmentHierarchyIncomingMessage,
    'get_wiki_segment':                GetWikiSegmentIncomingMessage,
    'get_wiki_page':                   GetWikiPageIncomingMessage,
    'delete_wiki':                     DeleteWikiIncomingMessage,
    'delete_segment':                  DeleteSegmentIncomingMessage,
    'delete_template_heading':         DeleteTemplateHeadingIncomingMessage,
    'delete_page':                     DeletePageIncomingMessage,
    'delete_heading':                  DeleteHeadingIncomingMessage,
    'move_segment':                    MoveSegmentIncomingMessage,
    'move_template_heading':           MoveTemplateHeadingIncomingMessage,
    'move_page':                       MovePageIncomingMessage,
    'move_heading':                    MoveHeadingIncomingMessage,

    # Links
    'delete_link':                     DeleteLinkIncomingMessage,

    # Passive Links
    'approve_passive_link':            ApprovePassiveLinkMessage,
    'reject_passive_link':             RejectPassiveLinkMessage,

    # Aliases
    'delete_alias':                    DeleteAliasIncomingMessage,
    'change_alias_name':               ChangeAliasNameIncomingMessage,

    # Statistics
    'get_story_statistics':            GetStoryStatisticsIncomingMessage,
    'get_section_statistics':          GetSectionStatisticsIncomingMessage,
    'get_paragraph_statistics':        GetParagraphStatisticsIncomingMessage,
    'get_page_frequencies':            GetPageFrequenciesIncomingMessage,

    # Subscriptions
    'subscribe_to_story':              SubscribeToStoryIncomingMessage,
    'unsubscribe_from_story':          UnsubscribeFromStoryIncomingMessage,
    'subscribe_to_wiki':               SubscribeToWikiIncomingMessage,
    'unsubscribe_from_wiki':           UnsubscribeFromWikiIncomingMessage,

    # Collaborative
    'add_story_collaborator':          AddStoryCollaboratorIncomingMessage,
    'remove_story_collaborator':       RemoveStoryCollaboratorIncomingMessage,
    'add_wiki_collaborator':           AddWikiCollaboratorIncomingMessage,
    'remove_wiki_collaborator':        RemoveWikiCollaboratorIncomingMessage,
}


class IncomingMessageFactory:
    def __init__(self):
        self._approved_messages = APPROVED_MESSAGES.copy()

    @property
    def approved_messages(self):
        return self._approved_messages

    def build_message(self, dispatcher, action: str, message: dict, additional_fields: dict):
        message_builder = self.approved_messages.get(action)
        if message_builder is not None:
            message_object = self._build_message(message_builder, message, additional_fields)
            message_object.set_dispatcher(dispatcher)
            return message_object
        raise ValueError(f"no such action: {action}")

    @staticmethod
    def _build_message(message_builder, message: dict, additional_fields: dict):
        message_object = message_builder()
        try:
            message_object.set_values_from_message(message)
        except TypeError as e:
            error_msg = e.args[0]
            if 'Missing fields' in error_msg:
                # Missing fields come back in the form: ['field 1', 'field 2', ...]
                error_fields = re.search(r'\[(.*?)\]', error_msg).group(1)
                # Replace single quotes around each field and split into a list
                missing_fields = error_fields.replace("'", '').split(', ')
                # Try to fulfill missing fields using the additional fields.
                for missing_field in missing_fields:
                    field = additional_fields.get(missing_field)
                    # Check to see if the missing field is supplied in the additional fields.
                    if field is not None:
                        message[missing_field] = field
                    # If the field is not, we won't find it and can raise the error again.
                    else:
                        raise
                # All fields are satisfied, this won't raise an exception.
                message_object.set_values_from_message(message)
                return message_object
            raise
        else:
            return message_object
