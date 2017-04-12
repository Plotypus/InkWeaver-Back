from uuid import UUID


class OutgoingMessage:
    class Identifier:
        def __init__(self, uuid: UUID, message_id: int):
            self.uuid = uuid
            self.message_id = message_id

    def __init__(self, uuid: UUID, message_id: int, event: str):
        self.identifier = OutgoingMessage.Identifier(uuid, message_id)
        self.event = event


class UnicastMessage(OutgoingMessage):
    pass


class MulticastMessage(OutgoingMessage):
    pass


class BroadcastMessage(OutgoingMessage):
    pass


class DualBroadcastMessage(BroadcastMessage):
    pass


class StoryBroadcastMessage(BroadcastMessage):
    pass


class WikiBroadcastMessage(BroadcastMessage):
    pass


class OutgoingErrorMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, error_message: str):
        super().__init__(uuid, message_id, 'error_occurred')
        self.error_message = error_message
