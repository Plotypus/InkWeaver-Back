from loom.handlers.websockets.errors import *

import loom.serialize

from loom.database.interfaces import AbstractDBInterface

from inspect import signature
from typing import Dict

JSON = Dict

APPROVED_METHODS = [
    # User Information
    'get_user_preferences',
    'get_user_stories',
    'get_user_wikis',

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

    # Wikis
    'create_wiki',
    'add_segment',
    'add_template_heading',
    'add_page',
    'add_heading',
    'edit_segment',
    'edit_page',
    'edit_heading',
    'get_wiki_information',
    'get_wiki_hierarchy',
    'get_wiki_segment_hierarchy',
    'get_wiki_page',
]


class LAWProtocolDispatcher:
    def __init__(self, interface: AbstractDBInterface, user_id=None):
        self._db_interface = interface
        self._user_id = user_id
        self.approved = APPROVED_METHODS.copy()

    @classmethod
    def encode_json(cls, data):
        return loom.serialize.decode_bson_to_string(data)

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

    def format_failure_json(self, reply_to=None, reason=None, **fields):
        response = {
            'success': False,
            'reason':  reason,
        }
        if reply_to is not None:
            response['reply_to'] = reply_to
        response.update(fields)
        json = self.encode_json(response)
        return json

    async def dispatch(self, message: JSON, action: str, message_id=None):
        if action not in self.approved:
            raise LoomWSUnimplementedError
        func = getattr(self, action)
        try:
            return await func(self, **message)
        except TypeError:
            # Most likely, the wrong arguments were given.
            # We do some introspection to give back useful error messages.
            sig = signature(func)
            # The first assumption is that not all of the necessary arguments were given, so check for that.
            missing_fields = []
            print("params: {}".format(signature(func).parameters.values()))
            for param in filter(lambda p: p.name != 'self' and p.kind == p.POSITIONAL_OR_KEYWORD and p.default == p.empty, sig.parameters.values()):
                if param.name not in message:
                    missing_fields.append(param.name)
            if missing_fields:
                # So something *was* missing!
                message = "request of type '{}' missing fields: {}".format(action, missing_fields)
                raise LoomWSBadArgumentsError(message)
            else:
                # Something else has gone wrong...
                # Let's check if too many arguments were given.
                num_required_arguments = len(sig.parameters) - 1  # We subtract 1 for `self`.
                num_given_arguments = len(message)
                if num_required_arguments != num_given_arguments:
                    # Yep, they gave the wrong number. Let them know.
                    # We don't check them all because somebody could create a large JSON with an absurd number of
                    # arguments and we'd spend cycles counting them all... easy DOS.
                    raise LoomWSBadArgumentsError("too many fields given for request of type '{}'".format(action))
                else:
                    # It was something else entirely.
                    raise
        except LoomWSNoLoginError:
            return self.format_failure_json(message_id, "not logged in")
        except LoomWSError as e:
            return self.format_failure_json(message_id, str(e))
        except Exception as e:
            # General exceptions store messages as the first argument in their `.args` property.
            message = type(e).__name__
            if e.args:
                message += ": {}".format(e.args[0])
            return self.format_failure_json(message_id, message)


    ############################################################
    #
    # Protocol implementation
    #
    ############################################################

    ## User Information

    async def get_user_preferences(self, message_id):
        preferences = await self.db_interface.get_user_preferences(self.user_id)
        return self.format_json(preferences, with_reply_id=message_id)

    async def get_user_stories(self, message_id):
        stories = await self.db_interface.get_user_stories(self.user_id)
        message = {'stories': stories}
        return self.format_json(message, with_reply_id=message_id)

    async def get_user_wikis(self, message_id):
        wikis = await self.db_interface.get_user_wikis(self.user_id)
        message = {'wikis': wikis}
        return self.format_json(message, with_reply_id=message_id)

    ## Stories

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
        return self.format_json(message, with_reply_id=message_id)

    async def add_preceding_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_preceding_subsection(title, parent_id, index)
        message = {'section_id': subsection_id}
        return self.format_json(message, with_reply_id=message_id)

    async def add_inner_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_inner_subsection(title, parent_id, index)
        message = {'section_id': subsection_id}
        return self.format_json(message, with_reply_id=message_id)

    async def add_succeeding_subsection(self, message_id, title, parent_id, index=None):
        subsection_id = await self.db_interface.add_succeeding_subsection(title, parent_id, index)
        message = {'section_id': subsection_id}
        return self.format_json(message, with_reply_id=message_id)

    async def add_paragraph(self, message_id, section_id, text, index=None):
        # TODO: Decide whether or not to add more to response
        await self.db_interface.add_paragraph(section_id, text, index)
        return self.format_json({}, with_reply_id=message_id)

    async def edit_paragraph(self, message_id, section_id, update, index):
        # TODO: Decide whether or not to add more to response
        if update['update_type'] == 'replace':
            text = update['text']
            await self.db_interface.set_paragraph_text(section_id, index=index, text=text)
            return self.format_json({}, with_reply_id=message_id)
        else:
            raise LoomWSUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    async def get_story_information(self, message_id, story_id):
        story = await self.db_interface.get_story(story_id)
        message = {
            'story_title':  story['title'],
            'section_id':   story['section_id'],
            'wiki_id':      story['wiki_id'],
            'users':        story['users'],
            'summary':      story['summary'],
        }
        return self.format_json(message, with_reply_id=message_id)

    async def get_story_hierarchy(self, message_id, story_id):
        message = {
            'hierarchy': await self.db_interface.get_story_hierarchy(story_id)
        }
        return self.format_json(message, with_reply_id=message_id)

    async def get_section_hierarchy(self, message_id, section_id):
        message = {
            'hierarchy': await self.db_interface.get_section_hierarchy(section_id)
        }
        return self.format_json(message, with_reply_id=message_id)

    async def get_section_content(self, message_id, section_id):
        paragraphs = await self.db_interface.get_section_content(section_id)
        content = [{'text': paragraph['text']} for paragraph in paragraphs]
        return self.format_json({'content': content}, with_reply_id=message_id)

    ## Wikis

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
        return self.format_json(message, with_reply_id=message_id)
        pass

    async def add_segment(self, message_id, title, parent_id):
        segment_id = await self.db_interface.add_child_segment(title, parent_id)
        return self.format_json({'segment_id': segment_id}, with_reply_id=message_id)

    async def add_template_heading(self, message_id, title, segment_id):
        await self.db_interface.add_template_heading(title, segment_id)
        # TODO: Decide whether or not to add more to response
        return self.format_json({}, with_reply_id=message_id)

    async def add_page(self, message_id, title, parent_id):
        page_id = await self.db_interface.create_page(title, parent_id)
        return self.format_json({'page_id': page_id}, with_reply_id=message_id)

    async def add_heading(self, message_id, title, page_id, index=None):
        await self.db_interface.add_heading(title, page_id, index)
        # TODO: Decide whether or not to add more to response
        return self.format_json({}, with_reply_id=message_id)

    async def edit_segment(self, message_id, segment_id, update):
        # TODO: Decide whether or not to add more to response
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_segment_title(title, segment_id)
            return self.format_json({}, with_reply_id=message_id)
        else:
            raise LoomWSUnimplementedError("invalid `update_type`: {}".format(update['update_type']))

    async def edit_page(self, message_id, page_id, update):
        # TODO: Implement this.
        pass

    async def edit_heading(self, message_id, page_id, heading_title, update):
        # TODO: Decide whether or not to add more to response
        if update['update_type'] == 'set_title':
            title = update['title']
            await self.db_interface.set_heading_title(old_title=heading_title, new_title=title, page_id=page_id)
            return self.format_json({}, with_reply_id=message_id)
        elif update['update_type'] == 'set_text':
            text = update['text']
            await self.db_interface.set_heading_text(heading_title, text, page_id)
            return self.format_json({}, with_reply_id=message_id)
        else:
            raise LoomWSUnimplementedError("invalid `update_type`: {}".format(update('update_type')))

    async def get_wiki_information(self, message_id, wiki_id):
        wiki = await self.db_interface.get_wiki(wiki_id)
        message = {
            'wiki_title':   wiki['title'],
            'segment_id':   wiki['segment_id'],
            'users':        wiki['users'],
            'summary':      wiki['summary'],
        }
        return self.format_json(message, with_reply_id=message_id)

    async def get_wiki_hierarchy(self, message_id, wiki_id):
        message = {
            'hierarchy': await self.db_interface.get_wiki_hierarchy(wiki_id)
        }
        return self.format_json(message, with_reply_id=message_id)

    async def get_wiki_segment_hierarchy(self, message_id, segment_id):
        message = {
            'hierarchy': await self.db_interface.get_segment_hierarchy(segment_id)
        }
        return self.format_json(message, with_reply_id=message_id)

    async def get_wiki_page(self, message_id, page_id):
        page = await self.db_interface.get_page(page_id)
        message = {
            'title':        page['title'],
            'aliases':      list(),  # TODO: Change when aliases are implemented.
            'references':   list(),  # TODO: Change when references are implemented.
            'headings':     page['headings'],
        }
        return self.format_json(message, with_reply_id=message_id)
