from .link_messages import *
from .story_messages import *
from .user_messages import *
from .wiki_messages import *

APPROVED_MESSAGES = {
    # User Information
    'get_user_preferences':            GetUserPreferencesIncomingMessage,
    'get_user_stories':                GetUserStoriesIncomingMessage,
    'get_user_wikis':                  GetUserWikisIncomingMessage,
    'set_user_name':                   SetUserNameIncomingMessage,
    'set_user_email':                  SetUserEmailIncomingMessage,
    'set_user_bio':                    SetUserBioIncomingMessage,
    'set_user_story_position_context': SetUserStoryPositionContextIncomingMessage,
    'user_login':                      UserLoginIncomingMessage,

    # Stories
    'create_story':                    CreateStoryIncomingMessage,
    'add_preceding_subsection':        AddPrecedingSubsectionIncomingMessage,
    'add_inner_subsection':            AddInnerSubsectionIncomingMessage,
    'add_succeeding_subsection':       AddSucceedingSubsectionIncomingMessage,
    'add_paragraph':                   AddParagraphIncomingMessage,
    'edit_story':                      EditStoryIncomingMessage,
    'edit_paragraph':                  EditParagraphIncomingMessage,
    'edit_section_title':              EditSectionTitleIncomingMessage,
    'set_note':                        SetNoteIncomingMessage,
    'get_story_information':           GetStoryInformationIncomingMessage,
    'get_story_hierarchy':             GetStoryHierarchyIncomingMessage,
    'get_section_hierarchy':           GetSectionHierarchyIncomingMessage,
    'get_section_content':             GetSectionContentIncomingMessage,
    'delete_story':                    DeleteStoryIncomingMessage,
    'delete_section':                  DeleteSectionIncomingMessage,
    'delete_paragraph':                DeleteParagraphIncomingMessage,
    'delete_note':                     DeleteNoteIncomingMessage,

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
    'get_wiki_hierarchy':              GetWikiHierarchyIncomingMessage,
    'get_wiki_segment_hierarchy':      GetWikiSegmentHierarchyIncomingMessage,
    'get_wiki_segment':                GetWikiSegmentIncomingMessage,
    'get_wiki_page':                   GetWikiPageIncomingMessage,
    'delete_wiki':                     DeleteWikiIncomingMessage,
    'delete_segment':                  DeleteSegmentIncomingMessage,
    'delete_template_heading':         DeleteTemplateHeadingIncomingMessage,
    'delete_page':                     DeletePageIncomingMessage,
    'delete_heading':                  DeleteHeadingIncomingMessage,

    # Links
    'create_link':                     CreateLinkIncomingMessage,
    'delete_link':                     DeleteLinkIncomingMessage,

    # Aliases
    'delete_alias':                    DeleteAliasIncomingMessage,
    'change_alias_name':               ChangeAliasNameIncomingMessage,
}


class IncomingMessageFactory:
    def __init__(self):
        self._approved_messages = APPROVED_MESSAGES.copy()

    @property
    def approved_messages(self):
        return self._approved_messages

    def build_message(self, dispatcher, action: str, message: dict):
        message_builder = self.approved_messages.get(action)
        if message_builder is not None:
            message_object = message_builder(message)
            message_object.set_dispatcher(dispatcher)
            return message_object
        raise ValueError
