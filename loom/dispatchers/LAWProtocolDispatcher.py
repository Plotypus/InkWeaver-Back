import loom.serialize

from .messages import IncomingMessageFactory
from .messages.outgoing import *
from loom.database.interfaces import AbstractDBInterface

from decorator import decorator
from typing import Dict

JSON = Dict


class LAWError(Exception):
    def __init__(self, message=None):
        if message is None:
            message = "no information given"
        self.message = message

    def __str__(self):
        return '{}: {}'.format(type(self).__name__, self.message)


class LAWUnimplementedError(LAWError):
    """
    Raised when a connection attempts an unimplemented task.
    """
    pass


class LAWBadArgumentsError(LAWError):
    """
    Raised when necessary arguments were omitted or formatted incorrectly.
    """
    pass


class LAWNotLoggedInError(LAWError):
    """
    Raised when an action is requested without having logged in.
    """
    pass

############################################################
#
# LAWProtocolDispatcher Decorators
#
############################################################


@decorator
def requires_login(func, *args, **kwargs):
    self = args[0]
    if self.user_id is None:
        raise LAWNotLoggedInError
    return func(*args, **kwargs)


class LAWProtocolDispatcher:
    def __init__(self, interface: AbstractDBInterface, user_id=None):
        self._db_interface = interface
        self._user_id = user_id
        self._message_factory = IncomingMessageFactory()

    @classmethod
    def encode_json(cls, data):
        return loom.serialize.encode_bson_to_string(data)

    @property
    def db_interface(self):
        return self._db_interface

    @property
    def user_id(self):
        return self._user_id

    def set_user_id(self, new_user_id):
        self._user_id = new_user_id

    @property
    def message_factory(self):
        return self._message_factory

    def format_json(self, base_message, **kwargs):
        for key, value in kwargs.items():
            base_message[key] = value
        return base_message

    def format_failure_json(self, reply_to_id=None, reason=None, **fields):
        response = {
            'success': False,
            'reason':  reason,
        }
        if reply_to_id is not None:
            response['reply_to_id'] = reply_to_id
        response.update(fields)
        return response

    async def dispatch(self, message: JSON, action: str, message_id=None):
        # Receive the message and format it into one of our IncomingMessage objects.
        try:
            message_object = self.message_factory.build_message(self, action, message)
        # Bad action.
        except ValueError:
            return self.format_failure_json(message_id, f"Action '{action}' not supported.")
        # Bad message format.
        except TypeError as e:
            # TODO: Replace with with a more specific error
            message = e.args[0]
            return self.format_failure_json(message_id, message)
        # Dispatch the IncomingMessage.
        try:
            return await message_object.dispatch()
        except LAWError as e:
            return self.format_failure_json(message_id, str(e))
        except Exception as e:
            # TODO: Replace this with a generic message for production.
            # General exceptions store messages as the first argument in their `.args` property.
            message = type(e).__name__
            if e.args:
                message += ": {}".format(e.args[0])
            return self.format_failure_json(message_id, message)

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    @requires_login
    async def get_user_preferences(self, message_id):
        preferences = await self.db_interface.get_user_preferences(self.user_id)
        return GetUserPreferencesOutgoingMessage(message_id, **preferences)

    @requires_login
    async def get_user_stories(self, message_id):
        stories = await self.db_interface.get_user_stories(self.user_id)
        return GetUserStoriesOutgoingMessage(message_id, stories)

    @requires_login
    async def get_user_wikis(self, message_id):
        wikis = await self.db_interface.get_user_wikis(self.user_id)
        return GetUserWikisOutgoingMessage(message_id, wikis)
    
    @requires_login
    async def set_user_name(self, message_id, name):
        await self.db_interface.set_user_name(self.user_id, name)

    @requires_login
    async def set_user_email(self, message_id, email):
        await self.db_interface.set_user_email(self.user_id, email)

    @requires_login
    async def set_user_bio(self, message_id, bio):
        await self.db_interface.set_user_bio(self.user_id, bio)

    # TODO: Implement this.
    # async def set_user_avatar(self, message_id, avatar):
    #     await self.db_interface.set_user_avatar(self.user_id, avatar)
    
    async def user_login(self, message_id, username, password):
        if self.user_id is not None:
            return self.format_failure_json(message_id, "Already logged in.")
        if await self.db_interface.password_is_valid_for_username(username, password):
            self._user_id = await self.db_interface.get_user_id_for_username(username)
            event = 'logged_in'
        else:
            event = 'denied'
        return UserLoginOutgoingMessage(message_id, event)

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    @requires_login
    async def create_story(self, message_id, title, wiki_id, summary):
        story_id = await self.db_interface.create_story(self.user_id, title, summary, wiki_id)
        story = await self.db_interface.get_story(story_id)
        message = {
            'story_id':     story_id,
            'story_title':  story['title'],
            'section_id':   story['section_id'],
            'wiki_id':      story['wiki_id'],
            'users':        story['users'],
            'summary':      story['summary'],
        }
        return CreateStoryOutgoingMessage(message_id, **message)

    @requires_login
    async def add_preceding_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_preceding_subsection(title, parent_id, index)
        return AddPrecedingSubsectionOutgoingMessage(message_id, subsection_id)

    @requires_login
    async def add_inner_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_inner_subsection(title, parent_id, index)
        return AddInnerSubsectionOutgoingMessage(message_id, subsection_id)

    @requires_login
    async def add_succeeding_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_succeeding_subsection(title, parent_id, index)
        return AddSucceedingSubsectionOutgoingMessage(message_id, subsection_id)

    @requires_login
    async def add_paragraph(self, message_id, section_id, text, succeeding_paragraph_id=None):
        paragraph_id = await self.db_interface.add_paragraph(section_id, text, succeeding_paragraph_id)
        return AddParagraphOutgoingMessage(message_id, paragraph_id)

    @requires_login
    async def edit_story(self, message_id, story_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_story_title(story_id, title)
            return EditStoryOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @requires_login
    async def edit_paragraph(self, message_id, section_id, update, paragraph_id):
        if update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_paragraph_text(section_id, paragraph_id=paragraph_id, text=text)
            return EditParagraphOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @requires_login
    async def edit_section_title(self, message_id, section_id, new_title):
        await self.db_interface.set_section_title(section_id, new_title)
        return EditSectionTitleOutgoingMessage(message_id)

    @requires_login
    async def get_story_information(self, message_id, story_id):
        story = await self.db_interface.get_story(story_id)
        message = {
            'story_title':  story['title'],
            'section_id':   story['section_id'],
            'wiki_id':      story['wiki_id'],
            'users':        story['users'],
            'summary':      story['summary'],
        }
        return GetStoryInformationOutgoingMessage(message_id, **message)

    @requires_login
    async def get_story_hierarchy(self, message_id, story_id):
        hierarchy = await self.db_interface.get_story_hierarchy(story_id)
        return GetStoryHierarchyOutgoingMessage(message_id, hierarchy)

    @requires_login
    async def get_section_hierarchy(self, message_id, section_id):
        hierarchy = await self.db_interface.get_section_hierarchy(section_id)
        return GetSectionHierarchyOutgoingMessage(message_id, hierarchy)

    @requires_login
    async def get_section_content(self, message_id, section_id):
        paragraphs = await self.db_interface.get_section_content(section_id)
        content = [{'text': paragraph['text'], 'paragraph_id': paragraph['_id']} for paragraph in paragraphs]
        return GetSectionContentOutgoingMessage(message_id, content)

    @requires_login
    async def delete_story(self, message_id, story_id):
        await self.db_interface.delete_story(story_id)
        return DeleteStoryOutgoingMessage(message_id, "story_deleted")

    @requires_login
    async def delete_section(self, message_id, section_id):
        await self.db_interface.delete_section(section_id)
        return DeleteSectionOutgoingMessage(message_id, "section_deleted")

    @requires_login
    async def delete_paragraph(self, message_id, section_id, paragraph_id):
        await self.db_interface.delete_paragraph(section_id, paragraph_id)
        return DeleteParagraphOutgoingMessage(message_id, "paragraph_deleted")

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    @requires_login
    async def create_wiki(self, message_id, title, summary):
        wiki_id = await self.db_interface.create_wiki(self.user_id, title, summary)
        wiki = await self.db_interface.get_wiki(wiki_id)
        message = {
            'wiki_id':      wiki_id,
            'wiki_title':   wiki['title'],
            'segment_id':   wiki['segment_id'],
            'users':        wiki['users'],
            'summary':      wiki['summary'],
        }
        return CreateWikiOutgoingMessage(message_id, **message)

    @requires_login
    async def add_segment(self, message_id, title, parent_id):
        segment_id = await self.db_interface.add_child_segment(title, parent_id)
        return AddSegmentOutgoingMessage(message_id, segment_id)

    @requires_login
    async def add_template_heading(self, message_id, title, segment_id):
        await self.db_interface.add_template_heading(title, segment_id)
        return AddTemplateHeadingOutgoingMessage(message_id)

    @requires_login
    async def add_page(self, message_id, title, parent_id):
        page_id = await self.db_interface.create_page(title, parent_id)
        return AddPageOutgoingMessage(message_id, page_id)

    @requires_login
    async def add_heading(self, message_id, title, page_id, index=None):
        await self.db_interface.add_heading(title, page_id, index)
        return AddHeadingOutgoingMessage(message_id)

    @requires_login
    async def edit_wiki(self, message_id, wiki_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_wiki_title(title, wiki_id)
            return EditWikiOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @requires_login
    async def edit_segment(self, message_id, segment_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_segment_title(title, segment_id)
            return EditSegmentOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @requires_login
    async def edit_template_heading(self, message_id, segment_id, template_heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_template_heading_title(old_title=template_heading_title, new_title=title,
                                                               segment_id=segment_id)
            return EditTemplateHeadingOutgoingMessage(message_id)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_template_heading_text(template_heading_title, text, segment_id)
            return EditTemplateHeadingOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @requires_login
    async def edit_page(self, message_id, page_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_page_title(title, page_id)
            return EditPageOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @requires_login
    async def edit_heading(self, message_id, page_id, heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_heading_title(old_title=heading_title, new_title=title, page_id=page_id)
            return EditHeadingOutgoingMessage(message_id)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_heading_text(heading_title, text, page_id)
            return EditHeadingOutgoingMessage(message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update('update_type')))

    @requires_login
    async def get_wiki_information(self, message_id, wiki_id):
        wiki = await self.db_interface.get_wiki(wiki_id)
        message = {
            'wiki_title':   wiki['title'],
            'segment_id':   wiki['segment_id'],
            'users':        wiki['users'],
            'summary':      wiki['summary'],
        }
        return GetWikiInformationOutgoingMessage(message_id, **message)

    @requires_login
    async def get_wiki_hierarchy(self, message_id, wiki_id):
        hierarchy = await self.db_interface.get_wiki_hierarchy(wiki_id)
        link_table = hierarchy.pop('links')
        return GetWikiHierarchyOutgoingMessage(message_id, hierarchy, link_table)

    @requires_login
    async def get_wiki_segment_hierarchy(self, message_id, segment_id):
        hierarchy = await self.db_interface.get_segment_hierarchy(segment_id)
        link_table = hierarchy.pop('links')
        return GetWikiSegmentHierarchyOutgoingMessage(message_id, hierarchy, link_table)

    @requires_login
    async def get_wiki_segment(self, message_id, segment_id):
        segment = await self.db_interface.get_segment(segment_id)
        return GetWikiSegmentOutgoingMessage(message_id, **segment)

    @requires_login
    async def get_wiki_page(self, message_id, page_id):
        page = await self.db_interface.get_page(page_id)
        return GetWikiPageOutgoingMessage(message_id, **page)

    @requires_login
    async def delete_wiki(self, message_id, wiki_id):
        await self.db_interface.delete_wiki(self.user_id, wiki_id)
        return DeleteWikiOutgoingMessage(message_id, "wiki_deleted")
        
    @requires_login
    async def delete_segment(self, message_id, segment_id):
        await self.db_interface.delete_segment(segment_id)
        return DeleteSegmentOutgoingMessage(message_id, "segment_deleted")

    @requires_login
    async def delete_template_heading(self, message_id, segment_id, template_heading_title):
        await self.db_interface.delete_template_heading(template_heading_title, segment_id)
        return DeleteTemplateHeadingOutgoingMessage(message_id, "template_heading_deleted")

    @requires_login
    async def delete_page(self, message_id, page_id):
        await self.db_interface.delete_page(page_id)
        return DeletePageOutgoingMessage(message_id, "page_deleted")

    @requires_login
    async def delete_heading(self, message_id, heading_title, page_id):
        await self.db_interface.delete_heading(heading_title, page_id)
        return DeleteHeadingOutgoingMessage(message_id, "heading_deleted")

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    @requires_login
    async def create_link(self, message_id, story_id, section_id, paragraph_id, name, page_id):
        link_id = await self.db_interface.create_link(story_id, section_id, paragraph_id, name, page_id)
        return CreateLinkOutgoingMessage(message_id, link_id)

    @requires_login
    async def delete_link(self, message_id, link_id):
        await self.db_interface.delete_link(link_id)
        return DeleteLinkOutgoingMessage(message_id, "link_deleted")

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################


    @requires_login
    async def change_alias_name(self, message_id, alias_id, new_name):
        await self.db_interface.change_alias_name(alias_id, new_name)
        return ChangeAliasNameOutgoingMessage(message_id)

    @requires_login
    async def delete_alias(self, message_id, alias_id):
        await self.db_interface.delete_alias(alias_id)
        return DeleteAliasOutgoingMessage(message_id, "alias_deleted")
