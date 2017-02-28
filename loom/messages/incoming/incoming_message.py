from ..message import Message

from abc import ABC, abstractmethod


class IncomingMessage(ABC, Message):
    def set_dispatcher(self, dispatcher):
        self._dispatcher = dispatcher

    @abstractmethod
    def dispatch(self):
        pass
