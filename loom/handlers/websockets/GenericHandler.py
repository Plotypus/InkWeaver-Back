from loom import serialize
from loom.messages.outgoing import OGMEncoder
from loom.loggers import ws_connections

import json
import tornado.websocket

from uuid import uuid4 as generate_uuid


class GenericHandler(tornado.websocket.WebSocketHandler):
    logger = ws_connections

    @classmethod
    def encode_json(cls, data):
        # TODO: Temporary fix, should use in serialize.
        return json.dumps(data, cls=OGMEncoder).replace("</", "<\\/")

    @classmethod
    def decode_json(cls, data):
        return serialize.decode_string_to_bson(data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uuid = generate_uuid()

    @property
    def uuid(self):
        return self._uuid

    def __repr__(self):
        return '<{} {}>'.format(type(self).__name__, self.uuid)

    def write_log(self, message):
        self.logger.info("{} {}".format(repr(self), message))

    def open(self):
        """
        Accept an incoming WS connection.
        :return:
        """
        self.write_log('opened')

    def on_message(self, message):
        """
        Receive a message from the client.
        :param message:
        :return:
        """
        self.write_log('received: {}'.format(message))

    def write_message(self, message, binary=False):
        self.write_log(f'sent response to client: {message}')
        super().write_message(message, binary)

    def on_close(self):
        """
        Handle WS termination.
        :return:
        """
        self.write_log('closed')

    def check_origin(self, origin):
        """
        Allow all connections.
        :param origin:
        :return:
        """
        # TODO: Make this better. See:
        # http://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketHandler.check_origin
        return True