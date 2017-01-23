class LoomWSError(Exception):
    def __init__(self, message=None):
        if message is None:
            message = "no information given"
        self.message = message

    def __str__(self):
        return '{}: {}'.format(type(self).__name__, self.message)


class LoomWSUnimplementedError(LoomWSError):
    """
    Raised when a connection attempts an unimplemented task.
    """
    pass


class LoomWSBadArgumentsError(LoomWSError):
    """
    Raised when necessary arguments were omitted or formatted incorrectly.
    """
    pass


class LoomWSNoLoginError(LoomWSError):
    """
    Raised when a user should be logged in but isn't.
    """
    pass
