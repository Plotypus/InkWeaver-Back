from .GenericHandler import *

from loom.database.mongodb_clients import LoomMongoDBClient  # For type hinting.

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
    if self.user is None:
        raise LoomWSNoLoginError
    return func(*args, **kwargs)


class LoomHandler(GenericHandler):

    ############################################################
    ##
    ## Generic websocket methods
    ##
    ############################################################

    def open(self):
        # TODO: Check for secure cookies and finish login procedure.
        self.user = None
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
    def db_client(self) -> LoomMongoDBClient:
        return self.settings['db_client']

    @property
    def user_id(self) -> ObjectId:
        pass

    ############################################################
    ##
    ## Message handling
    ##
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
    ##
    ## Protocol implementation
    ##
    ############################################################

    def _get_current_user_access_level_in_object(self, obj):
        for user in obj['users']:
            if user['_id'] == self.user_id:
                return user['access_level']

    ## User Information

    @requires_login
    async def get_user_preferences(self, message_id):
        preferences = await self.db_client.get_user_preferences(self.user_id)
        self.write_json(preferences, with_reply_id=message_id)

    @requires_login
    async def get_user_stories(self, message_id):
        story_ids = await self.db_client.get_user_story_ids(self.user_id)
        stories = await self._get_stories_or_wikis_by_ids(story_ids, 'story')
        message = {'stories': stories}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_user_wikis(self, message_id):
        wiki_ids = await self.db_client.get_user_wiki_ids(self.user_id)
        wikis = await self._get_stories_or_wikis_by_ids(wiki_ids, 'wiki')
        message = {'wikis': wikis}
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_user_stories_and_wikis(self, message_id):
        story_ids = await self.db_client.get_user_story_ids(self.user_id)
        wiki_ids = await self.db_client.get_user_wiki_ids(self.user_id)
        stories = await self._get_stories_or_wikis_by_ids(story_ids, 'story')
        wikis = await self._get_stories_or_wikis_by_ids(wiki_ids, 'wiki')
        message = {
            'stories': stories,
            'wikis': wikis,
        }
        self.write_json(message, with_reply_id=message_id)

    async def _get_stories_or_wikis_by_ids(self, object_ids, object_type):
        objects = []
        for object_id in object_ids:
            if object_type == 'story':
                obj = await self.db_client.get_story(object_id)
            elif object_type == 'wiki':
                obj = await self.db_client.get_wiki(object_id)
            else:
                raise ValueError("invalid object type: {}".format(object_type))
            access_level = self._get_current_user_access_level_in_object(obj)
            objects.append({
                'story_id':     obj['_id'],
                'title':        obj['title'],
                'access_level': access_level,
            })
        return objects

    ## Stories

    @requires_login
    async def create_story(self, message_id, title, wiki_id, summary):
        # TODO: Implement this.
        pass

    @requires_login
    async def add_presection(self, message_id, title, to_parent):
        # TODO: Implement this.
        pass

    @requires_login
    async def add_subsection(self, message_id, title, to_parent):
        # TODO: Implement this.
        pass

    @requires_login
    async def add_postsection(self, message_id, title, to_parent):
        # TODO: Implement this.
        pass

    @requires_login
    async def get_story_information(self, message_id, story_id):
        story = await self.db_client.get_story(story_id)
        message = {
            'story_title':  story['title'],
            'access_level': self._get_current_user_access_level_in_object(story),
            'section_id':   story['section_id'],
            'wiki_id':      story['wiki_id'],
            'users':        story['users'],
            'summary':      story['summary'],
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_section_hierarchy(self, message_id, section_id):
        message = {
            'hierarchy': await self._get_section_hierarchy(section_id)
        }
        self.write_json(message, with_reply_id=message_id)

    async def _get_section_hierarchy(self, section_id):
        section = await self.db_client.get_section(section_id)
        if section is not None:
            hierarchy = {
                'title':      section['title'],
                'section_id': section_id,
                'pre_sections':
                    [await self._get_section_hierarchy(pre_sec_id) for pre_sec_id in section['pre_sections']],
                'sections':
                    [await self._get_section_hierarchy(sec_id) for sec_id in section['sections']],
                'post_sections':
                    [await self._get_section_hierarchy(post_sec_id) for post_sec_id in section['post_sections']],
            }
            return hierarchy
        else:
            raise ValueError("invalid section ID: {}".format(section_id))

    @requires_login
    def get_section_content(self, message_id, section_id):
        # TODO: Implement this.
        pass

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
        wiki = await self.db_client.get_wiki(wiki_id)
        message = {
            'wiki_title':   wiki['title'],
            'access_level': self._get_current_user_access_level_in_object(wiki),
            'segment_id':   wiki['segment_id'],
            'users':        wiki['users'],
            'summary':      wiki['summary',]
        }
        self.write_json(message, with_reply_id=message_id)

    @requires_login
    async def get_wiki_segment_hierarchy(self, message_id, segment_id):
        message = {
            'hierarchy': await self._get_wiki_segment_hierarchy(segment_id)
        }
        self.write_json(message, with_reply_id=message_id)

    async def _get_wiki_segment_hierarchy(self, segment_id):
        segment = await self.db_client.get_segment(segment_id)
        if segment is not None:
            hierarchy = {
                'title':      segment['title'],
                'segment_id': segment_id,
                'segments':   [await self._get_wiki_segment_hierarchy(seg_id) for seg_id in segment['segments']],
                'pages':      [await self._get_wiki_page_for_hierarchy(page_id) for page_id in segment['pages']],
            }
            return hierarchy
        else:
            raise ValueError("invalid segment ID: {}".format(segment_id))

    async def _get_wiki_page_for_hierarchy(self, page_id):
        page = await self.db_client.get_page(page_id)
        return {
            'title':   page['title'],
            'page_id': page_id,
        }

    @requires_login
    def get_wiki_page(self, message_id, page_id):
        # TODO: Implement this.
        pass

    DISPATCH = {
        # User Information
        'get_user_preferences':       get_user_preferences,
        'get_user_stories':           get_user_stories,
        'get_user_wikis':             get_user_wikis,
        'get_user_stories_and_wikis': get_user_stories_and_wikis,

        # Stories
        'get_story_information':      get_story_information,
        'get_section_hierarchy':      get_section_hierarchy,
        'get_section_content':        get_section_content,

        # Wikis
        'get_wiki_information':       get_wiki_information,
        'get_wiki_segment_hierarchy': get_wiki_segment_hierarchy,
        'get_wiki_page':              get_wiki_page,
    }
