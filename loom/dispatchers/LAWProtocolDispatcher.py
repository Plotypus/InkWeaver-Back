import loom.serialize

from loom.database.interfaces import AbstractDBInterface

from decorator import decorator
from inspect import signature
from typing import Dict

JSON = Dict

APPROVED_METHODS = [
    # User Information
    'get_user_preferences',
    'get_user_stories',
    'get_user_wikis',
    'set_user_name',
    'set_user_email',
    'set_user_bio',
    'user_login',

    # Stories
    'create_story',
    'add_preceding_subsection',
    'add_inner_subsection',
    'add_succeeding_subsection',
    'add_paragraph',
    'edit_paragraph',
    'get_story_information',
    'get_story_hierarchy',
    'get_section_hierarchy',
    'get_section_content',
    'delete_story',
    'delete_section',
    'delete_paragraph',

    # Wikis
    'create_wiki',
    'add_segment',
    'add_template_heading',
    'add_page',
    'add_heading',
    'edit_segment',
    'edit_template_heading',
    'edit_page',
    'edit_heading',
    'get_wiki_information',
    'get_wiki_hierarchy',
    'get_wiki_segment_hierarchy',
    'get_wiki_segment',
    'get_wiki_page',
    'delete_wiki',
    'delete_segment',
    'delete_template_heading',
    'delete_page',
    'delete_heading',

    # Links
    'create_link',
    'delete_link',

    # Aliases
    'delete_alias',
    'change_alias_name',
]


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
        self.approved = APPROVED_METHODS.copy()

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
        json = self.encode_json(response)
        return json

    async def dispatch(self, message: JSON, action: str, message_id=None):
        if action not in self.approved:
            raise LAWUnimplementedError
        func = getattr(self, action)
        try:
            # `self` is not passed in because `getattr` binds the `self` parameter inside the function call.
            return await func(**message)
        except TypeError:
            # Most likely, the wrong arguments were given.
            # We do some introspection to give back useful error messages.
            sig = signature(func)
            # The first assumption is that not all of the necessary arguments were given, so check for that.
            missing_fields = []
            # print("params: {}".format(signature(func).parameters.values()))
            for param in filter(lambda p: p.kind == p.POSITIONAL_OR_KEYWORD and p.default == p.empty, sig.parameters.values()):
                if param.name not in message:
                    missing_fields.append(param.name)
            if missing_fields:
                # So something *was* missing!
                message = "request of type '{}' missing fields: {}".format(action, missing_fields)
                raise LAWBadArgumentsError(message)
            else:
                # Something else has gone wrong...
                # Let's check if too many arguments were given.
                num_required_arguments = len(sig.parameters)  # Don't subtract 1 for `self` because it's not required.
                num_given_arguments = len(message)
                if num_required_arguments != num_given_arguments:
                    # Yep, they gave the wrong number. Let them know.
                    # We don't check them all because somebody could create a large JSON with an absurd number of
                    # arguments and we'd spend cycles counting them all... easy DOS.
                    raise LAWBadArgumentsError("too many fields given for request of type '{}'".format(action))
                else:
                    # It was something else entirely.
                    raise
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
        return self.format_json(preferences, reply_to_id=message_id)

    @requires_login
    async def get_user_stories(self, message_id):
        stories = await self.db_interface.get_user_stories(self.user_id)
        message = {'stories': stories}
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_user_wikis(self, message_id):
        wikis = await self.db_interface.get_user_wikis(self.user_id)
        message = {'wikis': wikis}
        return self.format_json(message, reply_to_id=message_id)
    
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
            message = {'event': 'logged in'}
        else:
            message = {'event': 'denied'}
        return self.format_json(message, reply_to_id=message_id)

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
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def add_preceding_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_preceding_subsection(title, parent_id, index)
        message = {'section_id': subsection_id}
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def add_inner_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_inner_subsection(title, parent_id, index)
        message = {'section_id': subsection_id}
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def add_succeeding_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_succeeding_subsection(title, parent_id, index)
        message = {'section_id': subsection_id}
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def add_paragraph(self, message_id, section_id, text, index=None):
        # TODO: Decide whether or not to add more to response
        await self.db_interface.add_paragraph(section_id, text, index)
        return self.format_json({}, reply_to_id=message_id)

    @requires_login
    async def edit_paragraph(self, message_id, section_id, update, index):
        # TODO: Decide whether or not to add more to response
        if update['update_type'] == 'replace':
            text = update['text']
            await self.db_interface.set_paragraph_text(section_id, index=index, text=text)
            return self.format_json({}, reply_to_id=message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

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
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_story_hierarchy(self, message_id, story_id):
        message = {
            'hierarchy': await self.db_interface.get_story_hierarchy(story_id)
        }
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_section_hierarchy(self, message_id, section_id):
        message = {
            'hierarchy': await self.db_interface.get_section_hierarchy(section_id)
        }
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_section_content(self, message_id, section_id):
        paragraphs = await self.db_interface.get_section_content(section_id)
        content = [{'text': paragraph['text'], 'paragraph_id': paragraph['_id']} for paragraph in paragraphs]
        return self.format_json({'content': content}, reply_to_id=message_id)

    @requires_login
    async def delete_story(self, message_id, story_id):
        await self.db_interface.delete_story(story_id)

    @requires_login
    async def delete_section(self, message_id, section_id):
        await self.db_interface.delete_section(section_id)

    @requires_login
    async def delete_paragraph(self, message_id, section_id, paragraph_id):
        await self.db_interface.delete_paragraph(section_id, paragraph_id)

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
        return self.format_json(message, reply_to_id=message_id)
        pass

    @requires_login
    async def add_segment(self, message_id, title, parent_id):
        segment_id = await self.db_interface.add_child_segment(title, parent_id)
        return self.format_json({'segment_id': segment_id}, reply_to_id=message_id)

    @requires_login
    async def add_template_heading(self, message_id, title, segment_id):
        await self.db_interface.add_template_heading(title, segment_id)
        # TODO: Decide whether or not to add more to response
        return self.format_json({}, reply_to_id=message_id)

    @requires_login
    async def add_page(self, message_id, title, parent_id):
        page_id = await self.db_interface.create_page(title, parent_id)
        return self.format_json({'page_id': page_id}, reply_to_id=message_id)

    @requires_login
    async def add_heading(self, message_id, title, page_id, index=None):
        await self.db_interface.add_heading(title, page_id, index)
        # TODO: Decide whether or not to add more to response
        return self.format_json({}, reply_to_id=message_id)

    @requires_login
    async def edit_segment(self, message_id, segment_id, update):
        # TODO: Decide whether or not to add more to response
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_segment_title(title, segment_id)
            return self.format_json({}, reply_to_id=message_id)
        else:
            raise LAWUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    @requires_login
    async def edit_template_heading(self, message_id, segment_id, template_heading_title, update):
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_template_heading_title(old_title=template_heading_title, new_title=title,
                                                               segment_id=segment_id)
            return self.format_json({}, reply_to_id=message_id)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_template_heading_text(template_heading_title, text, segment_id)
            return self.format_json({}, reply_to_id=message_id)
        else:
            raise LAWUnimplementedError(f"invalid `update_type`: {update['update_type']}")

    @requires_login
    async def edit_page(self, message_id, page_id, update):
        # TODO: Implement this.
        pass

    @requires_login
    async def edit_heading(self, message_id, page_id, heading_title, update):
        # TODO: Decide whether or not to add more to response
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_heading_title(old_title=heading_title, new_title=title, page_id=page_id)
            return self.format_json({}, reply_to_id=message_id)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_heading_text(heading_title, text, page_id)
            return self.format_json({}, reply_to_id=message_id)
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
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_wiki_hierarchy(self, message_id, wiki_id):
        message = {
            'hierarchy': await self.db_interface.get_wiki_hierarchy(wiki_id)
        }
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_wiki_segment_hierarchy(self, message_id, segment_id):
        message = {
            'hierarchy': await self.db_interface.get_segment_hierarchy(segment_id)
        }
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_wiki_segment(self, message_id, segment_id):
        segment = await self.db_interface.get_segment(segment_id)
        message = {
            'title':             segment['title'],
            'segments':          segment['segments'],
            'pages':             segment['pages'],
            'template_headings': segment['template_headings'],
        }
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def get_wiki_page(self, message_id, page_id):
        page = await self.db_interface.get_page(page_id)
        message = {
            'title':        page['title'],
            'aliases':      page['aliases'],
            'references':   page['references'],
            'headings':     page['headings'],
        }
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def delete_wiki(self, message_id, wiki_id):
        await self.db_interface.delete_wiki(self.user_id, wiki_id)
        
    @requires_login
    async def delete_segment(self, message_id, segment_id):
        await self.db_interface.delete_segment(segment_id)

    @requires_login
    async def delete_template_heading(self, message_id, segment_id, template_heading_title):
        await self.db_interface.delete_template_heading(template_heading_title, segment_id)

    @requires_login
    async def delete_page(self, message_id, page_id):
        await self.db_interface.delete_page(page_id)

    @requires_login
    async def delete_heading(self, message_id, heading_title, page_id):
        await self.db_interface.delete_heading(heading_title, page_id)

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    @requires_login
    async def create_link(self, message_id, story_id, section_id, paragraph_id, name, page_id):
        link_id = await self.db_interface.create_link(story_id, section_id, paragraph_id, name, page_id)
        message = {'link_id': link_id}
        return self.format_json(message, reply_to_id=message_id)

    @requires_login
    async def delete_link(self, message_id, link_id):
        await self.db_interface.delete_link(link_id)

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################


    @requires_login
    async def change_alias_name(self, message_id, alias_id, new_name):
        await self.db_interface.change_alias_name(alias_id, new_name)
        return self.format_json({}, reply_to_id=message_id)

    @requires_login
    async def delete_alias(self, alias_id):
        await self.db_interface.delete_alias(alias_id)
