from .GenericHandler import *

from tornado.ioloop import IOLoop
from tornado.queues import Queue
from typing import Dict

JSON = Dict


class LoomHandler(GenericHandler):

    ############################################################
    #
    # Generic websocket methods
    #
    ############################################################

    def open(self):
        self.ready = False
        super().open()
        self.set_nodelay(True)
        session_id = self._get_secure_session_cookie()
        if session_id is None:
            self.on_failure(reason="No session ID cookie set.")
            self.close()
            return
        user_id = self._get_user_id_for_session_id(session_id)
        if user_id is None:
            self.on_failure(reason="Could not successfully open connection.")
            self.close()
            return
        self._router = self.settings['router']
        self.router.connect(self, user_id)
        self.startup()

    def on_close(self):
        self.router.disconnect(self)
        super().on_close()

    def on_failure(self, reply_to_id=None, reason=None, **fields):
        response = {
            'success': False,
            'reason':  reason,
        }
        if reply_to_id is not None:
            response['reply_to_id'] = reply_to_id
        response.update(fields)
        json_response = self.encode_json(response)
        self.write_message(json_response)

    def write_json(self, data):
        json_string = self.encode_json(data)
        self.write_message(json_string)

    def initialize_queue(self):
        self._messages = Queue()
        IOLoop.current().spawn_callback(self.process_messages)

    def startup(self):
        self.initialize_queue()
        self.ready = True
        self.send_ready_acknowledgement()

    @property
    def messages(self) -> Queue:
        return self._messages

    @property
    def router(self):
        return self._router

    def _get_user_id_for_session_id(self, session_id):
        session_manager = self.settings['session_manager']
        user_id = session_manager.get_user_id_for_session_id(session_id)
        if user_id is None:
            raise ValueError("Session ID is not valid")
        return user_id

    def _get_secure_session_cookie(self):
        cookie_name = self.settings['session_cookie_name']
        # Make sure users cannot use cookies for more than their session
        cookie = self.get_secure_cookie(cookie_name, max_age_days=0.5)
        # Cookies are retrieved as a byte-string, we need to decode it.
        if cookie is not None:
            decoded_cookie = cookie.decode('UTF-8')
        else:
            decoded_cookie = None
        return decoded_cookie

    ############################################################
    #
    # Message handling
    #
    ############################################################

    def on_message(self, message):
        super().on_message(message)
        # noinspection PyBroadException
        try:
            json_message = self.decode_json(message)
        except Exception:
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
        IOLoop.current().spawn_callback(self.handle_message, json_message)

    def send_ready_acknowledgement(self):
        message = {
            'event': 'acknowledged',
            'uuid':  self.uuid,
        }
        self.write_json(message)

    async def handle_message(self, message: JSON):
        if self.ready:
            await self.messages.put(message)
        else:
            self.write_log("Dropping message: {}".format(message))

    async def process_messages(self):
        async for message in self.messages:
            try:
                identifier = message.pop('identifier')
                action = message.pop('action')
            except KeyError:
                self.on_failure(reason="malformed message; all messages require `action` and `identifier` fields")
            else:
                try:
                    uuid = identifier.get('uuid')
                    message_id = identifier.get('message_id')
                    # TODO: Check this and send a specific error.
                    assert uuid == self.encode_json(self.uuid)
                except KeyError:
                    self.on_failure(reason="malformed identifier; must have both given `uuid` and `message_id` fields")
                else:
                    # Spawn a callback to handle the message, freeing this handler immediately.
                    IOLoop.current().spawn_callback(self.router.process_incoming, self, message, action, uuid,
                                                    message_id)
            finally:
                self.messages.task_done()
