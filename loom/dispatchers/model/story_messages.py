from .message import Message

from bson import ObjectId


class AddSucceedingSubsection(Message):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]
    _optional_fields = [
        'index',
    ]

    @property
    def message_id(self) -> int:
        return self._message_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def parent_id(self) -> ObjectId:
        return self._parent_id

    @property
    def index(self) -> int:
        return self._index
