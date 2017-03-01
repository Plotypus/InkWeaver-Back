from ..message import Message
from .field_types import RequiredField, OptionalField

from loom.dispatchers import AbstractDispatcher

from abc import ABC, abstractmethod

from typing import Iterable


class IncomingMessage(ABC, Message):
    def __init__(self):
        self.uuid = RequiredField()
        self.message_id = RequiredField()

    @property
    def _required_fields(self) -> Iterable[str]:
        return (f for f, fv in vars(self).items() if isinstance(fv, RequiredField))

    @property
    def _optional_fields(self) -> Iterable[str]:
        return (f for f, fv in vars(self).items() if isinstance(fv, OptionalField))

    def set_values_from_message(self, message):
        missing_fields = [field for field, field_type in vars(self).items()
                          if field not in message and isinstance(field_type, RequiredField)]
        extra_fields = [field for field in message if field not in vars(self)]
        if extra_fields:
            raise TypeError(f"Unsupported fields: {extra_fields}")
        if missing_fields:
            raise TypeError(f"Missing fields: {missing_fields}")
        # Initialize optional fields
        for field in self._optional_fields:
            setattr(self, f'{field}', None)
        # Set the rest of the fields
        for field, value in message.items():
            setattr(self, f'{field}', value)

    def set_dispatcher(self, dispatcher: AbstractDispatcher):
        self._dispatcher = dispatcher

    @abstractmethod
    def dispatch(self):
        pass


class SubscriptionIncomingMessage(IncomingMessage):
    def dispatch(self):
        pass
