class Message:
    _required_fields = []
    _optional_fields = []

    def __init__(self, message: dict):
        missing_fields = [field for field in self._required_fields if field not in message]
        extra_fields = [field for field in message if field not in self.all_fields]
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

    @property
    def all_fields(self):
        return self._required_fields + self._optional_fields