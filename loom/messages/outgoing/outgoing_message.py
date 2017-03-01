class OutgoingMessage:
    pass


class UnicastMessage(OutgoingMessage):
    pass


class BroadcastMessage(OutgoingMessage):
    pass


class StoryBroadcastMessage(BroadcastMessage):
    pass


class WikiBroadcastMessage(BroadcastMessage):
    pass


class OutgoingErrorMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, error_message: str):
        self.reply_to_id = reply_to_id
        self.event = 'error_occurred'
        self.error_message = error_message
