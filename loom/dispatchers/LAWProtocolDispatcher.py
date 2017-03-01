from .AbstractDispatcher import AbstractDispatcher

from loom.database.interfaces import AbstractDBInterface
from loom.messages import IncomingMessage
from loom.messages.outgoing import *


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
class LAWProtocolDispatcher(AbstractDispatcher):
    def __init__(self, interface: AbstractDBInterface, user_id=None):
        self._db_interface = interface
        self._user_id = user_id

    @property
    def db_interface(self):
        return self._db_interface

    @staticmethod
    def format_failure_json(uuid, message_id, reason=None, **fields):
        response = {
            'success':    False,
            'reason':     reason,
            'identifier': {
                'uuid':       uuid,
                'message_id': message_id,
            }
        }
        response.update(fields)
        return response

    async def dispatch(self, message: IncomingMessage, uuid: UUID, message_id=None):
        # Dispatch the IncomingMessage.
        try:
            return await message.dispatch()
        except LAWError as e:
            return self.format_failure_json(uuid, message_id, str(e))
        except Exception as e:
            # TODO: Replace this with a generic message for production.
            # General exceptions store messages as the first argument in their `.args` property.
            message = type(e).__name__
            if e.args:
                message += ": {}".format(e.args[0])
            return self.format_failure_json(uuid, message_id, message)

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    async def get_user_preferences(self, uuid, message_id, user_id):
        preferences = await self.db_interface.get_user_preferences(user_id)
        return GetUserPreferencesOutgoingMessage(uuid, message_id,
                                                 username=preferences['username'],
                                                 name=preferences['name'],
                                                 email=preferences['email'],
                                                 bio=preferences['bio'],
                                                 avatar=preferences['avatar'])

    async def get_user_stories(self, uuid, message_id, user_id):
        stories = await self.db_interface.get_user_stories(user_id)
        return GetUserStoriesOutgoingMessage(uuid, message_id, stories=stories)

    async def get_user_wikis(self, uuid, message_id, user_id):
        wikis = await self.db_interface.get_user_wikis(user_id)
        return GetUserWikisOutgoingMessage(uuid, message_id, wikis=wikis)
    
    async def set_user_name(self, uuid, message_id, name, user_id):
        await self.db_interface.set_user_name(user_id, name)
        return SetUserNameOutgoingMessage(uuid, message_id)

    async def set_user_email(self, uuid, message_id, email, user_id):
        await self.db_interface.set_user_email(user_id, email)
        return SetUserEmailOutgoingMessage(uuid, message_id)

    async def set_user_bio(self, uuid, message_id, user_id, bio):
        await self.db_interface.set_user_bio(user_id, bio)
        return SetUserBioOutgoingMessage(uuid, message_id)

    # TODO: Implement this.
    # async def set_user_avatar(self, uuid, message_id, avatar):
    #     await self.db_interface.set_user_avatar(self.user_id, avatar)

    async def set_user_story_position_context(self, user_id, story_id, position_context):
        await self.db_interface.set_story_position_context(user_id, story_id, position_context)

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    async def create_story(self, uuid, message_id, user_id, title, wiki_id, summary):
        story_id = await self.db_interface.create_story(user_id, title, summary, wiki_id)
        story = await self.db_interface.get_story(story_id)
        return CreateStoryOutgoingMessage(uuid, message_id,
                                          story_title=story['title'],
                                          story_id=story_id,
                                          section_id=story['section_id'],
                                          wiki_id=story['wiki_id'],
                                          users=story['users'])

    async def add_preceding_subsection(self, uuid, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_preceding_subsection(title, parent_id, index)
        return AddPrecedingSubsectionOutgoingMessage(uuid, message_id,
                                                     section_id=subsection_id,
                                                     title=title,
                                                     parent_id=parent_id,
                                                     index=index)

    async def add_inner_subsection(self, uuid, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_inner_subsection(title, parent_id, index)
        return AddInnerSubsectionOutgoingMessage(uuid, message_id,
                                                 section_id=subsection_id,
                                                 title=title,
                                                 parent_id=parent_id,
                                                 index=index)

    async def add_succeeding_subsection(self, uuid, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_succeeding_subsection(title, parent_id, index)
        return AddSucceedingSubsectionOutgoingMessage(uuid, message_id,
                                                      section_id=subsection_id,
                                                      title=title,
                                                      parent_id=parent_id,
                                                      index=index)

    async def add_paragraph(self, uuid, message_id, section_id, text, succeeding_paragraph_id=None):
        paragraph_id = await self.db_interface.add_paragraph(section_id, text, succeeding_paragraph_id)
        return AddParagraphOutgoingMessage(uuid, message_id,
                                           paragraph_id=paragraph_id,
                                           section_id=section_id,
                                           text=text,
                                           succeeding_paragraph_id=succeeding_paragraph_id)

    async def add_bookmark(self, uuid, message_id, name, story_id, section_id, paragraph_id, index=None):
        bookmark_id = await self.db_interface.add_bookmark(name, story_id, section_id, paragraph_id, index)
        return AddBookmarkOutgoingMessage(uuid, message_id,
                                          bookmark_id=bookmark_id,
                                          story_id=story_id,
                                          section_id=section_id,
                                          paragraph_id=paragraph_id,
                                          index=index)

    async def edit_story(self, uuid, message_id, story_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_story_title(story_id, title)
            return EditStoryOutgoingMessage(uuid, message_id,
                                            story_id=story_id,
                                            update=update)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    async def edit_paragraph(self, uuid, message_id, section_id, update, paragraph_id):
        if update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_paragraph_text(section_id, paragraph_id=paragraph_id, text=text)
            return EditParagraphOutgoingMessage(uuid, message_id,
                                                section_id=section_id,
                                                update=update,
                                                paragraph_id=paragraph_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    async def edit_section_title(self, uuid, message_id, section_id, new_title):
        await self.db_interface.set_section_title(section_id, new_title)
        return EditSectionTitleOutgoingMessage(uuid, message_id,
                                               section_id=section_id,
                                               new_title=new_title)

    async def edit_bookmark(self, uuid, message_id, story_id, bookmark_id, update):
        if update['update_type'] == 'set_name':
            name = update['name']
            await self.db_interface.set_bookmark_name(story_id, bookmark_id, name)
            return EditBookmarkOutgoingMessage(uuid, message_id,
                                               story_id=story_id,
                                               bookmark_id=bookmark_id,
                                               update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    async def set_note(self, uuid, message_id, section_id, paragraph_id, note):
        await self.db_interface.set_note(section_id, paragraph_id, note)
        return SetNoteOutgoingMessage(uuid, message_id,
                                      section_id=section_id,
                                      paragraph_id=paragraph_id,
                                      note=note)

    async def get_story_information(self, uuid, message_id, story_id):
        story = await self.db_interface.get_story(story_id)
        return GetStoryInformationOutgoingMessage(uuid, message_id,
                                                  story_title=story['title'],
                                                  section_id=story['section_id'],
                                                  wiki_id=story['wiki_id'],
                                                  users=story['users'])

    async def get_story_bookmarks(self, uuid, message_id, story_id):
        bookmarks = await self.db_interface.get_story_bookmarks(story_id)
        return GetStoryBookmarksOutgoingMessage(uuid, message_id, bookmarks=bookmarks)

    async def get_story_hierarchy(self, uuid, message_id, story_id):
        hierarchy = await self.db_interface.get_story_hierarchy(story_id)
        return GetStoryHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy)

    async def get_section_hierarchy(self, uuid, message_id, section_id):
        hierarchy = await self.db_interface.get_section_hierarchy(section_id)
        return GetSectionHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy)

    async def get_section_content(self, uuid, message_id, section_id):
        paragraphs = await self.db_interface.get_section_content(section_id)
        content = [{'text': paragraph['text'], 'paragraph_id': paragraph['_id'], 'note': paragraph['note']}
                   for paragraph in paragraphs]
        return GetSectionContentOutgoingMessage(uuid, message_id, content=content)

    async def delete_story(self, uuid, message_id, story_id):
        await self.db_interface.delete_story(story_id)
        return DeleteStoryOutgoingMessage(uuid, message_id, story_id=story_id)

    async def delete_section(self, uuid, message_id, section_id):
        await self.db_interface.delete_section(section_id)
        return DeleteSectionOutgoingMessage(uuid, message_id, section_id=section_id)

    async def delete_paragraph(self, uuid, message_id, section_id, paragraph_id):
        await self.db_interface.delete_paragraph(section_id, paragraph_id)
        return DeleteParagraphOutgoingMessage(uuid, message_id, section_id=section_id, paragraph_id=paragraph_id)

    async def delete_note(self, uuid, message_id, section_id, paragraph_id):
        await self.db_interface.delete_note(section_id, paragraph_id)
        return DeleteNoteOutgoingMessage(uuid, message_id, section_id=section_id, paragraph_id=paragraph_id)

    async def delete_bookmark(self, uuid, message_id, bookmark_id):
        await self.db_interface.delete_bookmark(bookmark_id)
        return DeleteBookmarkOutgoingMessage(uuid, message_id, bookmark_id=bookmark_id)

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    async def create_wiki(self, uuid, message_id, user_id, title, summary):
        wiki_id = await self.db_interface.create_wiki(user_id, title, summary)
        wiki = await self.db_interface.get_wiki(wiki_id)
        return CreateWikiOutgoingMessage(uuid, message_id,
                                         wiki_title=wiki['title'],
                                         wiki_id=wiki_id,
                                         segment_id=wiki['segment_id'],
                                         users=wiki['users'],
                                         summary=wiki['summary'])

    async def add_segment(self, uuid, message_id, title, parent_id):
        segment_id = await self.db_interface.add_child_segment(title, parent_id)
        return AddSegmentOutgoingMessage(uuid, message_id, segment_id=segment_id, title=title, parent_id=parent_id)

    async def add_template_heading(self, uuid, message_id, title, segment_id):
        await self.db_interface.add_template_heading(title, segment_id)
        return AddTemplateHeadingOutgoingMessage(uuid, message_id, title=title, segment_id=segment_id)

    async def add_page(self, uuid, message_id, title, parent_id):
        page_id = await self.db_interface.create_page(title, parent_id)
        return AddPageOutgoingMessage(uuid, message_id, page_id=page_id, title=title, parent_id=parent_id)

    async def add_heading(self, uuid, message_id, title, page_id, index=None):
        await self.db_interface.add_heading(title, page_id, index)
        return AddHeadingOutgoingMessage(uuid, message_id, title=title, page_id=page_id, index=index)

    async def edit_wiki(self, uuid, message_id, wiki_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_wiki_title(title, wiki_id)
            return EditWikiOutgoingMessage(uuid, message_id, wiki_id=wiki_id, update=update)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    async def edit_segment(self, uuid, message_id, segment_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_segment_title(title, segment_id)
            return EditSegmentOutgoingMessage(uuid, message_id, segment_id=segment_id, update=update)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    async def edit_template_heading(self, uuid, message_id, segment_id, template_heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_template_heading_title(old_title=template_heading_title, new_title=title,
                                                               segment_id=segment_id)
            return EditTemplateHeadingOutgoingMessage(uuid, message_id,
                                                      segment_id=segment_id,
                                                      template_heading_title=template_heading_title,
                                                      update=update)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_template_heading_text(template_heading_title, text, segment_id)
            return EditTemplateHeadingOutgoingMessage(uuid, message_id,
                                                      segment_id=segment_id,
                                                      template_heading_title=template_heading_title,
                                                      update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    async def edit_page(self, uuid, message_id, page_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_page_title(title, page_id)
            return EditPageOutgoingMessage(uuid, message_id, page_id=page_id, update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    async def edit_heading(self, uuid, message_id, page_id, heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_heading_title(old_title=heading_title, new_title=title, page_id=page_id)
            return EditHeadingOutgoingMessage(uuid, message_id,
                                              page_id=page_id,
                                              heading_title=heading_title,
                                              update=update)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_heading_text(heading_title, text, page_id)
            return EditHeadingOutgoingMessage(uuid, message_id,
                                              page_id=page_id,
                                              heading_title=heading_title,
                                              update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    async def get_wiki_information(self, uuid, message_id, wiki_id):
        wiki = await self.db_interface.get_wiki(wiki_id)
        return GetWikiInformationOutgoingMessage(uuid, message_id,
                                                 wiki_title=wiki['title'],
                                                 segment_id=wiki['segment_id'],
                                                 users=wiki['users'],
                                                 summary=wiki['summary'])

    async def get_wiki_hierarchy(self, uuid, message_id, wiki_id):
        hierarchy = await self.db_interface.get_wiki_hierarchy(wiki_id)
        link_table = hierarchy.pop('links')
        return GetWikiHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy, link_table=link_table)

    async def get_wiki_segment_hierarchy(self, uuid, message_id, segment_id):
        hierarchy = await self.db_interface.get_segment_hierarchy(segment_id)
        link_table = hierarchy.pop('links')
        return GetWikiSegmentHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy, link_table=link_table)

    async def get_wiki_segment(self, uuid, message_id, segment_id):
        segment = await self.db_interface.get_segment(segment_id)
        return GetWikiSegmentOutgoingMessage(uuid, message_id,
                                             title=segment['title'],
                                             segments=segment['segments'],
                                             pages=segment['pages'],
                                             template_headings=segment['template_headings'])

    async def get_wiki_page(self, uuid, message_id, page_id):
        page = await self.db_interface.get_page(page_id)
        return GetWikiPageOutgoingMessage(uuid, message_id,
                                          title=page['title'],
                                          aliases=page['aliases'],
                                          references=page['references'],
                                          headings=page['headings'])

    async def delete_wiki(self, uuid, message_id, user_id, wiki_id):
        await self.db_interface.delete_wiki(user_id, wiki_id)
        return DeleteWikiOutgoingMessage(uuid, message_id, wiki_id=wiki_id)
        
    async def delete_segment(self, uuid, message_id, segment_id):
        await self.db_interface.delete_segment(segment_id)
        return DeleteSegmentOutgoingMessage(uuid, message_id, segment_id=segment_id)

    async def delete_template_heading(self, uuid, message_id, segment_id, template_heading_title):
        await self.db_interface.delete_template_heading(template_heading_title, segment_id)
        return DeleteTemplateHeadingOutgoingMessage(uuid, message_id,
                                                    segment_id=segment_id,
                                                    template_heading_title=template_heading_title)

    async def delete_page(self, uuid, message_id, page_id):
        await self.db_interface.delete_page(page_id)
        return DeletePageOutgoingMessage(uuid, message_id, page_id=page_id)

    async def delete_heading(self, uuid, message_id, heading_title, page_id):
        await self.db_interface.delete_heading(heading_title, page_id)
        return DeleteHeadingOutgoingMessage(uuid, message_id, page_id=page_id, heading_title=heading_title)

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    async def delete_link(self, uuid, message_id, link_id):
        await self.db_interface.delete_link(link_id)
        return DeleteLinkOutgoingMessage(uuid, message_id, link_id=link_id)

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    async def change_alias_name(self, uuid, message_id, alias_id, new_name):
        await self.db_interface.change_alias_name(alias_id, new_name)
        return ChangeAliasNameOutgoingMessage(uuid, message_id, alias_id=alias_id, new_name=new_name)

    async def delete_alias(self, uuid, message_id, alias_id):
        await self.db_interface.delete_alias(alias_id)
        return DeleteAliasOutgoingMessage(uuid, message_id, alias_id=alias_id)

    ###########################################################################
    #
    # Statistics Methods
    #
    ###########################################################################

    async def get_story_statistics(self, uuid, message_id, story_id):
        stats = await self.db_interface.get_story_statistics(story_id)
        return GetStoryStatisticsOutgoingMessage(uuid, message_id, statistics=stats)

    async def get_section_statistics(self, uuid, message_id, section_id):
        stats = await self.db_interface.get_section_statistics(section_id)
        return GetSectionStatisticsOutgoingMessage(uuid, message_id, statistics=stats)

    async def get_paragraph_statistics(self, uuid, message_id, section_id, paragraph_id):
        stats = await self.db_interface.get_paragraph_statistics(section_id, paragraph_id)
        return GetParagraphStatisticsOutgoingMessage(uuid, message_id, statistics=stats)
