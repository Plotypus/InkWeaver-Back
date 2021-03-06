from .AbstractDispatcher import AbstractDispatcher

from loom.database.interfaces import AbstractDBInterface
from loom.database.interfaces.errors import *
from loom.loggers import interface_log
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


def handle_interface_errors(func):
    async def wrapped(dispatcher, uuid, message_id, *args, **kwargs):
        try:
            async for message in func(dispatcher, uuid, message_id, *args, **kwargs):
                yield message
        except InterfaceError as e:
            interface_log.error(f'{e.query}: {e.message}')
            yield LoomErrorOutgoingMessage(uuid, message_id, action=func.__name__, reason=e.message)
    return wrapped


############################################################
#
# LAWProtocolDispatcher Decorators
#
############################################################
class LAWProtocolDispatcher(AbstractDispatcher):
    def __init__(self, interface: AbstractDBInterface):
        self._db_interface = interface

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

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def get_user_preferences(self, uuid, message_id, user_id):
        preferences = await self.db_interface.get_user_preferences(user_id)
        yield GetUserPreferencesOutgoingMessage(uuid, message_id,
                                                username=preferences['username'],
                                                name=preferences['name'],
                                                email=preferences['email'],
                                                bio=preferences['bio'],
                                                avatar=preferences['avatar'])

    @handle_interface_errors
    async def get_user_stories_and_wikis(self, uuid, message_id, user_id):
        response = await self.db_interface.get_user_stories_and_wikis(user_id)
        yield GetUserStoriesAndWikisOutgoingMessage(uuid, message_id,
                                                    stories=response['stories'],
                                                    wikis=response['wikis'])

    @handle_interface_errors
    async def set_user_name(self, uuid, message_id, user_id, name):
        await self.db_interface.set_user_name(user_id, name)
        yield SetUserNameOutgoingMessage(uuid, message_id, name=name)

    @handle_interface_errors
    async def set_user_email(self, uuid, message_id, user_id, email):
        await self.db_interface.set_user_email(user_id, email)
        yield SetUserEmailOutgoingMessage(uuid, message_id, email=email)

    @handle_interface_errors
    async def set_user_bio(self, uuid, message_id, user_id, bio):
        await self.db_interface.set_user_bio(user_id, bio)
        yield SetUserBioOutgoingMessage(uuid, message_id, bio=bio)

    # TODO: Implement this.
    # async def set_user_avatar(self, uuid, message_id, avatar):
    #     await self.db_interface.set_user_avatar(self.user_id, avatar)

    @handle_interface_errors
    async def set_user_story_position_context(self, uuid, message_id, user_id, story_id, position_context):
        await self.db_interface.set_story_position_context(user_id, story_id, position_context)
        # Async equivalent to `return None`
        return
        # noinspection PyUnreachableCode
        yield

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def create_story(self, uuid, message_id, user_id, title, wiki_id, summary):
        story_id = await self.db_interface.create_story(user_id, title, summary, wiki_id)
        story = await self.db_interface.get_story(story_id)
        yield CreateStoryOutgoingMessage(uuid, message_id,
                                         story_title=story['title'],
                                         story_id=story_id,
                                         section_id=story['section_id'],
                                         wiki_id=story['wiki_id'],
                                         users=story['users'])

    @handle_interface_errors
    async def add_preceding_subsection(self, uuid, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_preceding_subsection(title, parent_id, index)
        yield AddPrecedingSubsectionOutgoingMessage(uuid, message_id,
                                                    section_id=subsection_id,
                                                    title=title,
                                                    parent_id=parent_id,
                                                    index=index)

    @handle_interface_errors
    async def add_inner_subsection(self, uuid, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_inner_subsection(title, parent_id, index)
        yield AddInnerSubsectionOutgoingMessage(uuid, message_id,
                                                section_id=subsection_id,
                                                title=title,
                                                parent_id=parent_id,
                                                index=index)

    @handle_interface_errors
    async def add_succeeding_subsection(self, uuid, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_succeeding_subsection(title, parent_id, index)
        yield AddSucceedingSubsectionOutgoingMessage(uuid, message_id,
                                                     section_id=subsection_id,
                                                     title=title,
                                                     parent_id=parent_id,
                                                     index=index)

    @handle_interface_errors
    async def add_paragraph(self, uuid, message_id, wiki_id, section_id, text, succeeding_paragraph_id=None):
        (
            text,
            paragraph_id,
            links_created,
            passive_links_created,
            aliases_created
        ) = await self.db_interface.add_paragraph(wiki_id, section_id, text, succeeding_paragraph_id)
        for alias_id, page_id, name in aliases_created:
            yield CreateAliasOutgoingMessage(uuid, message_id, alias_id=alias_id, page_id=page_id, alias_name=name)
        for link_id, alias_id in links_created:
            yield CreateLinkOutgoingMessage(uuid, message_id, link_id=link_id, alias_id=alias_id)
        for passive_link_id, alias_id in passive_links_created:
            yield CreatePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id, alias_id=alias_id)
        yield AddParagraphOutgoingMessage(uuid, message_id,
                                          paragraph_id=paragraph_id,
                                          section_id=section_id,
                                          text=text,
                                          succeeding_paragraph_id=succeeding_paragraph_id)

    @handle_interface_errors
    async def add_bookmark(self, uuid, message_id, name, story_id, section_id, paragraph_id, index=None):
        bookmark_id = await self.db_interface.add_bookmark(name, story_id, section_id, paragraph_id, index)
        yield AddBookmarkOutgoingMessage(uuid, message_id,
                                         bookmark_id=bookmark_id,
                                         story_id=story_id,
                                         section_id=section_id,
                                         paragraph_id=paragraph_id,
                                         name=name,
                                         index=index)

    @handle_interface_errors
    async def add_story_collaborator(self, uuid, message_id, story_id, username):
        user_id, user_name, wiki_id = await self.db_interface.add_story_collaborator(story_id, username)
        yield AddStoryCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id, user_name=user_name)
        story_description = await self.db_interface.get_story_description(user_id, story_id)
        yield InformNewStoryCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id,
                                                        story_description=story_description)
        if wiki_id is not None:
            yield AddWikiCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id, user_name=user_name)
            yield InformNewWikiCollaboratorOutgoingMessage(uuid, message_id, wiki_id=wiki_id, user_id=user_id)

    @handle_interface_errors
    async def edit_story(self, uuid, message_id, story_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_story_title(story_id, title)
            yield EditStoryOutgoingMessage(uuid, message_id,
                                           story_id=story_id,
                                           update=update)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @handle_interface_errors
    async def edit_paragraph(self, uuid, message_id, wiki_id, section_id, update, paragraph_id):
        if update['update_type'] == 'set_text':
            text = update['text']
            (
                text,
                links_created,
                passive_links_created,
                aliases_created
            ) = await self.db_interface.set_paragraph_text(wiki_id, section_id, paragraph_id=paragraph_id, text=text)
            for alias_id, page_id, name in aliases_created:
                yield CreateAliasOutgoingMessage(uuid, message_id, alias_id=alias_id, page_id=page_id, alias_name=name)
            for link_id, alias_id in links_created:
                yield CreateLinkOutgoingMessage(uuid, message_id, link_id=link_id, alias_id=alias_id)
            for passive_link_id, alias_id in passive_links_created:
                yield CreatePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id,
                                                       alias_id=alias_id)
            update['text'] = text
            yield EditParagraphOutgoingMessage(uuid, message_id,
                                               section_id=section_id,
                                               update=update,
                                               paragraph_id=paragraph_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @handle_interface_errors
    async def edit_section_title(self, uuid, message_id, section_id, new_title):
        await self.db_interface.set_section_title(section_id, new_title)
        yield EditSectionTitleOutgoingMessage(uuid, message_id,
                                              section_id=section_id,
                                              new_title=new_title)

    @handle_interface_errors
    async def edit_bookmark(self, uuid, message_id, story_id, bookmark_id, update):
        if update['update_type'] == 'set_name':
            name = update['name']
            await self.db_interface.set_bookmark_name(story_id, bookmark_id, name)
            yield EditBookmarkOutgoingMessage(uuid, message_id,
                                              story_id=story_id,
                                              bookmark_id=bookmark_id,
                                              update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @handle_interface_errors
    async def set_note(self, uuid, message_id, section_id, paragraph_id, note):
        await self.db_interface.set_note(section_id, paragraph_id, note)
        yield SetNoteOutgoingMessage(uuid, message_id,
                                     section_id=section_id,
                                     paragraph_id=paragraph_id,
                                     note=note)

    @handle_interface_errors
    async def get_story_information(self, uuid, message_id, story_id):
        story = await self.db_interface.get_story(story_id)
        yield GetStoryInformationOutgoingMessage(uuid, message_id,
                                                 story_title=story['title'],
                                                 section_id=story['section_id'],
                                                 wiki_id=story['wiki_id'],
                                                 users=story['users'])

    @handle_interface_errors
    async def get_story_bookmarks(self, uuid, message_id, story_id):
        bookmarks = await self.db_interface.get_story_bookmarks(story_id)
        yield GetStoryBookmarksOutgoingMessage(uuid, message_id, bookmarks=bookmarks)

    @handle_interface_errors
    async def get_story_hierarchy(self, uuid, message_id, story_id):
        hierarchy = await self.db_interface.get_story_hierarchy(story_id)
        yield GetStoryHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy)

    @handle_interface_errors
    async def get_section_hierarchy(self, uuid, message_id, section_id):
        hierarchy = await self.db_interface.get_section_hierarchy(section_id)
        yield GetSectionHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy)

    @handle_interface_errors
    async def get_section_content(self, uuid, message_id, section_id):
        paragraphs = await self.db_interface.get_section_content(section_id)
        content = [{'text': paragraph['text'], 'paragraph_id': paragraph['_id'], 'note': paragraph['note']}
                   for paragraph in paragraphs]
        yield GetSectionContentOutgoingMessage(uuid, message_id, content=content)

    @handle_interface_errors
    async def delete_story(self, uuid, message_id, story_id, user_id):
        user_ids = await self.db_interface.delete_story(story_id, user_id)
        yield DeleteStoryOutgoingMessage(uuid, message_id, story_id=story_id)
        for user_id in user_ids:
            yield DeleteStoryNotificationOutgoingMessage(uuid, message_id, story_id=story_id, user_id=user_id)

    @handle_interface_errors
    async def delete_section(self, uuid, message_id, story_id, section_id):
        deleted_bookmarks = await self.db_interface.delete_section(section_id, story_id)
        for bookmark in deleted_bookmarks:
            yield DeleteBookmarkOutgoingMessage(uuid, message_id, bookmark_id=bookmark['bookmark_id'])
        yield DeleteSectionOutgoingMessage(uuid, message_id, section_id=section_id)

    @handle_interface_errors
    async def delete_paragraph(self, uuid, message_id, story_id, section_id, paragraph_id):
        deleted_bookmarks = await self.db_interface.delete_paragraph(story_id, section_id, paragraph_id)
        for bookmark in deleted_bookmarks:
            yield DeleteBookmarkOutgoingMessage(uuid, message_id, bookmark_id=bookmark['bookmark_id'])
        yield DeleteParagraphOutgoingMessage(uuid, message_id, section_id=section_id, paragraph_id=paragraph_id)

    @handle_interface_errors
    async def delete_note(self, uuid, message_id, section_id, paragraph_id):
        await self.db_interface.delete_note(section_id, paragraph_id)
        yield DeleteNoteOutgoingMessage(uuid, message_id, section_id=section_id, paragraph_id=paragraph_id)

    @handle_interface_errors
    async def delete_bookmark(self, uuid, message_id, bookmark_id):
        await self.db_interface.delete_bookmark(bookmark_id)
        yield DeleteBookmarkOutgoingMessage(uuid, message_id, bookmark_id=bookmark_id)

    @handle_interface_errors
    async def remove_story_collaborator(self, uuid, message_id, story_id, user_id):
        wiki_id = await self.db_interface.remove_story_collaborator(story_id, user_id)
        yield RemoveStoryCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id)
        yield InformStoryCollaboratorOfRemovalOutgoingMessage(uuid, message_id, story_id=story_id, user_id=user_id)
        if wiki_id is not None:
            yield RemoveWikiCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id)
            yield InformWikiCollaboratorOfRemovalOutgoingMessage(uuid, message_id, wiki_id=wiki_id, user_id=user_id)

    @handle_interface_errors
    async def move_subsection_as_preceding(self, uuid, message_id, section_id, to_parent_id, to_index):
        await self.db_interface.move_subsection_as_preceding(section_id, to_parent_id, to_index)
        yield MoveSubsectionAsPrecedingOutgoingMessage(uuid, message_id, section_id=section_id,
                                                       to_parent_id=to_parent_id, to_index=to_index)

    @handle_interface_errors
    async def move_subsection_as_inner(self, uuid, message_id, section_id, to_parent_id, to_index):
        await self.db_interface.move_subsection_as_inner(section_id, to_parent_id, to_index)
        yield MoveSubsectionAsInnerOutgoingMessage(uuid, message_id, section_id=section_id,
                                                   to_parent_id=to_parent_id, to_index=to_index)

    @handle_interface_errors
    async def move_subsection_as_succeeding(self, uuid, message_id, section_id, to_parent_id, to_index):
        await self.db_interface.move_subsection_as_succeeding(section_id, to_parent_id, to_index)
        yield MoveSubsectionAsSucceedingOutgoingMessage(uuid, message_id, section_id=section_id,
                                                        to_parent_id=to_parent_id, to_index=to_index)

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def create_wiki(self, uuid, message_id, user_id, title, summary):
        wiki_id = await self.db_interface.create_wiki(user_id, title, summary)
        wiki = await self.db_interface.get_wiki(wiki_id)
        yield CreateWikiOutgoingMessage(uuid, message_id,
                                        wiki_title=wiki['title'],
                                        wiki_id=wiki_id,
                                        segment_id=wiki['segment_id'],
                                        users=wiki['users'],
                                        summary=wiki['summary'])

    @handle_interface_errors
    async def add_segment(self, uuid, message_id, wiki_id, title, parent_id):
        segment_id = await self.db_interface.add_child_segment(wiki_id, title, parent_id)
        yield AddSegmentOutgoingMessage(uuid, message_id, segment_id=segment_id, title=title, parent_id=parent_id)

    @handle_interface_errors
    async def add_template_heading(self, uuid, message_id, title, segment_id):
        await self.db_interface.add_template_heading(title, segment_id)
        yield AddTemplateHeadingOutgoingMessage(uuid, message_id, title=title, segment_id=segment_id)

    @handle_interface_errors
    async def add_page(self, uuid, message_id, wiki_id, title, parent_id):
        page_id, alias_id = await self.db_interface.create_page(wiki_id, title, parent_id)
        yield AddPageOutgoingMessage(uuid, message_id, page_id=page_id, title=title, parent_id=parent_id)
        yield CreateAliasOutgoingMessage(uuid, message_id, alias_id=alias_id, page_id=page_id, alias_name=title)

    @handle_interface_errors
    async def add_heading(self, uuid, message_id, title, page_id, index=None):
        await self.db_interface.add_heading(title, page_id, index)
        yield AddHeadingOutgoingMessage(uuid, message_id, title=title, page_id=page_id, index=index)

    @handle_interface_errors
    async def add_wiki_collaborator(self, uuid, message_id, wiki_id, username):
        user_id, user_name = await self.db_interface.add_wiki_collaborator(wiki_id, username)
        yield AddWikiCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id, user_name=user_name)
        yield InformNewWikiCollaboratorOutgoingMessage(uuid, message_id, wiki_id=wiki_id, user_id=user_id)

    @handle_interface_errors
    async def edit_wiki(self, uuid, message_id, wiki_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_wiki_title(title, wiki_id)
            yield EditWikiOutgoingMessage(uuid, message_id, wiki_id=wiki_id, update=update)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @handle_interface_errors
    async def edit_segment(self, uuid, message_id, segment_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_segment_title(title, segment_id)
            yield EditSegmentOutgoingMessage(uuid, message_id, segment_id=segment_id, update=update)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @handle_interface_errors
    async def edit_template_heading(self, uuid, message_id, segment_id, template_heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_template_heading_title(old_title=template_heading_title, new_title=title,
                                                               segment_id=segment_id)
            yield EditTemplateHeadingOutgoingMessage(uuid, message_id,
                                                     segment_id=segment_id,
                                                     template_heading_title=template_heading_title,
                                                     update=update)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_template_heading_text(template_heading_title, text, segment_id)
            yield EditTemplateHeadingOutgoingMessage(uuid, message_id,
                                                     segment_id=segment_id,
                                                     template_heading_title=template_heading_title,
                                                     update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @handle_interface_errors
    async def edit_page(self, uuid, message_id, wiki_id, page_id, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            alias_id, deleted_passive_link_ids, replacement_alias_info = await self.db_interface.set_page_title(wiki_id,
                                                                                                                title,
                                                                                                                page_id)
            yield EditPageOutgoingMessage(uuid, message_id, page_id=page_id, update=update)
            yield ChangeAliasNameOutgoingMessage(uuid, message_id, alias_id=alias_id, new_name=title)
            for passive_link_id in deleted_passive_link_ids:
                yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
            if replacement_alias_info is not None:
                replacement_alias_id, prev_name = replacement_alias_info
                yield CreateAliasOutgoingMessage(uuid, message_id, alias_id=replacement_alias_id, page_id=page_id,
                                                 alias_name=prev_name)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @handle_interface_errors
    async def edit_heading(self, uuid, message_id, page_id, heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_heading_title(old_title=heading_title, new_title=title, page_id=page_id)
            yield EditHeadingOutgoingMessage(uuid, message_id,
                                             page_id=page_id,
                                             heading_title=heading_title,
                                             update=update)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_heading_text(heading_title, text, page_id)
            yield EditHeadingOutgoingMessage(uuid, message_id,
                                             page_id=page_id,
                                             heading_title=heading_title,
                                             update=update)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @handle_interface_errors
    async def get_wiki_information(self, uuid, message_id, wiki_id):
        wiki = await self.db_interface.get_wiki(wiki_id)
        yield GetWikiInformationOutgoingMessage(uuid, message_id,
                                                wiki_title=wiki['title'],
                                                segment_id=wiki['segment_id'],
                                                users=wiki['users'],
                                                summary=wiki['summary'])

    @handle_interface_errors
    async def get_wiki_alias_list(self, uuid, message_id, wiki_id):
        alias_list = await self.db_interface.get_wiki_alias_list(wiki_id)
        yield GetWikiAliasListOutgoingMessage(uuid, message_id, alias_list=alias_list)

    @handle_interface_errors
    async def get_wiki_hierarchy(self, uuid, message_id, wiki_id):
        hierarchy = await self.db_interface.get_wiki_hierarchy(wiki_id)
        yield GetWikiHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy)

    @handle_interface_errors
    async def get_wiki_segment_hierarchy(self, uuid, message_id, segment_id):
        hierarchy = await self.db_interface.get_segment_hierarchy(segment_id)
        yield GetWikiSegmentHierarchyOutgoingMessage(uuid, message_id, hierarchy=hierarchy)

    @handle_interface_errors
    async def get_wiki_segment(self, uuid, message_id, segment_id):
        segment = await self.db_interface.get_segment(segment_id)
        yield GetWikiSegmentOutgoingMessage(uuid, message_id,
                                            title=segment['title'],
                                            segments=segment['segments'],
                                            pages=segment['pages'],
                                            template_headings=segment['template_headings'])

    @handle_interface_errors
    async def get_wiki_page(self, uuid, message_id, page_id):
        page = await self.db_interface.get_page_for_frontend(page_id)
        yield GetWikiPageOutgoingMessage(uuid, message_id,
                                         title=page['title'],
                                         aliases=page['aliases'],
                                         references=page['references'],
                                         headings=page['headings'])

    @handle_interface_errors
    async def delete_wiki(self, uuid, message_id, user_id, wiki_id):
        deleted_link_ids, deleted_passive_link_ids, deleted_alias_ids = await self.db_interface.delete_wiki(user_id,
                                                                                                            wiki_id)
        for link_id in deleted_link_ids:
            yield DeleteLinkOutgoingMessage(uuid, message_id, link_id=link_id)
        for passive_link_id in deleted_passive_link_ids:
            yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
        for alias_id in deleted_alias_ids:
            yield DeleteAliasOutgoingMessage(uuid, message_id, alias_id=alias_id)
        yield DeleteWikiOutgoingMessage(uuid, message_id, wiki_id=wiki_id)

    @handle_interface_errors
    async def delete_segment(self, uuid, message_id, wiki_id, segment_id):
        (
            deleted_link_ids,
            deleted_passive_link_ids,
            deleted_alias_ids
        ) = await self.db_interface.delete_segment(wiki_id, segment_id)
        for link_id in deleted_link_ids:
            yield DeleteLinkOutgoingMessage(uuid, message_id, link_id=link_id)
        for passive_link_id in deleted_passive_link_ids:
            yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
        for alias_id in deleted_alias_ids:
            yield DeleteAliasOutgoingMessage(uuid, message_id, alias_id=alias_id)
        yield DeleteSegmentOutgoingMessage(uuid, message_id, segment_id=segment_id)

    @handle_interface_errors
    async def delete_template_heading(self, uuid, message_id, segment_id, template_heading_title):
        await self.db_interface.delete_template_heading(template_heading_title, segment_id)
        yield DeleteTemplateHeadingOutgoingMessage(uuid, message_id,
                                                   segment_id=segment_id,
                                                   template_heading_title=template_heading_title)

    @handle_interface_errors
    async def delete_page(self, uuid, message_id, wiki_id, page_id):
        deleted_link_ids, deleted_passive_link_ids, deleted_alias_ids = await self.db_interface.delete_page(wiki_id,
                                                                                                            page_id)
        for link_id in deleted_link_ids:
            yield DeleteLinkOutgoingMessage(uuid, message_id, link_id=link_id)
        for passive_link_id in deleted_passive_link_ids:
            yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
        for alias_id in deleted_alias_ids:
            yield DeleteAliasOutgoingMessage(uuid, message_id, alias_id=alias_id)
        yield DeletePageOutgoingMessage(uuid, message_id, page_id=page_id)

    @handle_interface_errors
    async def delete_heading(self, uuid, message_id, heading_title, page_id):
        await self.db_interface.delete_heading(heading_title, page_id)
        yield DeleteHeadingOutgoingMessage(uuid, message_id, page_id=page_id, heading_title=heading_title)

    @handle_interface_errors
    async def remove_wiki_collaborator(self, uuid, message_id, wiki_id, user_id):
        # IDs of the stories where the user had collaborative privileges revoked
        story_ids = await self.db_interface.remove_wiki_collaborator(wiki_id, user_id)
        yield RemoveWikiCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id)
        yield InformWikiCollaboratorOfRemovalOutgoingMessage(uuid, message_id, wiki_id=wiki_id, user_id=user_id)
        for story_id in story_ids:
            yield InformStoryCollaboratorOfRemovalOutgoingMessage(uuid, message_id, story_id=story_id, user_id=user_id)
            # TODO: Send story specified message to all stories that the user was removed from.
            yield RemoveStoryCollaboratorOutgoingMessage(uuid, message_id, user_id=user_id)

    @handle_interface_errors
    async def move_segment(self, uuid, message_id, segment_id, to_parent_id, to_index):
        await self.db_interface.move_segment(segment_id, to_parent_id, to_index)
        yield MoveSegmentOutGoingMessage(uuid, message_id, segment_id=segment_id, to_parent_id=to_parent_id,
                                         to_index=to_index)

    @handle_interface_errors
    async def move_template_heading(self, uuid, message_id, segment_id, template_heading_title, to_index):
        await self.db_interface.move_template_heading(segment_id, template_heading_title, to_index)
        yield MoveTemplateHeadingOutgoingMessage(uuid, message_id, segment_id=segment_id,
                                                 template_heading_title=template_heading_title, to_index=to_index)

    @handle_interface_errors
    async def move_page(self, uuid, message_id, page_id, to_parent_id, to_index):
        await self.db_interface.move_page(page_id, to_parent_id, to_index)
        yield MovePageOutgoingMessage(uuid, message_id, page_id=page_id, to_parent_id=to_parent_id, to_index=to_index)

    @handle_interface_errors
    async def move_heading(self, uuid, message_id, page_id, heading_title, to_index):
        await self.db_interface.move_heading(page_id, heading_title, to_index)
        yield MoveHeadingOutgoingMessage(uuid, message_id, page_id=page_id, heading_title=heading_title,
                                         to_index=to_index)

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def delete_link(self, uuid, message_id, link_id):
        await self.db_interface.delete_link(link_id)
        yield DeleteLinkOutgoingMessage(uuid, message_id, link_id=link_id)

    ###########################################################################
    #
    # Passive Link Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def approve_passive_link(self, uuid, message_id, passive_link_id, story_id, wiki_id):
        (
            passive_link_id,
            section_id,
            paragraph_id,
            created_link,
            new_paragraph_text,
        ) = await self.db_interface.approve_passive_link(passive_link_id, story_id, wiki_id)
        yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
        update = {
            'update_type': 'set_text',
            'text':        new_paragraph_text,
        }
        link_id, alias_id = created_link
        yield CreateLinkOutgoingMessage(uuid, message_id, link_id=link_id, alias_id=alias_id)
        yield EditParagraphOutgoingMessage(uuid, message_id, section_id=section_id, update=update,
                                           paragraph_id=paragraph_id)

    @handle_interface_errors
    async def reject_passive_link(self, uuid, message_id, passive_link_id):
        await self.db_interface.reject_passive_link(passive_link_id)
        yield RejectPassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def create_alias(self, uuid, message_id, name, page_id):
        alias_id, alias_was_created = await self.db_interface.create_alias(name, page_id)
        if alias_was_created:
            yield CreateAliasOutgoingMessage(uuid, message_id, alias_id=alias_id, page_id=page_id, alias_name=name)
        # TODO: There should probably be an error returned here.

    @handle_interface_errors
    async def change_alias_name(self, uuid, message_id, wiki_id, alias_id, new_name):
        deleted_passive_link_ids, replacement_alias_info = await self.db_interface.change_alias_name(wiki_id, alias_id,
                                                                                                     new_name)
        yield ChangeAliasNameOutgoingMessage(uuid, message_id, alias_id=alias_id, new_name=new_name)
        for passive_link_id in deleted_passive_link_ids:
            yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
        if replacement_alias_info is not None:
            replacement_alias_id, old_alias_name = replacement_alias_info
            alias = await self.db_interface.get_alias(alias_id)
            page_id = alias['page_id']
            yield CreateAliasOutgoingMessage(uuid, message_id, alias_id=replacement_alias_id, page_id=page_id,
                                             alias_name=old_alias_name)

    @handle_interface_errors
    async def delete_alias(self, uuid, message_id, wiki_id, alias_id):
        deleted_link_ids, deleted_passive_link_ids = await self.db_interface.delete_alias(wiki_id, alias_id)
        for link_id in deleted_link_ids:
            yield DeleteLinkOutgoingMessage(uuid, message_id, link_id=link_id)
        for passive_link_id in deleted_passive_link_ids:
            yield DeletePassiveLinkOutgoingMessage(uuid, message_id, passive_link_id=passive_link_id)
        yield DeleteAliasOutgoingMessage(uuid, message_id, alias_id=alias_id)

    ###########################################################################
    #
    # Statistics Methods
    #
    ###########################################################################

    @handle_interface_errors
    async def get_story_statistics(self, uuid, message_id, story_id):
        stats = await self.db_interface.get_story_statistics(story_id)
        yield GetStoryStatisticsOutgoingMessage(uuid, message_id, statistics=stats)

    @handle_interface_errors
    async def get_section_statistics(self, uuid, message_id, section_id):
        stats = await self.db_interface.get_section_statistics_recursive(section_id)
        yield GetSectionStatisticsOutgoingMessage(uuid, message_id, statistics=stats)

    @handle_interface_errors
    async def get_paragraph_statistics(self, uuid, message_id, section_id, paragraph_id):
        stats = await self.db_interface.get_paragraph_statistics(section_id, paragraph_id)
        yield GetParagraphStatisticsOutgoingMessage(uuid, message_id, statistics=stats)

    @handle_interface_errors
    async def get_page_frequencies(self, uuid, message_id, story_id, wiki_id):
        pages = await self.db_interface.get_page_frequencies_in_story(story_id, wiki_id)
        yield GetPageFrequenciesOutgoingMessage(uuid, message_id, pages=pages)
