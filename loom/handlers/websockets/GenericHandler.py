from loom import serialize

import tornado.websocket

from uuid import uuid4 as generate_uuid


class GenericHandler(tornado.websocket.WebSocketHandler):
    """
    The default Plotypus WebSocket Handler.
    """
    @classmethod
    def encode_json(cls, data):
        return serialize.to_bson(data)

    @classmethod
    def decode_json(cls, data):
        return serialize.from_bson(data)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uuid = generate_uuid()

    @property
    def uuid(self):
        return self._uuid

    def open(self):
        """
        Accept an incoming WS connection.
        :return:
        """
        print("{} opened".format(self.uuid))

    def on_message(self, message):
        """
        Receive a message from the client.
        :param message:
        :return:
        """
        print("{} received: {}".format(self.uuid, repr(message)))

    def on_close(self):
        """
        Handle WS termination.
        :return:
        """
        print("{} closed".format(self.uuid))

    def check_origin(self, origin):
        """
        Allow all connections.
        :param origin:
        :return:
        """
        # TODO: Make this better. See:
        # http://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketHandler.check_origin
        return True