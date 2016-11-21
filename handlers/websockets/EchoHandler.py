from .GenericHandler import GenericHandler

class EchoHandler(GenericHandler):
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
