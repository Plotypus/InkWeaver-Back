from .outgoing_message import UnicastMessage

from uuid import UUID


class LoomErrorOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, action: str, reason: str):
        super().__init__(uuid, message_id, 'error_occurred')
        self.action = action
        self.reason = reason
