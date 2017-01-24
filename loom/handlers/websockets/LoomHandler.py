from .GenericHandler import *

from loom.database.interfaces import AbstractDBInterface  # For type hinting.
from loom.dispatchers import *

from bson import ObjectId
from tornado.ioloop import IOLoop
from typing import Dict

JSON = Dict


class LoomHandler(GenericHandler):

    ############################################################
    #
    # Generic websocket methods
    #
    ############################################################

    def open(self):
        # TODO: Remove this.
        super().open()
        session_id = self._get_secure_session_cookie()
        user_id = self._get_user_id_for_session_id(session_id)
        if user_id is None:
            self.on_failure(reason="Something went wrong.")
            # TODO: Clean up session
            self.close()
        self._user_id = user_id
        # By default, small messages are coalesced. This can cause delay. We don't want delay.
        self.set_nodelay(True)
        # Instantiate the dispatcher.
        self._dispatcher = LAWProtocolDispatcher(self.db_interface, self.user_id)

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
    def dispatcher(self) -> LAWProtocolDispatcher:
        return self._dispatcher

    @property
    def db_interface(self) -> AbstractDBInterface:
        try:
            return self._db_interface
        except AttributeError:
            self._db_interface = self.settings['db_interface']
            return self._db_interface

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
        else:
            try:
                json_result = await self.dispatcher.dispatch(message, action, message_id)
                self.write_json(json_result)
            except LAWUnimplementedError:
                err_message = "invalid `action`: {}".format(action)
                self.on_failure(reply_to=message_id, reason=err_message)
            except LAWBadArgumentsError as e:
                self.on_failure(reply_to=message_id, reason=e.message)
