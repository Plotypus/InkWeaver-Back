from ..LAWProtocolDispatcher import LAWProtocolDispatcher

from abc import ABC, abstractmethod

class Message(ABC):
    _required_fields = []
    _optional_fields = []

    def __init__(self, dispatcher: LAWProtocolDispatcher, message: dict):
        self._dispatcher = dispatcher
        missing_fields = [field for field in self._required_fields if field not in message]
        extra_fields = [field for field in message if field not in self.all_fields]
        if extra_fields:
            raise ValueError(f"Unsupported fields: {extra_fields}")
        if missing_fields:
            raise ValueError(f"Missing fields: {missing_fields}")
        # Initialize optional fields
        for field in self._optional_fields:
            setattr(self, f'_{field}', None)
        # Set the rest of the fields
        for field, value in message.items():
            setattr(self, f'_{field}', value)

    @property
    def all_fields(self):
        return self._required_fields + self._optional_fields

    @abstractmethod
    def dispatch(self):
        pass
