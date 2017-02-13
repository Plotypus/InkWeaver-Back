from .message import Message

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateStory(Message):
    _required_fields = [
        'message_id',
        'title',
        'wiki_id',
        'summary',
    ]

    @property
    def message_id(self) -> int:
        return self._message_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def wiki_id(self) -> ObjectId:
        return self._wiki_id

    @property
    def summary(self) -> str:
        return self._summary


###########################################################################
#
# Add Messages
#
###########################################################################
class AddPrecedingSubsection(Message):
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


class AddInnerSubsection(Message):
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


class AddParagraph(Message):
    _required_fields = [
        'message_id',
        'section_id'
        'text',
    ]
    _optional_fields = [
        'succeeding_paragraph_id',
    ]

    @property
    def message_id(self) -> int:
        return self._message_id

    @property
    def section_id(self) -> ObjectId:
        return self._section_id

    @property
    def text(self) -> str:
        return self._text

    @property
    def succeeding_paragraph_id(self) -> ObjectId:
        return self._succeeding_paragraph_id
