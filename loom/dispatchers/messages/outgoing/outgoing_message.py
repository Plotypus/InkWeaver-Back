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
