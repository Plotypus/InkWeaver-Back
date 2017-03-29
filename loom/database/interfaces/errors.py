class InterfaceError(Exception):
    def __init__(self, message: str, *, query: str):
        self.message = message
        self.query = query


class BadValueError(InterfaceError):
    def __init__(self, *, query: str, value):
        super().__init__('bad value supplied', query=query)
        self.value = value


class FailedUpdateError(InterfaceError):
    def __init__(self, *, query: str):
        super().__init__('unable to complete update', query=query)
