from .GenericHandler import *

from loom.database.interfaces import AbstractDBInterface  # For type hinting.

from bson import ObjectId
from decorator import decorator
from inspect import signature
from tornado.ioloop import IOLoop
from typing import Dict

JSON = Dict


class LoomWSError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return '{}: {}'.format(type(self), self.message)


class LoomWSUnimplementedError(LoomWSError):
    """
    Raised when a connection attempts an unimplemented task.
    """
    pass


class LoomWSBadArgumentsError(LoomWSError):
    """
    Raised when necessary arguments were omitted or formatted incorrectly.
    """
    pass


class LoomWSNoLoginError(LoomWSError):
    """
    Raised when a user should be logged in but isn't.
    """
    pass


############################################################
##
## LoomHandler decorators
##
############################################################


@decorator
def requires_login(func, *args, **kwargs):
    self = args[0]
    if self.user_id is None:
        raise LoomWSNoLoginError
    return func(*args, **kwargs)


class LoomHandler(GenericHandler):

    ############################################################
    #
    # Generic websocket methods
    #
    ############################################################

    def open(self):
        session_id = self._get_secure_session_cookie()
        user_id = self._get_user_id_for_session_id(session_id)
        if user_id is None:
            self.on_failure(reason="Something went wrong.")
            # TODO: Clean up session
            self.close()
        self._user_id = user_id
        super().open()
        # By default, small messages are coalesced. This can cause delay. We don't want delay.
        self.set_nodelay(True)

    def on_failure(self, reply_to=None, reason=None, **fields):
        response = {
            'success': False,
            'reason':  reason,
        }
        if reply_to is not None:
            response['reply_to'] = reply_to
        response.update(fields)
        json = self.encode_json(response)
        self.write_message(json)

    def write_json(self, data: Dict, with_reply_id=None):
        if with_reply_id is not None:
            data.update({'reply_to_id': with_reply_id})
        json_string = self.encode_json(data)
        self.write_message(json_string)

    @property
    def db_interface(self) -> AbstractDBInterface:
        return self.settings['db_interface']

    @property
    def user_id(self) -> ObjectId:
        return self._user_id

    def _get_user_id_for_session_id(self, session_id):
        session_manager = self.settings['session_manager']
        user_id = session_manager.get_user_id_for_session_id(session_id)
        if user_id is None:
            raise ValueError("Session id is not valid")
        return user_id

    def _get_secure_session_cookie(self):
        cookie_name = self.settings['session_cookie_name']
        # Make sure users cannot use cookies for more than their session
        cookie = self.get_secure_cookie(cookie_name, max_age_days=0)  # Might need to be set to 1?
        return cookie

    ############################################################
    #
    # Message handling
    #
    ############################################################

    def on_message(self, message):
        # TODO: Remove this.
        super().on_message(message)
        try:
            json = self.decode_json(message)
        except:
            self.on_failure(reason="Message received was not valid JSON.", received_message=message)
            return
        # `on_message` may not be a coroutine (as of Tornado 4.3).
        # To work around this, we call spawn_callback to start a coroutine.
        # However, this results in errors not propagating back up.
        # Side effect: More messages may be received before the one below is fully executed.
        # See:
        #   https://stackoverflow.com/questions/35542864/how-to-use-python-3-5-style-async-and-await-in-tornado-for-websockets
        # And:
        #   http://stackoverflow.com/questions/33723830/exception-ignored-in-tornado-websocket-on-message-method
        IOLoop.current().spawn_callback(self.handle_message, json)

    async def handle_message(self, message: JSON):
        message_id = message.get('message_id', None)
        try:
            # Remove the `action` key/value. It's only needed for dispatch, so the dispatch methods don't use it.
            action = message.pop('action')
        except KeyError:
            self.on_failure(reply_to=message_id, reason="`action` field not supplied")
            return
        try:
            await self.dispatch(message, action, message_id)
        except LoomWSUnimplementedError:
            err_message = "invalid `action`: {}".format(action)
            self.on_failure(reply_to=message_id, reason=err_message)
        except LoomWSBadArgumentsError as e:
            self.on_failure(reply_to=message_id, reason=e.message)

    async def dispatch(self, message: JSON, action: str, message_id=None):
        try:
            func = self.DISPATCH[action]
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
                self.on_failure(message_id, "not logged in")
        except KeyError:
            # The method is not implemented.
            raise LoomWSUnimplementedError

    ############################################################
    #
    # Protocol implementation
    #
    ############################################################

    ## User Information

    @requires_login
    async def get_user_preferences(self, message_id):
        preferences = await self.db_interface.get_user_preferences(self.user_id)
        self.write_json(preferences, with_reply_id=message_id)

    @requires_login
    async def get_user_stories(self, message_id):
        stories = await self.db_interface.get_user_stories(self.user_id)
        message = {'stories': stories}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_user_wikis(self, message_id):
        wikis = await self.db_interface.get_user_wikis(self.user_id)
        message = {'wikis': wikis}
        self.write_json(message, with_reply_id=message_id)

    ## Stories

    @requires_login
    async def create_story(self, message_id, title, wiki_id, summary):
        story_id = await self.db_interface.create_story(self.user_id, title, summary, wiki_id)
        story = await self.db_interface.get_story(story_id)
        message = {
            'story_title':  story['title'],
            'section_id':   story['section_id'],
            'wiki_id':      story['wiki_id'],
            'users':        story['users'],
            'summary':      story['summary'],
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def add_preceding_subsection_at_index(self, message_id, title, to_parent, index):
        subsection_id = await self.db_interface.insert_preceding_subsection(title, to_parent, index)
        message = {'section_id': subsection_id}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def append_preceding_subsection(self, message_id, title, to_parent):
        subsection_id = await self.db_interface.append_preceding_subsection(title, to_parent)
        message = {'section_id': subsection_id}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def add_inner_subsection_at_index(self, message_id, title, to_parent, index):
        subsection_id = await self.db_interface.insert_inner_subsection(title, to_parent, index)
        message = {'section_id': subsection_id}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def append_inner_subsection(self, message_id, title, to_parent):
        subsection_id = await self.db_interface.append_inner_subsection(title, to_parent)
        message = {'section_id': subsection_id}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def add_succeeding_subsection_at_index(self, message_id, title, to_parent, index):
        subsection_id = await self.db_interface.insert_succeeding_subsection(title, to_parent, index)
        message = {'section_id': subsection_id}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def append_succeeding_subsection(self, message_id, title, to_parent):
        subsection_id = await self.db_interface.append_succeeding_subsection(title, to_parent)
        message = {'section_id': subsection_id}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def add_paragraph_at_index_in_section(self, message_id, section_id, index, text):
        # TODO: Decide whether or not to add more to response
        await self.db_interface.insert_paragraph_into_section_at_index(section_id, index, text)
        self.write_json({}, with_reply_id=message_id)


    @requires_login
    async def append_paragraph_in_section(self, message_id, section_id, text):
        # TODO: Decide whether or not to add more to response
        await self.db_interface.append_paragraph_to_section(section_id, text)
        self.write_json({}, with_reply_id=message_id)

    @requires_login
    async def edit_paragraph_in_section(self, message_id, section_id, paragraph, update):
        # TODO: Implement this.
        pass

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
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_story_hierarchy(self, message_id, story_id):
        message = {
            'hierarchy': await self.db_interface.get_story_hierarchy(story_id)
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_section_hierarchy(self, message_id, section_id):
        message = {
            'hierarchy': await self.db_interface.get_section_hierarchy(section_id)
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_section_content(self, message_id, section_id):
        paragraphs = await self.db_interface.get_section_content(section_id)
        content = [{'text': paragraph['text']} for paragraph in paragraphs]
        self.write_json({'content': content}, with_reply_id=message_id)

    ## Wikis

    @requires_login
    async def create_wiki(self, message_id, title, summary):
        # TODO: Implement this.
        pass

    @requires_login
    async def add_segment(self, message_id, title, to_parent):
        # TODO: Implement this.
        pass

    @requires_login
    async def add_page(self, message_id, title, to_parent):
        # TODO: Implement this.
        pass

    @requires_login
    async def get_wiki_information(self, message_id, wiki_id):
        wiki = await self.db_interface.get_wiki(wiki_id)
        message = {
            'wiki_title':   wiki['title'],
            'segment_id':   wiki['segment_id'],
            'users':        wiki['users'],
            'summary':      wiki['summary'],
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_wiki_hierarchy(self, message_id, wiki_id):
        message = {
            'hierarchy': await self.db_interface.get_wiki_hierarchy(wiki_id)
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_wiki_segment_hierarchy(self, message_id, segment_id):
        message = {
            'hierarchy': await self.db_interface.get_segment_hierarchy(segment_id)
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    def get_wiki_page(self, message_id, page_id):
        # TODO: Implement this.
        pass

    DISPATCH = {
        # User Information
        'get_user_preferences':               get_user_preferences,
        'get_user_stories':                   get_user_stories,
        'get_user_wikis':                     get_user_wikis,

        # Stories
        'create_story':                       create_story,
        'add_preceding_subsection_at_index':  add_preceding_subsection_at_index,
        'append_preceding_subsection':        append_preceding_subsection,
        'add_inner_subsection_at_index':      add_inner_subsection_at_index,
        'append_inner_subsection':            append_inner_subsection,
        'add_succeeding_subsection_at_index': add_succeeding_subsection_at_index,
        'append_succeeding_subsection':       append_succeeding_subsection,
        'add_paragraph_at_index_in_section':  add_paragraph_at_index_in_section,
        'append_paragraph_in_section':        append_paragraph_in_section,
        'edit_paragraph_in_section':          edit_paragraph_in_section,
        'get_story_information':              get_story_information,
        'get_story_hierarchy':                get_story_hierarchy,
        'get_section_hierarchy':              get_section_hierarchy,
        'get_section_content':                get_section_content,

        # Wikis
        'create_wiki':                        create_wiki,
        'add_segment':                        add_segment,
        'add_page':                           add_page,
        'get_wiki_information':               get_wiki_information,
        'get_wiki_hierarchy':                 get_wiki_hierarchy,
        'get_wiki_segment_hierarchy':         get_wiki_segment_hierarchy,
        'get_wiki_page':                      get_wiki_page,
    }
