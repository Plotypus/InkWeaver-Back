from .GenericHandler import *

from tornado.ioloop import IOLoop
from typing import Dict
from uuid import UUID

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

    def startup(self):
        self.ready = True
        self.send_ready_acknowledgement()

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
        if not self.ready:
            self.write_log("Dropping message: {}".format(message))
            return
        # noinspection PyBroadException
        try:
            json_message = self.decode_json(message)
        except Exception:
            self.on_failure(reason="Message received was not valid JSON.", received_message=message)
            return
        self.route_message(json_message)

    def send_ready_acknowledgement(self):
        message = {
            'event': 'acknowledged',
            'uuid':  self.uuid,
        }
        self.write_json(message)

    def route_message(self, message):
        try:
            identifier = message.pop('identifier')
            action = message.pop('action')
        except KeyError:
            self.on_failure(reason="malformed message; all messages require `action` and `identifier` fields")
        else:
            try:
                uuid = UUID(identifier.get('uuid'))
                message_id = identifier.get('message_id')
                # TODO: Check this and send a specific error.
                assert uuid == self.uuid
            except KeyError:
                self.on_failure(reason="malformed identifier; must have both given `uuid` and `message_id` fields")
            except AssertionError:
                self.write_log(f"given UUID {uuid} does not equal correct UUID {self.uuid}")
            else:
                # Update the message.
                message['uuid'] = uuid
                message['message_id'] = message_id
                # Spawn a callback to handle the message, freeing this handler immediately.
                IOLoop.current().spawn_callback(self.router.enqueue_message, self, message, action, uuid, message_id)
