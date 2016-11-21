import tornado.websocket

from uuid import uuid4 as generate_uuid

class GenericHandler(tornado.websocket.WebSocketHandler):
    """
    The default Plotypus WebSocket Handler.
    """

    def __init__(self, *args, **kwargs):
        print("INIT")
        self.uuid = generate_uuid()
        super().__init__(*args, **kwargs)

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
        print("{} received: {}".format(self.uuid, message))

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
        return True
