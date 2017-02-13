from bson import ObjectId


class AddSucceedingSubsection:
    _approved_fields = {
        'message_id': True,   # Required fields
        'title':      True,
        'parent_id':  True,
        'index':      False,  # Optional fields
    }

    def __init__(self, message: dict):
        missing_fields = [field for field, value in self._approved_fields.items()
                          if field not in message and value is not False]
        extra_fields = [field for field in message.keys() if field not in self._approved_fields.keys()]
        if extra_fields:
            raise ValueError(f"Unsupported fields: {extra_fields}")
        if missing_fields:
            raise ValueError(f"Missing fields: {missing_fields}")
        # Initialize optional field
        self._index = None
        # Set the rest of the fields
        for field, value in message.items():
            setattr(self, f'_{field}', value)

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
