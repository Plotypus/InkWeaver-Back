from.GenericHandler import *

import loom.database

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


class LoomHandler(GenericHandler):
    def open(self):
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

    def write_json(self, data: dict):
        json_string = self.encode_json(data)
        self.write_message(json_string)

    def on_message(self, message):
        # TODO: Remove this.
        super().on_message(message)
        try:
            json = self.decode_json(message)
        except:
            self.on_failure(reason="Message received was not valid JSON.", received_message=message)
            return
        # on_message may not be a coroutine (as of Tornado 4.3).
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
        except KeyError:
            # The method is not implemented.
            raise LoomWSUnimplementedError

    async def get_user_info(self, message_id):
        pass

    async def load_story(self, message_id, story):
        pass

    async def get_chapters(self, message_id):
        pass

    async def load_story_with_chapters(self, message_id, story):
        pass

    async def load_chapter(self, message_id, chapter):
        pass

    async def get_paragraphs(self, message_id):
        pass

    async def load_chapter_with_paragraphs(self, message_id, chapter):
        pass

    async def load_paragraph(self, message_id, paragraph):
        pass

    async def load_paragraph_with_text(self, message_id, paragraph):
        raise LoomWSUnimplementedError

    async def create_story(self, message_id, story):
        pass

    async def create_chapter(self, message_id, title):
        pass

    async def create_end_chapter(self, message_id, title):
        pass

    async def create_paragraph(self, message_id):
        pass

    async def create_end_paragraph(self, message_id):
        pass

    async def update_story(self, message_id, story, changes):
        pass

    async def update_current_story(self, message_id, changes):
        pass

    async def update_chapter(self, message_id, chapter, changes):
        pass

    async def update_current_chapter(self, message_id, changes):
        pass

    async def update_paragraph(self, message_id, paragraph, changes):
        raise LoomWSUnimplementedError

    async def replace_paragraph(self, message_id, text):
        pass

    async def delete_story(self, message_id, story):
        pass

    async def delete_current_story(self, message_id):
        pass

    async def delete_chapter(self, message_id, chapter):
        pass

    async def delete_current_chapter(self, message_id):
        pass

    async def delete_paragraph(self, message_id, paragraph):
        pass

    async def delete_current_paragraph(self, message_id):
        pass

    DISPATCH = {
        'get_user_info': get_user_info,
    }
