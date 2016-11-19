from .WS_GenericHandler import WS_GenericHandler

class WS_EchoHandler(WS_GenericHandler):
    """
    A simple echo WS handler.
    """

    def on_message(self, message):
        """
        Return the message to the client.
        :param message:
        :return:
        """
        super().on_message(message)
        self.write_message(message)
