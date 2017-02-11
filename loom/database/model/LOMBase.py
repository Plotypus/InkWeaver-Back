class LOMBase:
    def __init__(self, body: dict):
        # Takes in a dictionary assumed to describe this object.
        self._body = body
        # Allows for subclasses to implement special initializations.
        self.initialize()

    def initialize(self):
        pass
