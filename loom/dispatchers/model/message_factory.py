from .link_messages import *
from .story_messages import *
from .user_messages import *
from .wiki_messages import *

APPROVED_MESSAGES = {
    # User Information
    'get_user_preferences':       GetUserPreferencesMessage,
    'get_user_stories':           GetUserStoriesMessage,
    'get_user_wikis':             GetUserWikisMessage,
    'set_user_name':              SetUserNameMessage,
    'set_user_email':             SetUserEmailMessage,
    'set_user_bio':               SetUserBioMessage,
    'user_login':                 UserLoginMessage,

    # Stories
    'create_story':               CreateStoryMessage,
    'add_preceding_subsection':   AddPrecedingSubsectionMessage,
    'add_inner_subsection':       AddInnerSubsectionMessage,
    'add_succeeding_subsection':  AddSucceedingSubsectionMessage,
    'add_paragraph':              AddParagraphMessage,
    'edit_paragraph':             EditParagraphMessage,
    'edit_section_title':         EditSectionTitleMessage,
    'get_story_information':      GetStoryInformationMessage,
    'get_story_hierarchy':        GetStoryHierarchyMessage,
    'get_section_hierarchy':      GetSectionHierarchyMessage,
    'get_section_content':        GetSectionContentMessage,
    'delete_story':               DeleteStoryMessage,
    'delete_section':             DeleteSectionMessage,
    'delete_paragraph':           DeleteParagraphMessage,

    # Wikis
    'create_wiki':                CreateWikiMessage,
    'add_segment':                AddSegmentMessage,
    'add_template_heading':       AddTemplateHeadingMessage,
    'add_page':                   AddPageMessage,
    'add_heading':                AddHeadingMessage,
    'edit_segment':               EditSegmentMessage,
    'edit_template_heading':      EditTemplateHeadingMessage,
    'edit_page':                  EditPageMessage,
    'edit_heading':               EditHeadingMessage,
    'get_wiki_information':       GetWikiInformationMessage,
    'get_wiki_hierarchy':         GetWikiHierarchyMessage,
    'get_wiki_segment_hierarchy': GetWikiSegmentHierarchyMessage,
    'get_wiki_segment':           GetWikiSegmentMessage,
    'get_wiki_page':              GetWikiPageMessage,
    'delete_wiki':                DeleteWikiMessage,
    'delete_segment':             DeleteSegmentMessage,
    'delete_template_heading':    DeleteTemplateHeadingMessage,
    'delete_page':                DeletePageMessage,
    'delete_heading':             DeleteHeadingMessage,

    # Links
    'create_link':                CreateLinkMessage,
    'delete_link':                DeleteLinkMessage,

    # Aliases
    'delete_alias':               DeleteAliasMessage,
    'change_alias_name':          ChangeAliasNameMessage,
}

class MessageFactory:
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
