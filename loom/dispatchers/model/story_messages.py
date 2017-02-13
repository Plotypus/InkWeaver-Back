from bson import ObjectId


class AddSucceedingSubsection:
    _approved_fields = {
        'message_id',
        'title',
        'parent_id',
        'index'
    }

    def __init__(self, message: dict):
        # Needs to check if field is missing, with index being optional
        self._index = None
        for field, value in message.items():
            if field in self._approved_fields:
                setattr(self, f'_{field}', value)
            else:
                raise ValueError(f"Field not supported: {field}")

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
